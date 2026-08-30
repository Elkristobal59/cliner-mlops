# ⚡ Guide : Exécuter le Pipeline de Fine-Tuning sur Lightning.ai

Ce dossier contient tout ce dont vous avez besoin pour lancer l'extraction du dataset V2 (1000 études CHIA) et le fine-tuning complet de Qwen sur une machine Cloud performante (Linux + GPU). 

Ne lancez pas cela sur votre Windows local si votre GPU est saturé ou si PyTorch freeze ! Utilisez la puissance de Lightning.ai.

## 🚀 Étape 1 : Préparation de l'environnement sur Lightning.ai

Ouvrez un terminal sur votre instance Lightning et assurez-vous d'avoir la bonne version de la librairie `datasets` pour contourner la sécurité de HuggingFace sur les scripts personnalisés :

```bash
pip install "datasets==2.20.0" "pyarrow<20"
```

## 📊 Étape 2 : Extraction et Split du Dataset V2 (Les 1000 études)

On télécharge d'abord le dataset officiel CHIA complet depuis HuggingFace et on le transforme en `.jsonl` :

```bash
python scripts/extract_full_chia.py
```

*(Cela va générer le fichier `data/chia_full_dataset.jsonl`)*

Ensuite, on découpe rigoureusement ce dataset pour éviter le Data Leakage (800 pour l'entraînement, 200 pour le test) :

```bash
python scripts/split_dataset.py
```

*(Cela va générer `data/train_dataset.jsonl` et `data/test_dataset.jsonl`)*

## 🧠 Étape 3 : Lancement du Fine-Tuning (GPU)

Maintenant que la donnée est propre et séparée, lancez l'entraînement :

```bash
python scripts/finetune_qwen.py
```

Le script est déjà configuré pour lire `data/train_dataset.jsonl`.
Une fois l'entraînement terminé, le modèle optimisé (poids LoRA) sera sauvegardé dans le dossier `models/qwen_chia_finetuned`.

## 📦 Étape 4 : Rapatriement

Vous n'avez plus qu'à télécharger le dossier `models/qwen_chia_finetuned` (qui pèse quelques Mégaoctets) vers votre ordinateur local Windows. Votre application locale pourra alors utiliser cette IA sur-entraînée pour le Demo Day !
