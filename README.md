# Clinical Protocols Standardization (AI-Powered) 🔬

Ce projet est une application complète (Data Engineering & Data Science) permettant l'ingestion, le traitement, l'indexation vectorielle, et l'extraction sémantique d'entités depuis des protocoles cliniques (fichiers PDF).

## 🏗️ Architecture du Projet (Pipeline Hybride Asynchrone)

L'application suit une architecture hautement optimisée (FinOps) séparant drastiquement la recherche rapide (CPU) de l'extraction lourde (GPU) :

- **Branche A (Recherche Instantanée & Gratuite)** : L'application interroge l'API officielle ClinicalTrials V2 via des requêtes ciblées. Les résultats (Titre, Phase, Maladie) sont immédiatement affichés dans un tableau Streamlit. **Cette étape ne consomme aucune ressource IA.**
- **Branche B (Extraction & RAG Hybride via GPU)** : Uniquement lorsque l'utilisateur sélectionne une étude spécifique ou pose une question, le pipeline IA est déclenché sur un serveur distant doté de GPU (**AWS EC2 g4dn.xlarge**).
  - **Le Retriever (BioBERT)** : Fragmente le texte de l'essai et isole uniquement les paragraphes pertinents par similarité vectorielle.
  - **Le Generator NER (Qwen-7B + LoRA via vLLM)** : Notre LLM "In-House" (optimisé via QLoRA sur le dataset CHIA) lit le paragraphe ciblé et extrait un fichier JSON structuré des entités médicales à la vitesse de l'éclair.
  - **Le Chatbot RAG (Qwen-7B Instruct)** : Un agent conversationnel capable de répondre à des questions libres en s'appuyant sur les paragraphes vectorisés de la base, sans l'adaptateur LoRA pour garantir une réponse fluide.
  - *(Voir le détail des interactions dans [architecture_data_flow.md](docs/architecture_data_flow.md))*
- **Stockage Cloud Hybride (AWS S3 + Supabase pgvector)** :
  - **AWS S3 (Data Lake & Model Registry)** : Stockage pérenne haute capacité pour les PDF de protocoles bruts (`clinical_pdfs/`), les datasets CHIA (`datasets/`), et les adaptateurs LoRA versionnés (`models_lora/`).
  - **PostgreSQL Supabase (pgvector & Operational DB)** : Indexation vectorielle BioBERT (768 dimensions), recherche sémantique par similarité cosinus (`<=>`), et gestion du **Cache Intelligent** (`clinical_ner_cache`) pour esquiver les traitements GPU coûteux en 0.1s.
