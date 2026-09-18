# ⏰ Stratégies de Déclenchement Automatisé (Scheduler & Triggers)

> **Projet :** CliNER-MLOPS — Continuous Training (CT)  
> **Composant :** `07_mlops_reentrainement/scheduler.md`  
> **Rôle :** Spécifie les stratégies de planification, l'architecture d'ingestion continue, les modes d'exécution et la politique de rétention des données.

---

## 🧭 Architecture Retenue vs Alternatives Industrielles

Dans ce projet, le choix architectural est guidé par les principes **FinOps** (coût au repos strictement égal à 0,00 €) et **DevSecOps** (centralisation des secrets dans GitHub) :

| Option | Technologie | Statut dans le Projet | Justification Décisionnelle |
| :--- | :--- | :---: | :--- |
| **Option 1 (Retenue)** | **GitHub Actions Cron Hebdomadaire** | **✅ DÉPLOYÉE & ACTIVE** | **100% Free Tier (2 000 min/mois gratuites)**, aucun serveur ni composant cloud en écoute permanente, exécution isolée sur runner éphémère. |
| **Option 2** | AWS EventBridge + Lambda + ECS | ℹ️ Alternative Enterprise | Solution cloud-native robuste mais requiert des rôles IAM cross-services et des coûts de veille potentiels (VPC Endpoints, NAT Gateway). |
| **Option 3** | Supabase Webhook HTTP | ℹ️ Alternative Événementielle | Réactivité instantanée à chaque insertion, mais nécessite un endpoint public d'écoute exposé 24/7 (anti-pattern FinOps). |

---

## 1️⃣ La Solution Active du Projet : GitHub Actions Cron Hebdomadaire

Fichier déployé dans le dépôt : [`.github/workflows/weekly_mlops_pipeline.yml`](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/.github/workflows/weekly_mlops_pipeline.yml)

```yaml
name: Weekly MLOps Drift & Retraining Pipeline

on:
  schedule:
    # Exécution planifiée chaque lundi à 02h00 UTC
    - cron: '0 2 * * 1'
  workflow_dispatch: # Permet également le déclenchement manuel immédiat en un clic

jobs:
  weekly-mlops-job:
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 🐍 Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: 📦 Install Dependencies
        run: |
          pip install --upgrade pip
          pip install pytest flake8 numpy scipy boto3 mlflow

      - name: 🧪 Run Automated PyTest Suite
        run: |
          pytest tests/ -v

      - name: 🚀 Run Continuous Training Orchestrator
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: ${{ secrets.AWS_DEFAULT_REGION || 'eu-west-3' }}
          AWS_EC2_GPU_INSTANCE_ID: ${{ secrets.AWS_EC2_GPU_INSTANCE_ID }}
          S3_BUCKET_NAME: ${{ secrets.S3_BUCKET_NAME || 'cliner-mlops' }}
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
          SUPABASE_DATABASE_URL: ${{ secrets.SUPABASE_DATABASE_URL }}
        run: |
          python 07_mlops_reentrainement/run_pipeline.py --threshold 0.15
```

---

## 🔄 Cinématique d'Ingestion & Réentraînement : Comment ça fonctionne ?

### 1. Les Deux Modes d'Alimentation du Système

Le système combine deux modes complémentaires d'ingestion et d'analyse :

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           DEUX MODES D'INGESTION COMPLÉMENTAIRES                 │
│                                                                                  │
│  [MODE A : À LA DEMANDE (PRATICIEN)]                                             │
│    🧑‍⚕️ Médecin saisit une pathologie cible sur Streamlit (ex: "Breast Cancer")     │
│        └──► Requête temps réel API ClinicalTrials.gov V2 (CPU / 0.00 €)          │
│        └──► Sélection d'une étude -> Ingestion JSON / PDF S3                      │
│        └──► BioBERT (768d) -> Supabase pgvector & Cache NER instantané           │
│                                                                                  │
│  [MODE B : CRON HEBDOMADAIRE (VEILLE MLOPS CONTINUE)]                            │
│    ⏰ GitHub Actions (Lundi 02h00 UTC) s'exécute automatiquement                 │
│        └──► Requête de veille sur les études récentes publiées dans la semaine   │
│             (ex: cohorte oncologie ou filtre API LastUpdatePostDate)             │
│        └──► Ingestion & archivage dans S3 Data Lake                              │
│        └──► Calcul Wasserstein Drift sur fenêtre glissante (5 derniers protocoles)│
│        └──► Si W > 0.15 -> Réveil EC2 GPU -> Fine-Tuning LoRA -> Auto-Kill        │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### 🔹 Mode A : Ingestion Interactive (Appel du Praticien)
* Le praticien se connecte à l'application web Streamlit et saisit **n'importe quelle pathologie** (ex: *Mélanome*, *Diabète de type 2*, *Cancer colorectal*).
* L'API ClinicalTrials.gov v2 est interrogée en direct, affiche la *Summary Table*, et le médecin sélectionne l'étude à analyser.
* Le protocole est découpé, encodé par BioBERT et stocké dans `clinical_trials_data_biobert` (et `clinical_ner_cache`).

