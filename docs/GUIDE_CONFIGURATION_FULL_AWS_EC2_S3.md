# ☁️ Guide Pas-à-Pas : Configuration Full AWS (EC2 GPU, S3 & GitHub Actions)

> **Projet :** CliNER-MLOPS  
> **Objectif :** Déployer une architecture Cloud 100% AWS industrielle, automatisée et sécurisée avec gestion FinOps (Auto-Kill).  
> **Composants AWS :** AWS EC2 (`g4dn.xlarge` GPU T4), AWS S3 (`cliner-clinical-storage`), AWS IAM, GitHub Actions CI/CD.  

---

## 🗺️ Architecture Cible Full AWS

```
┌────────────────────────────────────────────────────────────────────────┐
│                          GITHUB ACTIONS (CI/CD)                        │
│   • Secrets : AWS_ACCESS_KEY_ID / SECRET / EC2_INSTANCE_ID / S3_BUCKET  │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ 1. Start EC2 & Run              │ 4. Auto-Kill (Stop)
                   ▼                                 ▼
┌──────────────────────────────────────┐     ┌───────────────────────────┐
│     AWS EC2 GPU (g4dn.xlarge)        │     │      AWS S3 BUCKET        │
│   • Docker Container                 │◄───►│ • PDF Protocoles bruts    │
│   • FastAPI (Port 8000)              │     │ • Datasets CHIA (.jsonl)  │
│   • MLflow Server (Port 5000)        │     │ • Adaptateurs LoRA (84 Mo)│
│   • Inférence vLLM (Qwen-7B LoRA)    │     └───────────────────────────┘
└──────────────────┬───────────────────┘
                   │ Port 8000
                   ▼
┌──────────────────────────────────────┐
│     FRONTEND STREAMLIT (Port 8501)   │
│   • Déployé sur Render / Cloud       │
└──────────────────────────────────────┘
```

---

## 🛠️ ÉTAPE 1 : Création de l'Utilisateur IAM & Clés d'Accès

Pour que GitHub Actions et vos scripts Python (`boto3`) puissent piloter AWS, créez un utilisateur avec le principe du moindre privilège :

1. Rendez-vous sur la console **AWS ➔ IAM (Identity and Access Management)**.
2. Cliquez sur **Users (Utilisateurs)** ➔ **Create user (Créer un utilisateur)** :
   * Nom : `github-actions-cliner-mlops`.
3. Attachez les permissions directement (*Attach policies directly*) :
   * `AmazonEC2FullAccess` (ou une politique restreinte à `StartInstances`, `StopInstances`, `DescribeInstances`).
   * `AmazonS3FullAccess` (pour lire et écrire dans votre bucket).