- **Monitoring & Traçabilité** : `MLflow` pour le suivi des métriques en temps réel (latence, prompts, loss d'entraînement, Cache Hits), avec persistance des artefacts sur AWS S3.

## 📂 Rôle des Scripts de Machine Learning & Données (`scripts/`)

Pour garantir une rigueur scientifique totale (pas de *Data Leakage*), l'équipe a développé une suite de scripts stricts pour gérer la donnée CHIA :

1.  **`extract_full_chia.py` (La Collecte)** : Se connecte aux sources (Drive/HuggingFace), rassemble les PDF et les annotations BRAT, et génère la base de données brute consolidée (`chia_gold_standard_v2.json`).
2.  **`split_dataset.py` (La Répartition)** : Sépare intelligemment la base brute. Il met de côté 5 études secrètes (Le *Holdout Set* dans un coffre-fort pour le jour J), puis coupe le reste en deux fichiers : `train_dataset.jsonl` (le cahier d'exercices) et `test_dataset.jsonl` (l'examen blanc).
3.  **`finetune_qwen.py` (L'Entraînement)** : Le script de MLOps ! Il prend le modèle de pointe **`Qwen/Qwen2.5-7B-Instruct`** (gelé pour préserver ses capacités linguistiques), injecte les adaptateurs **LoRA** (QLoRA 4-bit, rank=16, alpha=32), l'entraîne sur le `train_dataset.jsonl` (annotations CHIA) en ~20 minutes sur GPU, et sauvegarde son adaptateur médical (~84 Mo) dans `models/` et sur AWS S3.
4.  **`inference_qwen.py` (L'Évaluation)** : Le script d'examen. Il charge le modèle fine-tuné et le fait travailler à l'aveugle sur le `test_dataset.jsonl`. Il calcule ensuite mathématiquement le Score F1, la Précision et le Rappel pour le Benchmark officiel de la soutenance.

## 🚀 Démarrage Rapide

**1. Cloner le projet**
```bash
git clone https://github.com/Elkristobal59/cliner-mlops.git
cd cliner-mlops
```

**2. Configuration des Identifiants & Fichier `.env`**

Copiez le modèle `.env.example` vers `.env` :
```bash
cp .env.example .env
```

Le projet isole strictement ses responsabilités entre trois briques de services :
- **AWS Cloud (IAM, S3 Data Lake & FinOps EC2 GPU)** :
  - **IAM User dédié** : Créer un utilisateur IAM programmatique (ex: `cliner-mlops-bot`) avec `AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY`.
    - Droits nécessaires : `AmazonS3FullAccess` (ou restreint au bucket `cliner-clinical-storage-dev`) et droits EC2 de contrôle d'état (`ec2:StartInstances`, `ec2:StopInstances`, `ec2:DescribeInstances`).
  - **S3 Data Lake** : Un bucket dédié (ex: `cliner-clinical-storage-dev`, région `eu-west-3`) pour stocker les protocoles PDF volumineux, les datasets CHIA et les poids d'adaptateurs LoRA (~84 Mo).
  - **Mode FinOps / Simulation** : `MOCK_AWS_EC2=true` est activé par défaut. Il permet d'exécuter et de démontrer toute la cinématique MLOps à 0.00 € de coût.
- **Supabase (Base Opérationnelle & Vectorielle pgvector)** :
  - `SUPABASE_DATABASE_URL` : Chaîne PostgreSQL vers le pooler Supabase (port `6543`).
  - Gère les requêtes temps réel : indexation vectorielle `pgvector` des embeddings BioBERT (768d), recherche par similarité cosinus (`<=>`) en 12 ms, et cache chirurgical `clinical_ner_cache` (0.01s).
- **MLflow Tracking & Model Registry (Architecture Hybride & Full Cloud GCP Cloud Run)** :
  - **En local** : Fonctionne sans configuration via SQLite embarqué (`sqlite:///mlflow.db`).
  - **En Full Cloud (Google Cloud Run Serverless)** :
    - Déployé en tant que conteneur managé Serverless via `ghcr.io/mlflow/mlflow:v2.21.3` sur le port `8080`.
    - **FinOps Scale-to-Zero** : `min-instances=0` (coût = 0.00 € dès qu'aucun run ou utilisateur n'interroge le dashboard) et `max-instances=2`.
    - **Backend Store persistant** : Connecté à PostgreSQL Supabase (`SUPABASE_DATABASE_URL`) pour pérenniser l'historique des runs, hyperparamètres et métriques même quand le conteneur s'éteint.
    - **Artifact Store Cloud** : Connecté au bucket AWS S3 (`s3://cliner-clinical-storage-dev/mlflow_artifacts/`) ou GCS.
    - **Variable de connexion** : `MLFLOW_TRACKING_URI="https://<VOTRE_SERVICE_MLFLOW>.a.run.app"`. L'API FastAPI et le script de réentraînement LoRA y envoient directement leurs logs en HTTPS.

**3. Lancement du Backend Inférence & Monitoring (AWS EC2 GPU / Docker)**

En environnement de production ou sur une instance **AWS EC2 `g4dn.xlarge`** (Nvidia T4 GPU) :

```bash
# Lancer l'API FastAPI et le serveur MLflow
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
mlflow ui --host 0.0.0.0 --port 5000 --disable-security-middleware &
```

> 💡 **FinOps & Auto-Kill** : Pour ne pas laisser l'instance EC2 tourner inutilement, le module `07_mlops_reentrainement/ec2_manager.py` allume l'instance à la demande et l'éteint automatiquement dès la fin des opérations.

## 📂 Déploiement de l'Interface Web (Render / Docker)

L'interface client (Streamlit) est dockerisée pour être déployée sur Render, Heroku ou Cloud Run.
Le projet utilise un fichier `requirements-frontend.txt` allégé pour le conteneur Docker afin d'éviter l'installation des librairies GPU lourdes (torch, vllm, transformers) sur le frontend Streamlit. Tout le calcul GPU reste centralisé sur l'instance AWS EC2.

```bash
docker-compose up --build
```
L'application sera accessible sur le port `8501`.

> 🛠️ **Configuration & Variables d'Environnement sur Render / Cloud** :
> Pour que Streamlit communique avec l'API backend et Supabase, ajoutez ces variables dans votre dashboard :
> - `BACKEND_API_URL` : L'URL de votre backend API EC2 (ex: `http://<IP_PUBLIQUE_EC2>:8000` ou endpoint HTTPS)
> - `SUPABASE_URL` et `SUPABASE_KEY` : Vos clés d'API Supabase.
> 
> 🛠️ **Dépannage Render** :
> - **Redémarrages intempestifs (`Stopping...`)** : Fixez le port en ajoutant la variable d'environnement `PORT=8501`.
> - **Erreur `[Errno 24] inotify instance limit reached`** : Désactivez la surveillance locale en ajoutant `STREAMLIT_SERVER_FILE_WATCHER_TYPE=none`.

### Infrastructure as Code (Terraform)
Le dossier `terraform/` contient les scripts pour générer la structure de la base de données Supabase automatiquement (`main.tf`, `schema.sql`).
```bash
cd terraform
terraform init
terraform apply
```

## 🛠️ Améliorations Futures

### 1. Stratégie MLOps & Continuous Training Implémentée (`07_mlops_reentrainement/`)
Pour garantir la pérennité et la conformité RNCP 41993 (Niveau 7) de notre solution en production :
- **Data Drift (Wasserstein BioBERT)** : Mesure continue de la distance de Wasserstein sur les distributions d'embeddings BioBERT des protocoles récents (`drift_detection.py`).
- **Concept Drift (Human-in-the-Loop)** : Recueil des corrections d'entités par les praticiens médicaux dans la table Supabase de feedback.
- **Réentraînement Événementiel LoRA (QLoRA 4-bit)** : Dès que la dérive dépasse le seuil critique ($W > 0.15$), GitHub Actions ou l'orchestrateur local démarre l'instance GPU AWS EC2, réentraîne uniquement les matrices légères de LoRA (~84 Mo) sur Qwen2.5-7B, versionne l'adaptateur sur **AWS S3** et **MLflow**, puis coupe immédiatement l'instance GPU (**Auto-Kill FinOps**).

### 2. Améliorations Techniques
- **Traitement Multi-modal (CNN / ViT)** : Analyser directement les images, graphiques et scanners encapsulés dans les PDF grâce à des réseaux de neurones convolutifs (CNN) ou des Vision Transformers.
- **Scalabilité Cloud** : Architecture distribuée pour l'ingestion massive d'essais cliniques mondiaux.
- **Modèles SLM** : Fine-tuning d'un petit modèle (Small Language Model) spécialisé pour réduire considérablement les coûts d'inférence en production.
- **Auto-suppression Supabase (TTL / CRON)** : Routines de purge automatique pour effacer régulièrement les PDF temporaires stockés dans le Cloud, afin d'optimiser les coûts de stockage et de garantir la conformité RGPD.

---

## ☁️ Guide de Configuration Cloud AWS & GitHub Actions

Pour reproduire ou auditer l'infrastructure complète du projet :

### 1. IAM & Droits d'Accès
- **Utilisateur :** `github-actions-cliner-mlops`
- **Politiques attachées :** `AmazonEC2FullAccess` et `AmazonS3FullAccess`
- **Clés :** `AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY`

### 2. AWS S3 (Data Lake & Model Registry)
- **Bucket :** `cliner-clinical-storage-<unique>` (Région `eu-west-3` Paris)
- **Structure :**
  - `clinical_pdfs/` (protocoles cliniques bruts volumineux)
  - `datasets/` (`train_dataset.jsonl` et `test_dataset.jsonl`)
  - `models_lora/` (checkpoints des adaptateurs LoRA réentraînés ~84 Mo)

### 3. Instance EC2 GPU (`g4dn.xlarge`)
- **AMI :** `Deep Learning OSS Nvidia Driver AMI GPU PyTorch (Ubuntu 22.04)`
- **Type :** `g4dn.xlarge` (1x GPU NVIDIA Tesla T4 16 Go VRAM, 4 vCPU, 16 Go RAM)
- **Stockage EBS :** 60 Go (`gp3`)
- **Security Group (`cliner-ec2-sg`) :** Port 22 (SSH), Port 8000 (FastAPI), Port 5000 (MLflow)

### 4. Secrets GitHub Actions (6 Variables)
Dans **Settings** ➔ **Secrets and variables** ➔ **Actions** :
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` (`eu-west-3`), `AWS_EC2_GPU_INSTANCE_ID`, `S3_BUCKET_NAME`, `SUPABASE_DATABASE_URL`.

### 5. Workflows CI/CD Automatisés
- **`ci_mlops.yml`** (Déclenchement automatique à chaque push) : Linting Flake8, simulation MLOps et build Docker.
- **`deploy_ec2_autokill.yml`** (Déclenchement manuel pour démo/soutenance) : Démarre l'EC2 GPU, active un minuteur de démo (15 à 60 min), et déclenche **l'Auto-Kill FinOps** automatique à l'issue de la session.

---

## 🎓 FAQ & Arguments Clés pour la Soutenance (RNCP 41993 - Bloc 4)

### Q1 : Pourquoi une architecture hybride AWS S3 + Supabase pgvector ? Pourquoi pas 100% S3 ?
* **AWS S3 = Data Lake & Model Registry :** Stockage passif illimité et économique (~0,02 $/Go/mois) pour les données volumineuses (PDFs de 100 pages, datasets, adaptateurs LoRA ~84 Mo).
* **Supabase (pgvector) = Moteur Vectoriel & Base Opérationnelle :** S3 ne sait pas faire de calcul vectoriel mathématique. PostgreSQL `pgvector` calcule la similarité cosinus (`<=>`) en 12 millisecondes et offre un cache d'inférence (`clinical_ner_cache`) répondant en 0,01s. Remplacer Supabase par S3 ferait bondir la latence de **15 ms à plus de 25 secondes** (obligation de tout recalculer en RAM Python à chaque question).

### Q2 : Pourquoi ne pas réentraîner Qwen-7B tous les jours sur un CRON ?
Réentraîner un LLM de 7 milliards de paramètres à l'aveugle sur planification chronologique est une faute d'architecture FinOps et GreenOps. Nous appliquons un **réentraînement événementiel conditionné** :
- BioBERT mesure la distance de **Wasserstein** sur la distribution d'embeddings.
- Si et seulement si $W > 0.15$ (ou si 100 nouvelles corrections médicales sont validées), le pipeline MLOps allume le GPU EC2, réentraîne uniquement les matrices LoRA légères (84 Mo, ~20 min de calcul), puis éteint immédiatement l'instance (Auto-Kill).

### Q3 : Quel est le cloisonnement avec le projet CDSD (`clinicalapp`) ?
Les deux projets sont **strictement étanches** :
- **CDSD** (`clinicalapp`) : centré sur l'applicatif Data Science (Streamlit, FastAPI, premier modèle de base).
- **Lead AI RNCP 41993** (`cliner-mlops`) : centré sur l'ingénierie système (migration Full AWS EC2 GPU, S3 Data Lake, Continuous Training sur dérive Wasserstein, CI/CD GitHub Actions, FinOps Auto-Kill).
- Dépôts Git distincts, dossiers locaux distincts, et lecture seule non destructrice sur la base Supabase.

