# Script PowerShell pour installer les dépendances nécessaires au Fine-Tuning QLoRA
# A exécuter dans l'environnement virtuel du projet (Pipenv / Venv)

Write-Host "Installation des dépendances Machine Learning pour le Fine-Tuning..." -ForegroundColor Cyan

# 1. Installer PyTorch avec support CUDA 12.1 (idéal pour RTX 3060)
Write-Host "Installation de PyTorch (CUDA)..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 2. Installer les bibliothèques Hugging Face et LoRA
Write-Host "Installation de Transformers, PEFT, TRL et Datasets..." -ForegroundColor Yellow
pip install transformers datasets accelerate peft trl

# 3. Installer BitsAndBytes pour la quantification en 4-bits (nécessaire pour que ça tienne dans les 12Go de la RTX 3060)
Write-Host "Installation de BitsAndBytes (pour QLoRA 4-bits)..." -ForegroundColor Yellow
pip install bitsandbytes scipy

Write-Host "Toutes les dépendances ont été installées avec succès !" -ForegroundColor Green
Write-Host "Vous pouvez maintenant lancer le script : python scripts/finetune_qwen.py" -ForegroundColor Magenta