4. Une fois l'utilisateur créé, allez dans l'onglet **Security credentials (Identifiants de sécurité)**.
5. Section **Access keys (Clés d'accès)** ➔ Cliquez sur **Create access key** :
   * Sélectionnez le cas d'usage : *Application running outside AWS* (ou *Command Line Interface*).
   * ⚠️ **Copiez immédiatement :**
     - **Access Key ID** (ex: `AKIAIOSFODNN7EXAMPLE`)
     - **Secret Access Key** (ex: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)

---

## 🪣 ÉTAPE 2 : Création du Bucket S3 (`cliner-clinical-storage`)

Le bucket S3 sert de stockage durable centralisé pour les protocoles PDF, les datasets d'entraînement et les poids LoRA réentraînés.

1. Rendez-vous sur la console **AWS ➔ S3**.
2. Cliquez sur **Create bucket (Créer un compartiment)** :
   * **Bucket name :** `cliner-clinical-storage-<votre-nom>` *(le nom doit être unique mondialement, ex: `cliner-storage-christopher`)*.
   * **AWS Region :** `eu-west-3` (Paris) ou `eu-west-1` (Irlande).
   * **Block Public Access :** Laissez tout coché par défaut (Privé - sécurité maximale).
   * **Encryption :** Chiffrement par défaut côté serveur (Amazon S3 managed keys - SSE-S3).
3. Cliquez sur **Create bucket**.
4. Créez 3 sous-dossiers dans le bucket pour organiser la donnée :
   * `clinical_pdfs/` (les protocoles PDF bruts)
   * `datasets/` (`train_dataset.jsonl` et `test_dataset.jsonl`)
   * `models_lora/` (les versions de l'adaptateur LoRA)

---

## 🖥️ ÉTAPE 3 : Création de l'Instance EC2 GPU (`g4dn.xlarge`)

1. Rendez-vous sur la console **AWS ➔ EC2** (dans la même région que votre bucket, ex: `eu-west-3`).
2. Cliquez sur **Launch Instance (Lancer une instance)** :
   * **Nom :** `cliner-gpu-worker-mlops`
   * **AMI (Système d'exploitation) :**
     * Recherchez dans les AMI Marketplace ou Community :  
       👉 **Deep Learning OSS Nvidia Driver AMI GPU PyTorch (Ubuntu 22.04)**  
       *(Cette AMI intègre nativement les pilotes Nvidia CUDA, PyTorch et Docker configurés avec Nvidia Container Toolkit, vous évitant 3 heures d'installation de drivers).*
   * **Type d'instance :**
     * Sélectionnez **`g4dn.xlarge`** (4 vCPU, 16 Go RAM, 1x GPU NVIDIA Tesla T4 16 Go VRAM).
   * **Paire de clés (Key pair) :**
     * Créez une nouvelle clé (ex: `cliner-key.pem`) et téléchargez-la précieusement sur votre machine.
   * **Paramètres réseau (Security Group) :**
     * Créez un Security Group nommé `cliner-ec2-sg` avec les règles entrantes suivantes :
       * **Port 22 (SSH) :** Autorisé pour votre IP (`My IP`).
       * **Port 8000 (FastAPI Backend) :** Autorisé pour `Anywhere-IPv4 (0.0.0.0/0)` (pour que Streamlit puisse appeler l'API).
       * **Port 5000 (MLflow UI) :** Autorisé pour `Anywhere-IPv4 (0.0.0.0/0)` ou votre IP.
       * **Port 8501 (Streamlit) :** Optionnel si vous testez Streamlit directement sur la machine.
   * **Stockage (Disque dur EBS) :**
     * Définissez au moins **60 Go (gp3)** (le modèle de base Qwen-7B et les images Docker nécessitent de la place).
3. Cliquez sur **Launch instance**.
4. 📋 **Notez précieusement l'ID de votre instance :**  
   *(ex: `i-09f18a47bce42gpu`).*

> [!TIP]
> **FinOps Réflexe :** Éteignez l'instance dès qu'elle a fini de démarrer (*Instance state ➔ Stop instance*). Elle ne sera allumée que par les scripts d'automatisation ou pour vos tests.

---

## 🔒 ÉTAPE 4 : Configuration des Secrets GitHub Actions

Sur votre repository GitHub [Elkristobal59/cliner-mlops](https://github.com/Elkristobal59/cliner-mlops) :

1. Allez dans l'onglet **Settings** ➔ **Secrets and variables** ➔ **Actions**.
2. Cliquez sur **New repository secret** et ajoutez ces 5 secrets :

| Nom du Secret | Valeur à renseigner |
| :--- | :--- |
| `AWS_ACCESS_KEY_ID` | Votre clé d'accès IAM (Étape 1) |
| `AWS_SECRET_ACCESS_KEY` | Votre clé secrète IAM (Étape 1) |
| `AWS_DEFAULT_REGION` | `eu-west-3` (ou votre région) |
| `AWS_EC2_GPU_INSTANCE_ID` | L'ID de votre instance EC2 (ex: `i-09f18a47bce42gpu`) |
| `S3_BUCKET_NAME` | Le nom de votre bucket (ex: `cliner-storage-christopher`) |
| `SUPABASE_DATABASE_URL` | Votre URL Postgres Supabase existante |

---

## 🚀 ÉTAPE 5 : Les Workflows GitHub Actions Prêts à l'Emploi

Deux workflows automatisent la vie du projet dans `.github/workflows/` :

### 1️⃣ `ci_mlops.yml` (Intégration Continue & Quality Gate)
Se déclenche à chaque push/PR :
- Linting syntaxique (`flake8`).
- Test de détection de dérive sémantique sur BioBERT.
- Test de l'orchestrateur en mode simulation sans coût.
- Build de validation des conteneurs Docker.

### 2️⃣ `deploy_ec2_autokill.yml` (Déploiement Démo avec Auto-Kill)
Se déclenche manuellement via le bouton **Run workflow** sur GitHub :
- Allume l'instance EC2 GPU via `boto3`.
- Rapatrie le code à jour et démarre l'API FastAPI et MLflow dans Docker.
- Attend que l'endpoint `/health` réponde `200 OK`.
- Affiche l'adresse IP publique pour votre démo.
- **Minuteur FinOps de 45 minutes :** Éteint automatiquement l'instance EC2 à la fin du temps imparti si vous avez oublié de le faire !

---

## 💻 ÉTAPE 6 : Initialisation Rapide sur l'Instance EC2 (Premier démarrage)

La toute première fois que vous vous connectez en SSH sur l'instance :

```bash
# Connexion SSH
ssh -i "cliner-key.pem" ubuntu@<IP_PUBLIQUE_EC2>

# Cloner le repo
git clone https://github.com/Elkristobal59/cliner-mlops.git
cd cliner-mlops

# Synchroniser les fichiers avec S3 (si besoin)
aws s3 sync s3://cliner-storage-christopher/data ./data

# Lancer la stack en arrière-plan
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
mlflow ui --host 0.0.0.0 --port 5000 --disable-security-middleware &
```

Votre instance est prête, monitorée, et pilotable à distance !
