# ⏰ Stratégies de Déclenchement Automatisé (Scheduler & Triggers)

> **Projet :** CliNER-MLOPS — Continuous Training (CT)  
> **Composant :** `07_mlops_reentrainement/scheduler.md`  
> **Rôle :** Décrit comment et quand le pipeline MLOps est planifié ou déclenché en environnement de production.

---

## 🧭 Deux Stratégies Complémentaires

En production d'entreprise (centre hospitalier ou laboratoire pharmaceutique), l'orchestration repose sur deux modes de déclenchement :

1. **Le Déclencheur Périodique (CRON Hebdomadaire) :**  
   Pour vérifier chaque semaine si des nouveaux protocoles sont arrivés et si la distribution vectorielle a dérivé.
2. **Le Déclencheur Événementiel (Event-Driven Trigger) :**  
   Déclenché instantanément dès qu'un seuil de $N \ge 5$ nouveaux protocoles est inséré dans Supabase ou validé par un clinicien.

---

## 1️⃣ Option 1 : GitHub Actions (Cron Hebdomadaire — Solution 100% Free Tier)

Fichier recommandé : `.github/workflows/weekly_mlops_pipeline.yml`

```yaml
name: Weekly MLOps Drift & Retraining Pipeline

on:
  schedule:
    # Exécution chaque dimanche à 23h00 UTC
    - cron: '0 23 * * 0'
  workflow_dispatch: # Permet aussi le lancement manuel en 1 clic pour la démo

jobs:
  mlops-pipeline:
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout du Code
        uses: actions/checkout@v4

      - name: 🐍 Configuration Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: 📦 Installation des dépendances
        run: |
          pip install -r 07_mlops_reentrainement/requirements_mlops.txt

      - name: 🚀 Exécution de l'Orchestrateur MLOps
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: 'eu-west-3'
          AWS_EC2_GPU_INSTANCE_ID: ${{ secrets.AWS_EC2_GPU_INSTANCE_ID }}
          SUPABASE_DATABASE_URL: ${{ secrets.SUPABASE_DATABASE_URL }}
        run: |
          python 07_mlops_reentrainement/run_pipeline.py --threshold 0.15
```

---

## 2️⃣ Option 2 : AWS EventBridge + AWS Lambda (Architecture Serverless Cloud)

En environnement d'entreprise AWS natif :

```
┌─────────────────────────┐
│     AWS EventBridge     │ (Règle CRON : cron(0 23 ? * SUN *))
└────────────┬────────────┘
             │ Événement planifié
             ▼
┌─────────────────────────┐
│       AWS Lambda        │ (Fonction Python légère)
└────────────┬────────────┘
             │ Déclenche le conteneur Docker
             ▼
┌─────────────────────────┐
│     AWS ECS / EC2       │ (Lance 'run_pipeline.py' dans le conteneur)
│       (GPU Spot)        │
└────────────┬────────────┘
             │ Auto-Kill dès la fin
             ▼
┌─────────────────────────┐
│    Extinction Immédiate │ (0.00 € de coût au repos)
└─────────────────────────┘
```

### Code de la Fonction Lambda de Déclenchement :
```python
import boto3

def lambda_handler(event, context):
    ecs = boto3.client('ecs')
    response = ecs.run_task(
        cluster='cliner-mlops-cluster',
        taskDefinition='cliner-retraining-task',
        launchType='FARGATE',
        overrides={
            'containerOverrides': [
                {
                    'name': 'mlops-worker',
                    'command': ['python', 'run_pipeline.py', '--threshold', '0.15']
                }
            ]
        }
    )
    return {"status": "Pipeline MLOps déclenché avec succès", "taskArn": response['tasks'][0]['taskArn']}
```

---

## 3️⃣ Option 3 : Déclencheur Événementiel Supabase (Database Webhook)

* **Règle SQL :** Un trigger PostgreSQL sur la table `clinical_trials_data_biobert` compte les nouveaux ajouts.
* **Condition :** Dès que `COUNT(DISTINCT doc_id) >= 5` depuis le dernier réentraînement, Supabase émet un **Webhook HTTP POST** vers l'orchestrateur pour déclencher l'analyse de dérive sans attendre la fin de la semaine.
