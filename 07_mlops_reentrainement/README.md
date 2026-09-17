# 🔁 Module MLOps : Pipeline Automatisé de Dérive & Réentraînement LoRA

> **Dossier :** `07_mlops_reentrainement/`  
> **Projet :** **CliNER-MLOPS**  
> **Titre visé :** Architecte en Intelligence Artificielle (RNCP41993 – Niveau 7)  
> **Bloc évalué :** **Bloc 4** — Concevoir et piloter l'industrialisation et le déploiement de solutions d'IA (Continuous Training & FinOps)

---

## 🏗️ Architecture du Module

```
07_mlops_reentrainement/
├── drift_detection.py      -> mesure le drift sur les embeddings (décide s'il faut ré-entraîner)
├── finetune_lora.py        -> ré-entraîne l'adaptateur LoRA (QLoRA) sur Qwen 7B
├── ec2_manager.py          -> allume / éteint l'instance EC2 GPU (boto3)
├── run_pipeline.py         -> l'orchestrateur : drift -> EC2 -> finetune -> récup LoRA -> kill
├── Dockerfile              -> packager le code de fine-tuning
├── requirements_mlops.txt  -> dépendances Python du conteneur
├── scheduler.md            -> le déclencheur hebdo (cron / AWS EventBridge)
└── README.md               -> vue d'ensemble (ce document)
```

---

## 🎯 Pourquoi cette Architecture est Idéale pour le Jury

1. **Pas de Réentraînement Chronologique Aveugle (FinOps / GreenOps) :**  
   Au lieu de faire tourner une carte graphique à 10 000 € toutes les nuits, le système commence par `drift_detection.py`. Si les données n'ont pas bougé, **l'instance GPU reste éteinte**.
2. **Allumage et Extinction à la Demande (`ec2_manager.py`) :**  
   L'instance GPU AWS EC2 n'est allumée que pendant les ~20 minutes nécessaires au calcul, puis **immédiatement coupée (Auto-Kill)** via `boto3`.
3. **Agilité & Légèreté du LoRA (`finetune_lora.py`) :**  
   On ne touche pas au modèle de base de 15 Go (Qwen-7B). On n'entraîne et ne versionne que les matrices adaptatrices (~80 Mo), ce qui rend le cycle de vie ultra-rapide et économique.
4. **Conteneurisation Complète (`Dockerfile`) :**  
   L'environnement est encapsulé, sans conflit de dépendances, prêt pour ECS, Kubernetes ou une VM dédiée.

---

## ⚡ Guide de Démarrage Rapide

### 1. Tester le Détecteur de Dérive Seul
```bash
python 07_mlops_reentrainement/drift_detection.py --threshold 0.15
```

### 2. Tester le Gestionnaire FinOps EC2 (Simulation)
```bash
python 07_mlops_reentrainement/ec2_manager.py --action start --dry-run
python 07_mlops_reentrainement/ec2_manager.py --action stop  --dry-run
```

### 3. Lancer l'Orchestrateur Complet (Démo Jury / Mode Simulé)
```bash
python 07_mlops_reentrainement/run_pipeline.py --dry-run --force-retrain
```

---

## 📊 Exemple de Sortie du Pipeline

```text
╔══════════════════════════════════════════════════════════════════════╗
║     🚀 PIPELINE D'AUTOMATISATION MLOPS & CONTINUOUS TRAINING         ║
║          Projet CliNER — RNCP41993 Architecte IA (Niveau 7)          ║
╚══════════════════════════════════════════════════════════════════════╝

📍 [ÉTAPE 1/4] Surveillance de dérive sur les protocoles récents...
  ├── Distance de Wasserstein : 0.2415 (Seuil: 0.15)
  └── Statut Dérive : 🚨 DRIFT DÉTECTÉ

📍 [ÉTAPE 2/4] Provisioning FinOps : Démarrage du GPU AWS EC2...
  └── Instance passée en état 'running' (IP: 54.198.42.105)

📍 [ÉTAPE 3/4] Exécution du Fine-Tuning LoRA (QLoRA 4-bit sur Qwen-7B)...
  ├── Loss finale : 0.284
  └── Poids de l'adaptateur sauvegardés : models/qwen_7b_lora_retrained (~84 Mo)

📍 [ÉTAPE 4/4] Versionnage & Enregistrement (MLflow & HF Hub)...
  └── Version qwen-7b-chia-ner-v2 promue en 'Production' ✅

🔒 [PROTECTION FINOPS] Extinction immédiate de l'instance AWS GPU...
  └── Instance stoppée. Facturation arrêtée. Coût résiduel = 0.00 €.

✨ PIPELINE TERMINÉ AVEC SUCCÈS EN 7.82s !
```