#### 🔹 Mode B : Ingestion Automatisée de Veille (Cron Hebdomadaire)
* Le cron GitHub Actions s'exécute chaque lundi matin de manière totalement autonome.
* **Comment sait-il quoi chercher sans médecin ?**
  Le job utilise une requête de veille programmée :
  1. **Cohorte cible paramétrée :** Par défaut, un domaine thérapeutique prioritaire d'oncologie (ex: `"non-small cell lung cancer"` ou `"solid tumors"`).
  2. **Filtre de fraîcheur de l'API v2 :** La requête API peut cibler les protocoles mis à jour au cours des 7 derniers jours (`filter.advanced=AREA[LastUpdatePostDate]RANGE[NOW-7DAYS,NOW]`).
* Les nouveaux protocoles collectés sont archivés dans le Data Lake S3 et vectorisés par BioBERT.

---

## 🗑️ Faut-il vider la base au bout de X semaines ? (Politique de Rétention & FinOps)

> **Réponse nette : NON, on ne vide jamais brutalement la base de données.**  
> L'architecture applique une politique de gestion des données différenciée et propre aux standards de l'industrie :

### 1. Sur le Data Lake AWS S3 (`s3://cliner-mlops/`) : Conservation Immuable
* **Principe d'intégrité :** Les protocoles bruts (JSON v2 complets et PDFs de 50 pages) constituent le patrimoine immuable de l'établissement de santé. Ils sont archivés et partitionnés chronologiquement (`s3://cliner-mlops/clinical_studies/year=2026/month=09/`).
* **Coût négligeable :** Le stockage S3 Standard coûte ~0,023 $/Go/mois. Conserver 10 000 protocoles JSON (~150 Mo) coûte moins de **0,005 $ par an** ! Il n'y a donc aucune raison FinOps de les supprimer.

### 2. Sur la Base Vectorielle Supabase (`pgvector`) : Mises à jour Idempotentes
* On ne vide pas la base (`TRUNCATE` interdit).
* On applique un remplacement **idempotent par protocole** :
  ```sql
  DELETE FROM clinical_trials_data_biobert WHERE doc_id = %s;
  ```
  Si une étude est révisée par les chercheurs sur ClinicalTrials.gov, ses anciens fragments vectoriels sont purgés avant de réinsérer les nouveaux, évitant toute pollution vectorielle ou doublon. Les autres études restent intactes.

### 3. Sur la Détection de Dérive (Wasserstein Drift) : Fenêtre Glissante (*Sliding Window*)
* Pour évaluer la dérive sémantique, `drift_detection.py` ne calcule pas la dérive sur l'ensemble de la base historique (ce qui masquerait les variations récentes).
* L'algorithme extrait une **fenêtre glissante des $N$ derniers protocoles ingérés** (typiquement les 5 ou 10 derniers) :
  ```sql
  SELECT embedding FROM clinical_trials_data_biobert ORDER BY id DESC LIMIT 5;
  ```
* Cette cohorte récente est comparée statistiquement à la distribution de référence immuable (**Gold Standard CHIA de 800 protocoles**).
* Si de nouveaux termes médicaux ou des modifications substantielles de critères apparaissent dans ces 5 derniers protocoles, la distance de Wasserstein grimpe ($W > 0.15$) et déclenche le réentraînement ciblé.

---

## 2️⃣ Option Alternative 2 : AWS EventBridge + AWS Lambda (Architecture Serverless Cloud)

En environnement d'entreprise où l'ensemble des composants réside strictement au sein d'un même compte AWS :

```text
┌─────────────────────────┐
│     AWS EventBridge     │ (Règle CRON : cron(0 2 ? * MON *))
└────────────┬────────────┘
             │ Événement planifié
             ▼
┌─────────────────────────┐
│       AWS Lambda        │ (Fonction Python légère)
└────────────┬────────────┘
             │ Déclenche la tâche conteneurisée
             ▼
┌─────────────────────────┐
│     AWS ECS / EC2       │ (Lance 'run_pipeline.py' dans le conteneur)
│       (GPU Spot)        │
└────────────┬────────────┘
             │ Auto-Kill dès la fin (bloc finally:)
             ▼
┌─────────────────────────┐
│    Extinction Immédiate │ (0.00 € de coût au repos)
└─────────────────────────┘
```

---

## 3️⃣ Option Alternative 3 : Déclencheur Événementiel Supabase (Database Webhook)

* **Règle SQL :** Un trigger PostgreSQL sur la table `clinical_trials_data_biobert` compte les nouveaux ajouts.
* **Condition :** Dès que `COUNT(DISTINCT doc_id) >= 5` nouveaux protocoles sont insérés depuis le dernier run, Supabase émet un **Webhook HTTP POST** vers l'orchestrateur.
* **Inconvénient FinOps :** Nécessite une passerelle d'API ou un conteneur toujours en écoute (alors que le Cron GitHub Actions ne consomme aucune ressource continue).
