import os
import shutil

legacy_dir = 'scripts/legacy'
os.makedirs(legacy_dir, exist_ok=True)

files_to_move = [
    'init_neondb.py',
    'live_scraper.py',
    'build_chia_gold_standard.py',
    'fetch_sample_trials.py',
    'prepare_finetuning_data.py'
]

for f in files_to_move:
    src = os.path.join('scripts', f)
    dst = os.path.join(legacy_dir, f)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {f} to legacy/")
    else:
        print(f"Skipped {f} (not found)")
