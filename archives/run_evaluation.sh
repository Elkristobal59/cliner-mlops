#!/usr/bin/env bash
#
# run_evaluation.sh
#
# End-to-end pipeline: remap your tool's full-protocol entity offsets into
# Chia's gold-snippet coordinate system, then score them against Chia's
# gold .ann files using brateval.
#
# Usage:
#   ./run_evaluation.sh
#
# Edit the CONFIG section below to point at your actual paths, then run.
# Re-running is safe: brateval will be built once and skipped on subsequent
# runs unless you delete the brateval/ directory.

set -euo pipefail

# ============================================================================
# CONFIG -- edit these paths for your setup
# ============================================================================

# Directory with the full clinical protocol .txt files your tool ran on
FULL_TXT_DIR="protocols/"

# Directory with your tool's system .ann files (offsets in FULL protocol space)
FULL_ANN_DIR="system_out/"

# Directory with Chia's gold snippet .txt files (e.g. NCT01234567Inclusion.txt)
GOLD_TXT_DIR="chia/txt/"

# Directory with Chia's gold .ann files (must have same filenames as GOLD_TXT_DIR)
GOLD_ANN_DIR="chia/ann/"

# Where to write the remapped system .ann files
REMAPPED_DIR="remapped_system/"

# Where to write the brateval-ready folder pair
EVAL_ROOT="brateval_input/"
EVAL_SYSTEM_DIR="${EVAL_ROOT}system/"
EVAL_GOLD_DIR="${EVAL_ROOT}groundtruth/"

# Where to write the per-document alignment report
ALIGNMENT_REPORT="alignment_report.csv"

# Path to the offset-remapping script
REMAP_SCRIPT="remap_offsets.py"

# brateval source/build location
BRATEVAL_DIR="brateval"
BRATEVAL_REPO="https://github.com/READ-BioMed/brateval.git"

# Span matching mode for brateval: exact | overlap | "approx 0.8"
SPAN_MATCH_MODE="exact"

# ============================================================================
# 1. Sanity-check inputs
# ============================================================================

echo "== Step 1/5: checking inputs =="

for d in "$FULL_TXT_DIR" "$FULL_ANN_DIR" "$GOLD_TXT_DIR" "$GOLD_ANN_DIR"; do
    if [ ! -d "$d" ]; then
        echo "ERROR: directory not found: $d" >&2
        exit 1
    fi
done

if [ ! -f "$REMAP_SCRIPT" ]; then
    echo "ERROR: remap script not found: $REMAP_SCRIPT" >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found on PATH" >&2
    exit 1
fi

if ! command -v java >/dev/null 2>&1; then
    echo "ERROR: java not found on PATH (required to run brateval)" >&2
    exit 1
fi

# ============================================================================
# 2. Remap system offsets from full-protocol space to gold-snippet space
# ============================================================================

echo "== Step 2/5: remapping entity offsets =="

mkdir -p "$REMAPPED_DIR"

python3 "$REMAP_SCRIPT" --batch \
    --full-txt-dir "$FULL_TXT_DIR" \
    --full-ann-dir "$FULL_ANN_DIR" \
    --gold-txt-dir "$GOLD_TXT_DIR" \
    --out-dir "$REMAPPED_DIR" \
    --report-csv "$ALIGNMENT_REPORT"

echo "Alignment report written to: $ALIGNMENT_REPORT"
echo "(Check match_ratio / dropped_boundary_straddle before trusting scores below.)"

# ============================================================================
# 3. Build the brateval-ready folder pair
#    (system/ = remapped output, groundtruth/ = Chia's original gold files)
# ============================================================================

echo "== Step 3/5: assembling brateval input folders =="

rm -rf "$EVAL_ROOT"
mkdir -p "$EVAL_SYSTEM_DIR" "$EVAL_GOLD_DIR"

# system side: remapped .ann + their paired .txt (already written by the
# remap script into REMAPPED_DIR)
cp "$REMAPPED_DIR"*.ann "$EVAL_SYSTEM_DIR" 2>/dev/null || true
cp "$REMAPPED_DIR"*.txt "$EVAL_SYSTEM_DIR" 2>/dev/null || true

# gold side: Chia's original .ann + .txt, restricted to documents that were
# actually remapped (so brateval only scores on the matched intersection)
for ann_file in "$EVAL_SYSTEM_DIR"*.ann; do
    base="$(basename "$ann_file")"
    stem="${base%.ann}"
    if [ -f "${GOLD_ANN_DIR}${base}" ]; then
        cp "${GOLD_ANN_DIR}${base}" "$EVAL_GOLD_DIR"
    else
        echo "WARNING: no gold .ann found for $base, skipping" >&2
    fi
    if [ -f "${GOLD_TXT_DIR}${stem}.txt" ]; then
        cp "${GOLD_TXT_DIR}${stem}.txt" "$EVAL_GOLD_DIR"
    fi
done

n_system=$(find "$EVAL_SYSTEM_DIR" -name '*.ann' | wc -l | tr -d ' ')
n_gold=$(find "$EVAL_GOLD_DIR" -name '*.ann' | wc -l | tr -d ' ')
echo "System .ann files: $n_system   Gold .ann files: $n_gold"

if [ "$n_system" -eq 0 ] || [ "$n_gold" -eq 0 ]; then
    echo "ERROR: nothing to evaluate (empty system or gold folder)." >&2
    exit 1
fi

# ============================================================================
# 4. Build brateval if not already built
# ============================================================================

echo "== Step 4/5: preparing brateval =="

if ! command -v mvn >/dev/null 2>&1; then
    echo "ERROR: maven (mvn) not found on PATH (required to build brateval)" >&2
    exit 1
fi

if [ ! -d "$BRATEVAL_DIR" ]; then
    git clone "$BRATEVAL_REPO" "$BRATEVAL_DIR"
fi

BRATEVAL_JAR="$(find "$BRATEVAL_DIR/target" -name 'BRATEval-*.jar' 2>/dev/null | head -n1 || true)"

if [ -z "$BRATEVAL_JAR" ]; then
    echo "Building brateval with maven (first run only)..."
    (cd "$BRATEVAL_DIR" && mvn -q package)
    BRATEVAL_JAR="$(find "$BRATEVAL_DIR/target" -name 'BRATEval-*.jar' | head -n1)"
fi

if [ -z "$BRATEVAL_JAR" ]; then
    echo "ERROR: brateval jar not found after build. Check the maven build log." >&2
    exit 1
fi

echo "Using brateval jar: $BRATEVAL_JAR"

# ============================================================================
# 5. Run brateval entity comparison
# ============================================================================

echo "== Step 5/5: running brateval =="
echo "Span match mode: $SPAN_MATCH_MODE"
echo ""

if [ "$SPAN_MATCH_MODE" = "exact" ]; then
    java -cp "$BRATEVAL_JAR" au.com.nicta.csp.brateval.CompareEntities \
        "$EVAL_SYSTEM_DIR" "$EVAL_GOLD_DIR"
else
    java -cp "$BRATEVAL_JAR" au.com.nicta.csp.brateval.CompareEntities \
        "$EVAL_SYSTEM_DIR" "$EVAL_GOLD_DIR" -s $SPAN_MATCH_MODE
fi

echo ""
echo "Done. Remember to also check $ALIGNMENT_REPORT for documents with low"
echo "match_ratio or high dropped_boundary_straddle counts -- those inflate"
echo "false negatives for reasons unrelated to your tool's extraction quality."
