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
- **Stockage Cloud (Supabase Storage & DB)** : Les PDF bruts sont sauvegardés dans un bucket public sur Supabase (`clinical_pdfs`). Les vecteurs mathématiques sont indexés via l'extension `pgvector`.
- **⚡ Cache Intelligent (Supabase)** : Si un essai clinique a déjà été extrait par le passé, son résultat est stocké en base (`clinical_ner_cache`). L'application l'affiche instantanément (0.1s), esquivant ainsi tout traitement GPU coûteux.
- **Monitoring** : `MLflow` pour le suivi des performances en temps réel (latence, prompts, JSON de sortie, Cache Hits).

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

**2. Lancement du Backend Inférence & Monitoring (AWS EC2 GPU / Docker)**

En environnement de production ou sur une instance **AWS EC2 `g4dn.xlarge`** (Nvidia T4 GPU) :

```bash
# Configuration de la base Supabase
echo 'SUPABASE_DATABASE_URL="postgresql://postgres.<PROJECT_REF>:<PASSWORD_URL_ENCODED>@<SUPABASE_POOLER_HOST>:6543/postgres"' > .env

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
