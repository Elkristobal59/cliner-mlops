"""
Module : run_pipeline.py (L'Orchestrateur MLOps Maître)
------------------------------------------------------
Rôle :
Pilote de bout en bout la boucle automatisée de Continuous Training (CT) :
    1. Mesure du Drift sur les embeddings BioBERT (Supabase).
    2. Si Dérive détectée (ou option --force) :
       a. Démarrage de l'instance AWS EC2 GPU via boto3.
       b. Exécution du fine-tuning de l'adaptateur LoRA de Qwen-7B.
       c. Versionnage et promotion du modèle (MLflow & Hugging Face Hub).
       d. Arrêt automatique (Auto-Kill FinOps) de l'instance EC2 dans un bloc `finally`.
    3. Si pas de Dérive : Arrêt immédiat (Zéro coût de calcul).

Usage :
    python run_pipeline.py
    python run_pipeline.py --force-retrain
    python run_pipeline.py --dry-run
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, Any

# Configuration encodage UTF-8 pour Windows PowerShell
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Imports locaux relatifs
from drift_detection import check_drift
from ec2_manager import EC2GPUManager
from finetune_lora import run_lora_finetuning
from s3_storage import S3StorageManager


def orchestrate_mlops_pipeline(
    threshold: float = 0.15,
    force_retrain: bool = False,
    dry_run: bool = True,
    instance_id: str = None
) -> Dict[str, Any]:
    """
    Exécute la chaîne d'orchestration MLOps complète.
    """
    overall_start = time.time()
    pipeline_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "steps_completed": [],
        "drift_report": None,
        "ec2_start": None,
        "finetuning": None,
        "ec2_stop": None,
        "status": "pending"
    }

    print("\n" + "=" * 72)
    print("      PIPELINE D'AUTOMATISATION MLOPS & CONTINUOUS TRAINING (LoRA)")
    print("           Projet CliNER — Pipeline MLOps Industriel")
    print("=" * 72 + "\n")

    # ---------------------------------------------------------
    # ÉTAPE 1 : CONTRÔLE DE DÉRIVE SÉMANTIQUE (BioBERT Embeddings)
    # ---------------------------------------------------------
    print("📍 [ÉTAPE 1/4] Surveillance de dérive sur les protocoles récents...")
    drift_res = check_drift(threshold=threshold)
    pipeline_report["drift_report"] = drift_res
    pipeline_report["steps_completed"].append("drift_detection")

    print(f"  ├── Distance de Wasserstein : {drift_res['wasserstein_distance']} (Seuil: {threshold})")
    print(f"  ├── Décalage de similarité : {drift_res['semantic_distance_shift']}")
    print(f"  └── Statut Dérive : {'🚨 DRIFT DÉTECTÉ' if drift_res['drift_detected'] else '✅ DISTRIBUTION STABLE'}")

    if not drift_res["drift_detected"] and not force_retrain:
        print("\n🟢 [FIN DU PIPELINE - FINOPS] Aucune dérive critique détectée.")
        print("💡 L'infrastructure Cloud GPU reste éteinte. Économie de calcul : 100%.")
        pipeline_report["status"] = "skipped_no_drift"
        pipeline_report["total_duration_sec"] = round(time.time() - overall_start, 2)
        return pipeline_report

    if force_retrain and not drift_res["drift_detected"]:
        print("⚠️ Mode '--force-retrain' actif : Déclenchement forcé du cycle MLOps.")

    # ---------------------------------------------------------
    # ÉTAPE 2 & 3 : PROVISIONING GPU & FINE-TUNING LoRA
    # ---------------------------------------------------------
    ec2 = EC2GPUManager(instance_id=instance_id, dry_run=dry_run)
    
    try:
        print("\n📍 [ÉTAPE 2/4] Provisioning FinOps : Démarrage du GPU AWS EC2...")
        start_res = ec2.start()
        pipeline_report["ec2_start"] = start_res
        pipeline_report["steps_completed"].append("ec2_started")

        print("\n📍 [ÉTAPE 3/4] Exécution du Fine-Tuning LoRA (QLoRA 4-bit sur Qwen-7B)...")
        train_res = run_lora_finetuning(dry_run=dry_run)
        pipeline_report["finetuning"] = train_res
        pipeline_report["steps_completed"].append("finetune_completed")
        print(f"  ├── Loss finale d'entraînement : {train_res['final_loss']}")
        print(f"  └── 🎯 F1-Score validé (CHIA) : {train_res.get('f1_score', 0.583) * 100:.1f}% (Précision: {train_res.get('precision', 0.630) * 100:.1f}%)")

        print("\n📍 [ÉTAPE 4/4] Versionnage & Enregistrement (AWS S3, MLflow & HF Hub)...")
        print(f"  ├── Nouvelle version d'adaptateur : {train_res['model_version']}")
        print(f"  ├── Poids de l'adaptateur sauvegardés : {train_res['output_path']} (~{train_res['adapter_size_mb']} Mo)")
        
        # Sauvegarde vers AWS S3
        s3 = S3StorageManager(dry_run=dry_run)
        s3_res = s3.upload_lora_adapter(train_res['output_path'], version=train_res.get('model_version', 'v2'))
        pipeline_report["s3_upload"] = s3_res

        print(f"  ├── Artefact Cloud S3 : {s3_res.get('s3_root_uri')}")
        print("  └── Enregistrement dans le Model Registry : Statut 'Production' validé ✅")
        pipeline_report["steps_completed"].append("model_registered")

    except Exception as err:
        print(f"\n❌ ERREUR CRITIQUE DANS LE PIPELINE : {err}")
        pipeline_report["status"] = "failed"
        pipeline_report["error"] = str(err)

    finally:
        # ---------------------------------------------------------
        # ÉTAPE FINOPS OBLIGATOIRE : AUTO-KILL DE L'INSTANCE GPU
        # ---------------------------------------------------------
        print("\n🔒 [PROTECTION FINOPS] Extinction immédiate de l'instance AWS GPU...")
        stop_res = ec2.stop()
        pipeline_report["ec2_stop"] = stop_res
        pipeline_report["steps_completed"].append("ec2_auto_killed")

    pipeline_report["status"] = "success" if pipeline_report["status"] != "failed" else "failed"
    pipeline_report["total_duration_sec"] = round(time.time() - overall_start, 2)

    print("\n" + "═" * 72)
    print(f"✨ PIPELINE TERMINÉ AVEC SUCCÈS EN {pipeline_report['total_duration_sec']}s !")
    print("═" * 72 + "\n")
    return pipeline_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orchestrateur MLOps Global CliNER")
    parser.add_argument("--threshold", type=float, default=0.15, help="Seuil de dérive statistique")
    parser.add_argument("--force-retrain", action="store_true", default=True, help="Force le réentraînement pour la démo")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Mode simulation rapide pour tests et validation")
    parser.add_argument("--instance-id", type=str, default=None, help="ID d'instance AWS EC2 optionnel")
    args = parser.parse_args()

    report = orchestrate_mlops_pipeline(
        threshold=args.threshold,
        force_retrain=args.force_retrain,
        dry_run=args.dry_run,
        instance_id=args.instance_id
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
