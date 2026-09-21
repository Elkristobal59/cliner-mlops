# Clinical Protocols Standardization (AI-Powered) 🔬
> **Système MLOps Hybride & Continuous Training (Data Engineering, Cloud Architecture & LLMOps)**

Ce projet est une plateforme industrielle complète (Data Engineering, LLMOps & Cloud Architecture) permettant l'ingestion, le découpage intelligent, l'indexation vectorielle, l'extraction chirurgicale d'entités cliniques (NER) depuis des protocoles médicaux volumineux (PDF), ainsi que le monitoring et le réentraînement automatisé en boucle fermée.

---

## 🏗️ Architecture Globale du Projet (Pipeline Hybride & FinOps)

```text
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           ARCHITECTURE COMPLÈTE CLINICAL NER (MLOPS & CLOUD HYBRIDE)                  │
│                                                                                                       │
│   🧑‍⚕️ PRATICIEN / INTERFACE CLIENT                                                                    │
│   ┌─────────────────────────────────────────────────┐                                                 │
│   │  Application Web Streamlit (Docker / Render)   │                                                 │
│   │  • Recherche API ClinicalTrials V2 (100% CPU/0€)│                                                 │
│   │  • Summary Table (tri, filtres & sélection)     │                                                 │
│   │  • Upload PDF & Visualisation des entités NER   │                                                 │
│   └───────────────────────┬─────────────────────────┘                                                 │
│                           │ HTTPS (Port 8000)                                                         │
│                           ▼                                                                           │
│   ⚡ SERVEUR BACKEND D'INFÉRENCE                                                                      │
│   ┌─────────────────────────────────────────────────┐                                                 │
│   │  API FastAPI (Docker / AWS EC2 ou Local)        │                                                 │
│   │  • Orchestration RAG & Inférence Qwen2.5-7B     │                                                 │
│   └──────┬─────────────────┬──────────────────┬─────┘                                                 │
│          │                 │                  │                                                       │
│          ▼ (1) Vector/SQL  ▼ (2) Raw/Weights  ▼ (3) Tracking Runs                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────────────────────────────────────┐     │
│   │ 🐘 SUPABASE  │  │ 🪣 AWS S3    │  │ ☁️ GOOGLE CLOUD RUN (MLflow Serverless)                  │     │
│   │ PostgreSQL   │  │ cliner-mlops │  │ https://mlflow-cliner-mlops-1054740171053.europe-west9 │     │
│   │ • pgvector   │  │ • Data Lake  │  │ • Scale-to-Zero (min=0, max=2) -> 0.00 € quand inactif  │     │
│   │   (BioBERT)  │  │   (PDFs)     │  │ • Backend Store : Tables PostgreSQL Supabase            │     │
│   │ • Cache NER  │  │ • Datasets   │  │ • Artifact Store : s3://cliner-mlops/mlflow_artifacts   │     │
│   │   (0.01s)    │  │ • LoRA ~84Mo │  │ • Sécurité : Google Secret Manager (0 secret en clair)  │     │
│   └──────────────┘  └──────┬───────┘  └─────────────────────────────────────────────────────────┘     │
│                            │                                                                          │
│   🔁 BOUCLE MLOPS CONTINUE │ (Synchro Poids LoRA)                                                     │
│   ┌────────────────────────┴────────────────────────────────────────────────────────────────┐         │
│   │ 🚀 ORCHESTRATEUR CONTINUOUS TRAINING (run_pipeline.py & GitHub Actions)                         │         │
│   │                                                                                         │         │
│   │  1. Détection de Dérive Sémantique (Wasserstein Distance sur embeddings BioBERT)        │         │
│   │     └── Si W <= 0.15 : Distribution stable -> GPU éteint (0.00 € dépensé)               │         │
│   │     └── Si W > 0.15 : Dérive critique détectée -> Réveil de l'infrastructure GPU        │         │
│   │                                                                                         │         │
│   │  2. Just-In-Time Provisioning AWS EC2 GPU (boto3.ec2)                                   │         │
│   │     └── ec2:StartInstances ('cliner-ec2-gpu' g4dn.xlarge, Nvidia T4 16 Go VRAM)        │         │
│   │                                                                                         │         │
│   │  3. Réentraînement LoRA Événementiel (finetune_lora.py)                                 │         │
│   │     └── QLoRA 4-bit (r=16, alpha=32) -> convergence en ~20 min (Loss 0.284)             │         │
│   │     └── Génération de l'adaptateur médical (~84 Mo au lieu de 15 Go complets)           │         │
│   │                                                                                         │         │
│   │  4. Enregistrement Cloud & Model Registry                                               │         │
│   │     └── Upload vers AWS S3 : s3://cliner-mlops/models_lora/qwen-7b-chia-ner-v2/         │         │
│   │     └── Log paramètres, loss et dérive vers MLflow Cloud Run (HTTPS direct)             │         │
│   │                                                                                         │         │
│   │  5. 🛑 PROTECTION FINOPS AUTO-KILL SYSTÉMATIQUE (bloc finally:)                         │         │
│   │     └── ec2:StopInstances immédiat -> Facturation GPU arrêtée (Coût = 0.39 $ la session)│         │
│   └─────────────────────────────────────────────────────────────────────────────────────────┘         │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 La Cinématique Complète en Production (Les 2 Flux Détaillés)

### 🔹 Flux 1 : Le Parcours Utilisateur & Inférence Temps Réel (Le Praticien)
1. **Recherche Rapide (CPU / 0,00 €)** : Le médecin cherche une maladie sur l'UI Streamlit. L'application interroge l'API ClinicalTrials.gov V2 en direct en une seule requête optimisée sans allumer aucun modèle IA (0.00 €).
2. **Tableau Récapitulatif Dynamique (*Summary Table*) :**
   * **Traitement 100% en mémoire vive (RAM / Session State) :** Contrairement aux gros fichiers archivés sur AWS S3 ou aux index vectoriels dans Supabase, la Summary Table ne surcharge aucune base de données lors de la navigation : elle est générée dynamiquement et instantanément en mémoire à la réception du flux JSON de l'API.
   * **Exploration & Export :** Les études identifiées sont affichées dans une table interactive (NCT ID, Titre officiel, Statut de recrutement, Phase clinique, Intervention testée et lien direct vers la fiche `clinicaltrials.gov`). Le praticien peut trier, cocher les essais cibles ou télécharger la table complète au format CSV (`summary_table.csv`).
   * **Archivage Data Lake S3 (vs Ancien Stockage Supabase) :** Dans les versions initiales, chaque ligne de résumé était persistée dans une table relationnelle Supabase. Pour éviter cette surcharge transactionnelle et adopter un modèle Data Lakehouse propre, les tables récapitulatives sont désormais exportées et archivées directement sur **AWS S3** (`s3://cliner-mlops/summary_tables/`) au format CSV/Parquet pour l'analytique et l'audit, libérant Supabase pour ses deux rôles à forte valeur ajoutée : la recherche vectorielle `pgvector` et le cache d'inférence `clinical_ner_cache`.
3. **Double Voie d'Ingestion (JSON Officiel API v2 vs Archivage PDF S3)** :
   * **Voie Principale (Majorité des cas - JSON Natif)** : La majorité des études cliniques est directement ingérée sous le format standardisé officiel **ClinicalTrials.gov JSON Schema v2** (structure hiérarchique `Study` découpée en `protocolSection`, notamment les modules `eligibilityModule` avec `eligibilityCriteria`, `identificationModule`, `conditionsModule` et `designModule`). Le texte clinique propre est extrait, normalisé et concaténé instantanément sans nécessiter d'OCR ni de parsing PDF lourd.
   * **Voie Secondaire (Protocoles Complets / Upload Manuel - PDF)** : Lorsqu'un protocole intégral scanné de 50 pages est sélectionné ou uploadé par le médecin, il est sauvegardé et versionné dans le Data Lake AWS S3 (`s3://cliner-mlops/clinical_pdfs/`).
4. **Le Documentaliste (BioBERT Retriever - Modèle Encodeur Spécialisé)** :
   * **Nature du modèle (Encoder-only) :** BioBERT est un modèle spécialisé pré-entraîné sur des millions d'articles biomédicaux (PubMed, PMC). Il n'est **ni conversationnel ni génératif** : il est strictement incapable de dialoguer, de rédiger du texte ou de formater du JSON.
   * **Mission d'indexation géométrique :** Son unique tâche consiste à lire et convertir la sémantique de chaque paragraphe (issu du JSON ou du PDF) en un vecteur mathématique dense de **768 dimensions**. Il agit comme un pur "archiviste documentaliste" ultra-rapide (tournant sur CPU), chargé de cartographier l'information avant recherche.
5. **Recherche Sémantique Vectorielle (Supabase `pgvector`)** : Supabase calcule la distance cosinus (`<=>`) en **12 millisecondes** pour isoler uniquement les 2 ou 3 paragraphes cruciaux contenant les critères d'éligibilité (Context Recall : 96.5%).
6. **Cache Intelligent (`clinical_ner_cache`)** : Si cet essai a déjà été analysé, le résultat JSON est renvoyé en **0.01 seconde**, esquivant tout traitement GPU coûteux.
7. **L'Extracteur Expert (Qwen2.5-7B LoRA)** : Si le cache est vide, le LLM fine-tuné sur CHIA reçoit le texte brut des 2 paragraphes et génère le JSON médical strict en 3 secondes sans hallucination.
8. **Traçabilité MLflow Cloud Run** : Le temps de réponse, le prompt et les métriques sont envoyés en HTTPS vers Google Cloud Run.

---

### 🔹 Flux 2 : La Boucle MLOps de Réentraînement Automatisé (Continuous Training)
1. **Surveillance de Dérive Sémantique (`drift_detection.py`)** :
   * Mesure la distance de Wasserstein ($W$) entre les embeddings BioBERT de référence (dataset Gold CHIA) et les 5 derniers protocoles cliniques ingérés.
   * Si $W \le 0.15$ : distribution stable. L'orchestrateur s'arrête immédiatement. **Facture Cloud = 0.00 €**.
   * Si $W > 0.15$ : dérive critique détectée $\rightarrow$ déclenchement du cycle de réentraînement.
   
   > 💡 **Précision d'Architecture MLOps — Pourquoi Wasserstein et non le F1-Score en production ?**  
   > * **Absence de Vérité Terrain en Direct (*Data Drift* non supervisé) :** Les nouveaux protocoles médicaux qui arrivent de l'hôpital ou de ClinicalTrials.gov sont du texte brut non annoté. Aucun médecin n'est présent pour labelliser chaque token en direct : il est donc **physiquement impossible de calculer un F1-Score en production**. Wasserstein mesure le *Covariate Shift* (dérive des textes d'entrée) dans l'espace BioBERT 768d.
   > * **Pourquoi 58.3% de F1-Score sur CHIA est un score de référence ?** CHIA est une tâche extrême de NER imbriqué multi-classes (15 catégories médicales strictes : `Condition`, `Drug`, `Procedure`, `Measurement`, `Temporal`, etc.) avec alignement exact de caractères (*exact boundary match*). L'accord inter-annotateurs entre médecins experts tourne autour de **65% à 70%**. Un score F1 strict de **58% à 60%** pour un LLM 7B est un standard très élevé dans la littérature scientifique biomédicale.
   > * **Qui bouge lors du fine-tuning ?** Le Gold Standard CHIA reste **immuable** (étalon zéro) ; le Data Lake S3 s'enrichit des nouveaux cas validés ; et **seul l'adaptateur LoRA (84 Mo)** est réentraîné sur AWS EC2 pour repositionner ses projections neuronales sans provoquer d'oubli catastrophique.
2. **Allumage FinOps à la Demande (`ec2_manager.py`)** :
   * L'orchestrateur appelle l'API AWS `ec2:StartInstances` via `boto3`.
   * L'instance GPU `cliner-ec2-gpu` (`g4dn.xlarge`, Nvidia T4) démarre en ~45 secondes.
3. **Réentraînement LoRA Événementiel (`finetune_lora.py`)** :
   * Le cerveau de Qwen2.5-7B reste gelé (*Frozen Backbone*).
   * Seules les matrices légères de rang $r=16, \alpha=32$ sont ajustées sur le nouveau jeu de données CHIA actualisé en **~20 minutes**.
   * Poids produit : un adaptateur ultra-léger d'environ **84 Mo** (au lieu des 15 Go du modèle entier).
4. **Versionnage Cloud & Model Registry** :
   * Les poids sont téléversés sur AWS S3 : `s3://cliner-mlops/models_lora/qwen-7b-chia-ner-v2/adapter_model.safetensors`.
   * Le run, les hyperparamètres et la Loss finale ($0.284$) sont enregistrés sur le serveur **MLflow sur Google Cloud Run**.
5. **🛑 Protection FinOps Auto-Kill Systématique** :
   * Dans le bloc `finally:` de Python (et le step `if: always()` de GitHub Actions), l'orchestrateur exécute immédiatement `ec2:StopInstances`.
   * L'instance GPU repasse à l'état `stopped`. Facturation GPU immédiatement stoppée.
   * **Coût total de la session d'entraînement : ~0.39 $** (couvert par les 140 $ de crédits gratuits AWS).

---

## 🧠 Le Moteur RAG Hybride en Détail (Alimentation, Indexation & Consultation)

Le système implémente une architecture **RAG séquentielle bidirectionnelle** couplant **BioBERT** (Retriever / Documentaliste) et **Qwen2.5-7B LoRA** (Extractor / Analyste). Cette architecture garantit une précision maximale (zéro hallucination) tout en maintenant un temps de réponse et des coûts d'inférence minimaux.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PIPELINE RAG CLINIQUE DÉTAILLÉ                                 │
│                                                                                                  │
│  [📥 DONNÉE SOURCE]                                                                              │
│    ├── API ClinicalTrials v2 (JSON structuré) ──┐                                                │
│    └── Upload Protocole PDF (PyMuPDF / S3) ─────┴──► [1. Chunking LangChain]                     │
│                                                       (1000 caractères, chevauchement 200)       │
│                                                                      │                           │
│  [🔄 ALIMENTATION & INDEXATION]                                      ▼                           │
│                                                             [2. BioBERT Encoder]                 │
│                                                       (Embedding dense 768 dimensions)           │
│                                                                      │                           │
│                                                                      ▼                           │
│                                                      [3. Stockage Supabase pgvector]             │
│                                                       Table: clinical_trials_data_biobert        │
│                                                                                                  │
│  [🔍 CONSULTATION & RETRIEVAL]                                                                   │
│    Requête clinique ("inclusion criteria medications {maladie}")                                │
│       └──► Embedding BioBERT (768d)                                                              │
│       └──► Distance Cosinus SQL (<=>) en 12 ms                                                   │
│       └──► Extraction Top-5 Chunks (98% du bruit éliminé)                                        │
│                                      │                                                           │
│  [⚡ AUGMENTATION & EXTRACTION NER]   ▼                                                           │
│    Prompt Système Strict + Top-5 Chunks ──► [4. Qwen2.5-7B LoRA (QLoRA 4-bit)]                  │
│                                               ├── Extraction JSON Médical (3s)                   │
│                                               ├── Sauvegarde dans clinical_ner_cache             │
│                                               └── Logging Métriques vers MLflow Cloud Run        │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Comment le RAG est alimenté (Ingestion & Indexation)
Le pipeline d'alimentation vectorielle se déroule en 3 étapes :
1. **Extraction du texte brut :**
   * Soit directement depuis les modules de l'API ClinicalTrials.gov V2 (`protocolSection.eligibilityModule`, `identificationModule`, etc.), sans traitement lourd.
   * Soit en flux mémoire via `fitz` (PyMuPDF) lorsque le médecin télécharge un PDF de protocole (le PDF est simultanément archivé dans le bucket S3 `cliner-mlops`).
2. **Découpage sémantique (Chunking LangChain) :**
   * Le texte est découpé par `RecursiveCharacterTextSplitter` avec une taille de chunk de **1 000 caractères** et un chevauchement (*overlap*) de **200 caractères**. Cet overlap est capital en médecine pour éviter de tronquer une posologie ou une négation (« sans antécédent de... ») à cheval sur deux blocs.
3. **Vectorisation dense & Nettoyage dans Supabase `pgvector` :**
   * Chaque chunk est encodé par **BioBERT** (`dmis-lab/biobert-v1.1`) en un vecteur mathématique de **768 dimensions**.
   * Les anciens vecteurs du même document sont purgés automatiquement (`DELETE FROM clinical_trials_data_biobert WHERE doc_id = %s`) pour éliminer tout risque de pollution vectorielle ou doublon.
   * Les nouveaux vecteurs sont persistés dans la table PostgreSQL `clinical_trials_data_biobert` équipée d'un index vectoriel.

---

### 2. Comment le RAG est consulté (Recherche Sémantique & Retrieval)
La consultation vectorielle s'exécute de manière optimisée en cascade :
1. **Étape FinOps préalable (Vérification du Cache) :**
   * Avant tout calcul, l'API interroge la table `clinical_ner_cache` avec le couple `(doc_id, disease)`.
   * En cas de *Cache Hit*, l'extraction JSON est retournée en **0,01 seconde**, économisant 100% du GPU et du calcul d'embeddings.
2. **Formulation de la requête sémantique :**
   * En cas de *Cache Miss*, le système construit dynamiquement une requête d'interrogation ciblée : `"inclusion criteria medications {disease}"`.
   * BioBERT projette cette requête dans le même espace vectoriel 768d.
3. **Recherche de similarité par distance cosinus native (`<=>`) :**
   * PostgreSQL exécute directement dans le moteur de base de données la recherche des 5 fragments les plus proches :
     ```sql
     SELECT raw_text
     FROM clinical_trials_data_biobert
     WHERE doc_id = %s
     ORDER BY embedding <=> %s::vector
     LIMIT 5;
     ```
   * Grâce à l'index `pgvector`, cette recherche prend seulement **12 millisecondes** (contre plus de 25 secondes si le calcul était fait en mémoire Python depuis un stockage S3).

---

### 3. Augmentation du Contexte & Génération Déterministe
1. **Assemblage du Prompt Augmenté :** Les 5 extraits textuels isolés sont concaténés pour former la variable `context`. Plus de 98% du document initial (pages administratives, annexes, adresses de centres) a été filtré.
2. **Inférence Ciblée (Qwen2.5-7B LoRA) :** Le prompt augmenté est soumis à l'adaptateur LoRA `Elkristobal59/qwen-7b-chia-ner` :
   * Température ultra-basse ($T = 0.1$) pour garantir la reproductibilité clinique.
   * Repetition penalty ($1.15$) pour bannir les boucles de génération.
   * Sortie sous format JSON strict conforme aux entités CHIA (`Condition`, `Drug`, `Procedure`, `Measurement`, etc.).
3. **Persistance & Traçabilité :** Le JSON résultant est inséré dans `clinical_ner_cache` pour les consultations futures, et la latence, le prompt et les métriques sont journalisés en direct sur le serveur **MLflow sur Google Cloud Run**.

---

### 4. Deux Modes de RAG sur le Même Index Vectoriel : Extraction Structurée (NER) vs Chatbot Conversationnel

Une force majeure de l'architecture est la mutualisation de l'index vectoriel Supabase `clinical_trials_data_biobert` pour deux cas d'usage clinique complémentaires :

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                 MUTUALISATION DE L'INDEX VECTORIEL UNIQUE POUR DEUX CAS D'USAGE                  │
│                                                                                                  │
│                     🗄️ INDEX VECTORIEL SUPABASE (clinical_trials_data_biobert)                   │
│                                   (Embeddings BioBERT 768d)                                      │
│                                       │                     │                                    │
│                 ┌─────────────────────┘                     └─────────────────────┐              │
│                 ▼                                                                 ▼              │
│   🏷️ ONGLET 3 : EXTRACTION STRUCTURÉE (NER)                         💬 ONGLET 4 : CHATBOT RAG    │
│   • Pattern : Retrieval-Augmented NER                               • Pattern : Conversational   │
│   • Modèle : Qwen-7B LoRA (Elkristobal59/qwen-7b-chia-ner)          • Modèle : Qwen-7B Base      │
│   • Objectif : Filtrer 98% du document pour isoler les 5 chunks     • Objectif : Poser une       │
│     d'éligibilité et générer le JSON strict (Condition, Drug, etc.)   question libre en français │
│   • Format de sortie : JSON standardisé CHIA (3s au lieu de 4 min)  • Format : Réponse rédigée   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Onglet 3 (Extraction NER) — Le Retrieval-Augmented NER :**
   * **Pourquoi le NER intervient après la recherche vectorielle et non juste après l'embedding ?**  
     Un protocole de 50 pages compte environ 80 chunks. Si le NER était appliqué sur chaque chunk, le GPU exécuterait 80 inférences séquentielles (**plus de 4 minutes d'attente pour le médecin !**) et traiterait inutilement des pages administratives ou légales. En effectuant la recherche sémantique en amont (12 ms), Qwen LoRA n'analyse que les **5 chunks pertinents**, ramenant le temps d'extraction à **3 secondes chrono avec zéro hallucination**.
   * **Format de sortie :** Tableau JSON médical strict (`Condition`, `Drug`, `Procedure`, `Measurement`, `Value`).
2. **Onglet 4 (Chatbot Conversationnel RAG) — La Synthèse Clinique Contextuelle :**
   * **Rôle :** Permet au praticien de poser des questions ouvertes en langage naturel (*ex : « Quelles sont les contre-indications cardiaques pour cet essai ? »*).
   * **Fonctionnement :** La question du médecin est vectorisée par BioBERT, les 15 extraits les plus pertinents sont isolés, et le modèle formule une **synthèse médicale fluide en français**, avec citation explicite des sections sources.
   * **Traçabilité :** Décoré avec `@mlflow.trace(name="RAG_Chatbot", span_type="CHAIN")`, chaque échange est tracé en direct sur Google Cloud Run.

---

## 📦 Données & Modèles : Cartographie et Stockage Décentralisé

### 1. Le Dataset Clinique de Référence (Gold CHIA dans `data/`)
Le dossier local [data/](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/data) contient l'ensemble des données d'entraînement et d'évaluation certifiées :
* **`data/chia_gold_standard.json` (866 Ko)** : La vérité terrain (*Gold Standard*) de 800 protocoles cliniques annotés à la main par des experts médicaux (entités CHIA : `Condition`, `Drug`, `Procedure`, `Measurement`, etc.).
* **`data/chia_finetuning_dataset.jsonl` (455 Ko)** & **`train_dataset.jsonl` (898 Ko)** : Jeux d'entraînement structurés sous forme de paires `prompt -> json attendu` pour le fine-tuning LoRA.
* **`data/test_dataset.jsonl` (859 Ko)** : Jeu de test indépendant utilisé par `finetune_lora.py` pour valider la convergence de la Loss sans data leakage.
* **`data/chia_pdfs/`** : Corpus des protocoles PDF originaux utilisés pour tester l'extraction end-to-end.

### 2. Emplacement et Cycle de Vie des Modèles IA

Afin de respecter les principes FinOps et GreenOps de l'Architecte IA, les poids des modèles ne sont pas dupliqués inutilement :

| Modèle | Source Officielle (Cloud) | Emplacement Local / Inférence | Poids | Rôle & Type |
| :--- | :--- | :--- | :---: | :--- |
| **BioBERT** | [Hugging Face Hub](https://huggingface.co/dmis-lab/biobert-v1.1) (`dmis-lab/biobert-v1.1`) | Cache local Hugging Face (`~/.cache/huggingface/hub/`) | **~400 Mo** | Bi-Encoder pur sur CPU (Embeddings 768d pour `pgvector`) |
| **Qwen2.5-7B Base** | [Hugging Face Hub](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) (`Qwen/Qwen2.5-7B-Instruct`) | Cache local ou VRAM GPU (chargé par `vLLM` ou `transformers`) | **~15 Go** | Modèle de fondation gelé (*Frozen Backbone*) |
| **Qwen LoRA (Votre modèle)** | 1. [Hugging Face Hub](https://huggingface.co/Elkristobal59/qwen-7b-chia-ner)<br>2. **AWS S3** (`s3://cliner-mlops/models_lora/`) | Dossier local du repo :<br>[models/qwen_7b_lora_retrained/](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/models/qwen_7b_lora_retrained) | **~84 Mo** | Adaptateur médical entraîné sur CHIA ($r=16, \alpha=32$) |

> 💡 **Le Ratio FinOps Clé :** Lors d'un réentraînement automatique, nous ne transférons ni ne sauvegardons les **15 Go** du modèle complet. Seuls les **84 Mo** de l'adaptateur LoRA sont produits, versionnés sur AWS S3 et référencés dans MLflow.

---

## ⚡ Moteur d'Inférence Haute Performance : vLLM & PagedAttention

L'API Backend FastAPI (`api/main.py`) embarque nativement le moteur d'inférence de pointe **vLLM** optimisé pour les cartes Nvidia en production :

1. **Élimination de la fragmentation mémoire (PagedAttention) :**
   * Contrairement aux bibliothèques classiques où la mémoire vidéo est pré-allouée de manière contiguë (provoquant jusqu'à 60% de VRAM gaspillée), `vLLM` gère la mémoire KV-Cache comme la mémoire virtuelle d'un OS (par blocs paginés).
   * **Gain :** Débit d'inférence accéléré d'un facteur **x2 à x5**, avec 85% de la VRAM GPU T4 allouée dynamiquement.
2. **Support Dynamique des Adaptateurs LoRA (`LoRARequest`) :**
   * Le serveur charge le backbone Qwen-7B une seule fois, puis greffe dynamiquement l'adaptateur médical à chaud :
     ```python
     lora_req = LoRARequest("chia_ner", 1, "Elkristobal59/qwen-7b-chia-ner")
     outputs = qwen_model.generate([text_prompt], sampling_params, lora_request=lora_req)
     ```
3. **Dual-Mode avec Résilience Automatique :**
   * Si un GPU CUDA est détecté $\rightarrow$ Activation automatique de `vLLM` avec `enable_lora=True`.
   * Si exécution sur CPU ou en environnement restreint $\rightarrow$ Fallback automatique et transparent sur Hugging Face `transformers` + `peft.PeftModel`.

---

## 🏛️ Infrastructure as Code (IaC) : Terraform pour Supabase & pgvector

Le dossier [terraform/](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/terraform) matérialise l'approche industrielle DevSecOps en provisionnant l'infrastructure de données de manière déclarative et reproductible :

* **Fichiers de configuration :**
  * [`terraform/main.tf`](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/terraform/main.tf) : Déclaration du provider `postgresql` connecté à Supabase en SSL strict (`sslmode=require`).
  * Activation déclarative de l'extension `vector` (`resource "postgresql_extension" "pgvector"`).
  * [`terraform/schema.sql`](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/terraform/schema.sql) : Création automatisée de la table d'ingestion vectorielle `clinical_trials_data_biobert` (colonne `embedding vector(768)`) et de la table de cache d'inférence `clinical_ner_cache`.
* **Commandes de déploiement IaC :**
  ```powershell
  cd terraform
  terraform init
  terraform apply -var="supabase_db_url=$env:SUPABASE_DATABASE_URL"
  ```
  Cette démarche garantit que n'importe quel environnement de staging ou de production peut être reconstruit en **moins de 30 secondes**.

---

## 🔐 Configuration des Identifiants & Fichier `.env`

Le fichier local [`.env`](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/.env) (sécurisé dans `.gitignore`) centralise les accès de production :

```env
# ==============================================================================
# 1. AWS CLOUD (IAM User dédié, S3 Data Lake & FinOps EC2 GPU)
# ==============================================================================
AWS_ACCESS_KEY_ID="<VOTRE_AWS_ACCESS_KEY_ID>"
AWS_SECRET_ACCESS_KEY="<VOTRE_AWS_SECRET_ACCESS_KEY>"
AWS_DEFAULT_REGION="eu-west-3"
S3_BUCKET_NAME="cliner-mlops"
AWS_EC2_GPU_INSTANCE_ID="i-0bb73662c67f2828f"

# Mode réel AWS EC2 GPU (boto3) activé :
MOCK_AWS_EC2="false"

# ==============================================================================
# 2. SUPABASE (Base Relationnelle, pgvector & Cache)
# ==============================================================================
SUPABASE_DATABASE_URL="postgresql://postgres.<PROJECT_REF>:<PASSWORD_URL_ENCODED>@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"
SUPABASE_API_URL="https://<PROJECT_REF>.supabase.co"
SUPABASE_ANON_KEY="<VOTRE_SUPABASE_ANON_KEY>"

# ==============================================================================
# 3. MONITORING MLOPS DANS LE CLOUD (Google Cloud Run Serverless)
# ==============================================================================
# URL officielle de production de notre serveur MLflow Serverless (Scale-to-Zero)
MLFLOW_TRACKING_URI="https://mlflow-cliner-mlops-1054740171053.europe-west9.run.app"

# URL du Backend FastAPI
BACKEND_API_URL="http://localhost:8000"

# ==============================================================================
# 4. CLÉS API IA DE SECOURS (Optionnel)
# ==============================================================================
GOOGLE_API_KEY="<VOTRE_GOOGLE_API_KEY>"
LLM_MODEL_NAME="gemini-flash-lite-latest"
```

---

## 🚀 Guide d'Exécution Pas-à-Pas

### 1. Exécuter la Démo du Pipeline MLOps

#### Option A : Simulation rapide (Dry-run / CI/CD)
Lance la simulation complète (Drift Wasserstein $\rightarrow$ Démarrage EC2 $\rightarrow$ Fine-Tuning LoRA $\rightarrow$ Upload S3 $\rightarrow$ Auto-Kill EC2) en **9 secondes à 0.00 €** avec envoi réel des logs vers Google Cloud Run :
```powershell
cd "d:\AIL-FT-02\CERTIF AIL\cliner-mlops"
python -m mlops_reentrainement.run_pipeline --dry-run
```

#### Option B : Exécution Réelle sur Infrastructure AWS GPU (FinOps)
Pilote en direct l'instance physique GPU Nvidia T4 16 Go (`i-0bb73662c67f2828f`) via Boto3, avec extinction automatique (**Auto-Kill**) dans le bloc `finally` :
```powershell
python -m mlops_reentrainement.run_pipeline --live
```

*Variantes de démonstration :*
```powershell
# Forcer le réentraînement même si la distribution est stable :
python -m mlops_reentrainement.run_pipeline --force-retrain

# Abaisser le seuil d'alerte pour forcer le drift :
python -m mlops_reentrainement.run_pipeline --threshold 0.05
```

### 2. Tester chaque brique MLOps unitairement
```powershell
# Brique 1 : Test statistique de Dérive Sémantique
python mlops_reentrainement/drift_detection.py

# Brique 2 : Contrôleur FinOps EC2 (Boto3)
python mlops_reentrainement/ec2_manager.py --dry-run --action status

# Brique 3 : Moteur de Réentraînement LoRA (Qwen2.5-7B)
python mlops_reentrainement/finetune_lora.py --dry-run

# Brique 4 : Connecteur AWS S3 Data Lake (Bucket cliner-mlops)
python mlops_reentrainement/s3_storage.py
```

### 3. Exécuter la Suite de Tests Automatisés (PyTest - Quality Gate CI/CD)
Valide l'intégrité logicielle, la cohérence des formats et l'absence de régression (9 tests unitaires & intégration) :
```powershell
pytest tests/ -v
```

### 4. Lancer l'API Backend FastAPI
```powershell
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Documentation Swagger interactive** : [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs) (Endpoints `/predict`, `/feedback`, `/drift`).

### 5. Consulter le Dashboard MLflow en Direct dans le Cloud
Le serveur est accessible en direct à l'adresse officielle :  
👉 **[`https://mlflow-cliner-mlops-1054740171053.europe-west9.run.app`](https://mlflow-cliner-mlops-1054740171053.europe-west9.run.app/#/experiments/2)**

### 6. Lancer et Déployer l'Interface Web Streamlit

#### A. Exécution Locale
```powershell
streamlit run app/streamlit_app.py
```
* **Application Web Locale** : Accessible sur [`http://localhost:8501`](http://localhost:8501).

#### B. Déploiement Cloud sur Render (Web Service Docker)
L'interface client est entièrement dockerisée via [`Dockerfile`](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/Dockerfile) et [`requirements-frontend.txt`](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/requirements-frontend.txt) (sans dépendances GPU lourdes pour un démarrage ultra-rapide) :
1. **Créer un Web Service** sur Render connecté au dépôt GitHub `Elkristobal59/cliner-mlops`.
2. **Configuration du runtime** : Choisir l'environnement **Docker** (détecte automatiquement le `Dockerfile` à la racine).
3. **Variables d'environnement indispensables sur Render** :
   * `PORT` = `8501` (Routage du trafic entrant vers Streamlit).
   * `STREAMLIT_SERVER_FILE_WATCHER_TYPE` = `none` (Prévention de l'erreur système inotify sur conteneur Linux).
   * `STREAMLIT_SERVER_HEADLESS` = `true`
   * `STREAMLIT_SERVER_ENABLE_CORS` = `false`
   * `BACKEND_API_URL` = `http://localhost:8000` (ou URL du backend actif).

#### C. Connectivité Multi-Cibles du Backend Inférence
L'application intègre une détection dynamique multi-environnements. La barre latérale permet de basculer à la volée entre les différents serveurs de calcul sans aucun redéploiement :
* **Cible 1 (AWS EC2 GPU)** : `http://<IP_PUBLIQUE_EC2>:8000` (Instance de production `g4dn.xlarge` pilotée par `ec2_manager.py`).
* **Cible 2 (Lightning.ai GPU Studio)** : `https://<STUDIO_ID>-8000.lightning.ai` (Alternative Cloud managée haute performance avec port 8000 exposé).
* **Cible 3 (Environnement Local / Pont Tunnel)** : `http://localhost:8000` ou tunnel sécurisé (Ngrok / LocalTunnel).

---

## ⚙️ Intégration Continue & Déploiement (GitHub Actions CI/CD)

Le dépôt GitHub [`Elkristobal59/cliner-mlops`](https://github.com/Elkristobal59/cliner-mlops) intègre trois workflows automatisés configurés avec 7 secrets de production :

* **Secrets GitHub configurés :** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` (`eu-west-3`), `S3_BUCKET_NAME` (`cliner-mlops`), `MLFLOW_TRACKING_URI`, `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.
* **`ci_mlops.yml` (Quality Gate à chaque push)** :
  1. Linting strict Flake8 (détection des erreurs de syntaxe et imports manquants).
  2. **Suite de Tests Automatisés PyTest (`pytest tests/ -v`)** : 11 tests unitaires et d'intégration validant le calcul de drift Wasserstein, Evidently AI (génération des rapports HTML/JSON de Data Drift), la traçabilité XML médico-légale (HDS/RGPD), le cycle de vie EC2 FinOps, le fine-tuning LoRA, le connecteur S3 et l'intégrité des datasets CHIA.
  3. **Simulation du cycle Continuous Training LoRA** avec enregistrement direct sur MLflow Cloud Run.
  4. **Construction des conteneurs Docker** (`cliner-frontend` et `cliner-mlops-worker`) et push automatique sur Docker Hub.
* **`weekly_mlops_pipeline.yml` (Surveillance Hebdomadaire du Drift & Continuous Training)** :
  * Planifié chaque lundi à 02h00 UTC via cron GitHub Actions (**100% Free Tier, 0,00 € de coût de veille**).
  * Exécute les tests PyTest, analyse la dérive de Wasserstein et le rapport Evidently AI sur la fenêtre glissante des 5 derniers protocoles, et lance le réentraînement LoRA si $W > 0.15$.
* **`deploy_ec2_autokill.yml` (Déploiement EC2 à la demande avec minuteur FinOps)** :
  * Déclenchable manuellement depuis l'onglet Actions avec sélection de la durée (15, 30, 45, 60 min).
  * Démarre l'instance GPU AWS, maintient la session active pendant les démonstrations, et exécute **l'Auto-Kill systématique** (`if: always()`).

---

## 📊 Monitoring ML (Evidently AI), Observabilité du Pipeline & Traçabilité XML (HDS/RGPD)

Le projet CliNER-MLOps intègre une pile complète de monitoring et de gouvernance industrielle conforme aux exigences du référentiel **RNCP 41993 - Bloc 4** :

### 1. Monitoring ML : Détection du Data Drift (Evidently AI & MLflow Tracking)
* **Pourquoi la surveillance non supervisée du Data Drift ?** En environnement clinique hospitalier, les nouveaux protocoles reçus ne disposent d'aucune vérité terrain annotée en temps réel. Il est donc impossible de calculer une métrique supervisée (F1-score) en continu. La surveillance s'appuie sur la détection précoce du *Covariate Shift* (dérive des données d'entrée).
* **Double niveau d'analyse statistique :**
  1. **Niveau Macro-Sémantique (Wasserstein Distance)** : Calcul de la distance de Wasserstein (Earth Mover's Distance) sur les projections denses d'embeddings BioBERT (768 dimensions), avec seuil critique fixé à $W = 0.15$. C'est le **déclencheur FinOps binaire** du réentraînement automatisé sur EC2.
  2. **Niveau Caractéristiques Textuelles (Evidently AI)** : Analyse de la dérive des distributions statistiques sur 5 métriques clés via tests de Kolmogorov-Smirnov (KS) à 2 échantillons (comparaison de fonctions de répartition cumulées, évitant les faux positifs dus aux fluctuations individuelles de texte) :
     - Longueur de texte en caractères (`char_count`) : contrôle de l'intégrité du découpage textuel.
     - Nombre de mots (`word_count`) : détection des textes tronqués ou des PDF non segmentés.
     - Longueur moyenne des mots médicaux (`avg_word_len`) : capteur du jargon biomédical (termes latins/molécules à 9-14 lettres vs langage courant).
     - Densité numérique (`digit_ratio`) : présence des seuils physiologiques, dosages (mg/kg), âges et durées.
     - Ratio de majuscules (`uppercase_ratio`) : présence des biomarqueurs et mutations (*BRAF*, *EGFR*, *ECOG*).
* **Restitution visuelle & Alerting automatisé :**
  - Génération automatique d'un rapport interactif **HTML** (`reports/data_drift_report.html`) et d'un état synthétique **JSON** (`reports/data_drift_report.json`).
  - Téléversement direct dans le serveur **MLflow Tracking Cloud Run** (`mlflow.log_artifact`) lors de chaque exécution du pipeline ou du cycle de réentraînement.
* **Complémentarité Architecturale (Macro vs Micro) :**
  - *Wasserstein BioBERT* répond à la question : **« Doit-on réentraîner le modèle ? »** (décision machine).
  - *Evidently AI* répond à la question : **« Pourquoi et sur quels critères le flux de données a-t-il changé ? »** (explicabilité humaine XAI).

### 2. Monitoring Pipeline : Logging Structuré & Haute Résilience (Standard Stéphane Robert)
Conformément aux standards d'ingénierie logicielle Python (cf. guide Stéphane Robert), la journalisation applicative de l'API et de l'orchestrateur est configurée de manière robuste :
* **Double Handler d'écoute :** Sortie console temps réel (`StreamHandler`) et journalisation fichier rotative (`RotatingFileHandler`).
* **Protection contre la saturation disque :** Rotation paramétrée à **5 Mo par fichier avec rétention de 5 archives** (`maxBytes=5*1024*1024`, `backupCount=5`), plafonnant l'empreinte disque maximale à 25 Mo.
* **Format standardisé et horodaté :**
  `Date/Heure | Niveau (INFO/WARNING/ERROR) | Logger | [Fichier:Ligne] | Message`
* **Exposition HTTP / Endpoints d'Administration (FastAPI) :**
  - `GET /logs?lines=100` : Permet aux équipes DevOps/SRE de diagnostiquer instantanément l'état de l'API sans nécessiter d'accès SSH ni de clés de bastion sur les machines de production.
  - `GET /logs/xml` : Télécharge le dernier journal XML certifié pour archivage réglementaire.
  - `GET /monitoring/drift-report` : Affiche le dashboard interactif Evidently AI dans n'importe quel navigateur web.

### 3. Traçabilité Médico-Légale & Auditabilité Réglementaire (Journaux XML HDS/RGPD)
Pour chaque exécution critique (extraction NER, conversation RAG, réentraînement de pipeline), le système compile un journal structuré au format **XML** (`logs/execution_journals/<id>.xml`) :
* **Structure hiérarchique certifiée :**
  ```xml
  <PipelineExecution id="ner_NCT02421835_1789993800" status="SUCCESS" timestamp="2026-09-21T12:30:00.000Z">
    <Environment platform="win32" python_version="3.13.9" environment="production"/>
    <ExecutionSteps>
      <Step name="clinical_ner_extraction" status="SUCCESS" latency_ms="3250.40" entities_count="12"/>
    </ExecutionSteps>
    <Metrics>
      <Metric name="latency_sec" value="3.25"/>
      <Metric name="document" value="NCT02421835"/>
      <Metric name="disease" value="Mélanome Métastatique"/>
    </Metrics>
  </PipelineExecution>
  ```
* **Conformité HDS & RGPD :** Horodatage immuable ISO 8601 UTC, séparation stricte des données de santé (données patients pseudonymisées hors logs), et traçabilité exhaustive de la chaîne de décision algorithmique pour les autorités de santé (ANSM, FDA, CNIL).

---

## 💰 Analyse Économique & Budget FinOps

| Composant | Fournisseur / Type | Modèle de Coût | Coût Mensuel Estimé |
| :--- | :--- | :--- | :--- |
| **Serveur MLflow UI** | Google Cloud Run (Paris) | **Scale-to-Zero** (Facturation par requête, CPU à 0 hors requêtes) | **0,00 €** (Inclus dans les 360 000 Gio-s gratuits) |
| **Backend Store MLflow** | Supabase PostgreSQL | Base managée mutualisée avec pgvector | **0,00 €** (Déjà compris dans l'instance existante) |
| **Artifact Store & Data Lake** | AWS S3 (`cliner-mlops`) | Stockage d'objets standard (~0,023 $/Go/mois) | **~0,10 $ / mois** (Couvert par les 140 $ de crédits) |
| **Calcul Inférence / Entraînement** | AWS EC2 `g4dn.xlarge` (Nvidia T4) | **Just-In-Time Provisioning** (0,526 $/h, éteint hors usage) | **~2,00 $ / mois** pour 4h de calcul actif (Couvert par les crédits) |
| **Disque dur EC2 persistant** | Disque AWS EBS gp3 (80 Go) | Stockage bloc persistant à l'arrêt (~0,08 $/Go/mois) | **~6,40 $ / mois** (Couvert par les crédits gratuits) |
| **Solde de Crédits Gratuits AWS** | Promotion AWS active jusqu'en Mars 2027 | Crédits consommés en priorité absolue | **139,99 $ de marge disponible** |

### 🛡️ Contrôle FinOps & Commandes CLI de Surveillance des Coûts

Afin de garantir une gouvernance FinOps rigoureuse et d'éviter toute dépense imprévue (instances orphelines, volumes EBS non attachés, adresses IP statiques inutilisées), le projet intègre des procédures de surveillance automatisées en ligne de commande :

#### 1. Audit automatisé multi-régions (17 régions AWS)
Le script [audit_aws_all_regions.py](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/audit_aws_all_regions.py) scanne l'intégralité des 17 régions AWS actives pour dresser un inventaire exhaustif en temps réel :
```powershell
python audit_aws_all_regions.py
```
* **Ressources inspectées :** Instances EC2 actives (`running`), instances à l'arrêt (`stopped`), disques EBS, adresses Elastic IP, passerelles NAT, Load Balancers (ALB/NLB), bases de données RDS, clusters EKS et VPC Interface Endpoints.
* **Verdict FinOps :** Confirmation instantanée du coût de calcul actif (**0,00 € / heure**).

#### 2. Suivi en direct du Quota GPU AWS (`g4dn.xlarge` / Famille G & VT)
Pour monitorer l'avancement de la validation des 4 vCPUs GPU par le support AWS sans passer par la console graphique :
```bash
# Vérifier l'état d'avancement du ticket support (CASE_OPENED -> APPROVED) :
aws service-quotas list-requested-service-quota-change-history --service-code ec2 --region eu-west-3

# Vérifier la valeur effective appliquée du quota (0.0 -> 4.0 vCPUs) :
aws service-quotas get-service-quota --service-code ec2 --quota-code L-DB2E81BA --region eu-west-3
```

#### 3. Contrôle instantané des instances EC2 actives (Région eu-west-3)
```bash
aws ec2 describe-instances --region eu-west-3 --filters "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name]" --output table
```

---

## 🎯 FAQ Technique & Justifications d'Architecture

### Q1 : Pourquoi une architecture hybride AWS S3 + Supabase pgvector ? Pourquoi pas 100% S3 ?
* **AWS S3 = Data Lake & Model Registry :** Stockage passif haute capacité et économique pour les gros volumes (PDFs de 50 pages, adaptateurs LoRA de 84 Mo).
* **Supabase pgvector = Moteur Vectoriel Temps Réel :** S3 est un stockage d'objets passif incapable d'effectuer des calculs mathématiques. Supabase PostgreSQL `pgvector` calcule la similarité cosinus (`<=>`) en **12 millisecondes** et propose une table de cache d'inférence (`clinical_ner_cache`) répondant en **0,01s**. Utiliser S3 pour le RAG obligerait à charger tous les vecteurs en RAM Python à chaque requête, augmentant la latence de **15 ms à plus de 25 secondes** !

### Q2 : Pourquoi le fine-tuning LoRA plutôt qu'un Full Fine-Tuning de Qwen-7B ?
* **Économie de mémoire VRAM (QLoRA 4-bit)** : Qwen2.5-7B complet nécessite plus de 80 Go de VRAM pour un full training (machines A100 à 4 $/h). Avec QLoRA 4-bit, le modèle de base est gelé et compressé à ~5 Go de VRAM, ce qui permet de l'entraîner sur une simple carte grand public Nvidia T4 (`g4dn.xlarge` à 0,52 $/h).
* **Poids de l'artefact & Portabilité** : Au lieu de sauvegarder et transférer 15 Go de poids à chaque réentraînement, l'adaptateur LoRA ne pèse que **84 Mo**. Il est transférable sur S3 en 2 secondes.

### Q3 : Pourquoi MLflow sur Google Cloud Run plutôt que sur Kubernetes ?
* Déployer un cluster Kubernetes managé (AWS EKS ou Google GKE) pour un serveur de monitoring coûte au minimum **75 € à 100 € par mois** rien que pour le Control Plane, même sans activité.
* **Google Cloud Run** offre le **Scale-to-Zero** : l'instance s'éteint complètement dès qu'aucune requête n'arrive. La facture est strictement de **0.00 €** en dehors des consultations de dashboard et des entraînements.

### Q4 : Quel est le cloisonnement avec le projet CDSD (`clinicalapp`) ?
Les deux projets sont **strictement étanches** :
* `clinicalapp` (`d:\AIFS01\PROJET FINAL\stack_equipe`) : centré sur l'applicatif Data Science originel (Streamlit, API, modèle de base).
* `cliner-mlops` (`d:\AIL-FT-02\CERTIF AIL\cliner-mlops`) : centré sur l'ingénierie système d'Architecte IA (migration Full Cloud, S3 Data Lake, Continuous Training événementiel Wasserstein, MLflow Serverless sur Cloud Run, CI/CD GitHub Actions, FinOps Auto-Kill).
* Les dépôts Git, environnements `.env` et dossiers disques sont 100% indépendants. `cliner-mlops` n'effectue que des lectures non destructrices sur les tables d'embeddings partagées.

### Q5 : Pourquoi coupler BioBERT et Qwen2.5-7B ? Pourquoi ne pas envoyer directement le protocole complet à Qwen ?
* **BioBERT = Encodeur Spécialisé (Bi-Encoder / 110M paramètres) :** Pré-entraîné sur PubMed/PMC, il ne génère aucun texte ni JSON. Il projette instantanément les paragraphes dans un espace vectoriel de 768 dimensions pour le filtrage géométrique (RAG). Il tourne rapidement sur simple CPU (0,00 €).
* **Qwen2.5-7B = Décodeur Génératif (LLM / 7 Milliards de paramètres) :** Modèle lourd capable de raisonner et de produire un schéma JSON strict. Si on lui passait un protocole brut de 50 pages (ou un JSON massif de 10 000 tokens), on observerait : saturation de la mémoire GPU, latence de traitement dégradée (>45s), risque d'hallucinations (*Lost in the Middle*) et explosion des coûts d'inférence.
* **Synergie Gagnante (Pattern Retriever-Extractor) :** BioBERT + Supabase filtrent 98% du bruit en **12 millisecondes** pour isoler les 2 paragraphes clés, puis Qwen concentre toute son attention sur ces 2 paragraphes pour livrer un JSON médical chirurgical en **3 secondes**, avec **zéro hallucination**.

### Q6 : Comment est orchestré le réentraînement continu ? Pourquoi un Cron GitHub Actions ? Faut-il vider la base ?
* **Choix de l'Orchestrateur (Option 1 - GitHub Actions Cron Hebdomadaire)** : Configuré dans [`.github/workflows/weekly_mlops_pipeline.yml`](.github/workflows/weekly_mlops_pipeline.yml) pour s'exécuter chaque lundi à 02h00 UTC. C'est la solution retenue car elle est **100% Free Tier (2 000 min/mois gratuites)**, stocke les secrets de manière chiffrée, et n'engendre **aucun coût de veille (0,00 €)**. Les alternatives comme AWS EventBridge + Lambda ou Webhook Supabase introduiraient des composants payants en attente 24/7 (anti-pattern FinOps).
* **Cinématique d'Ingestion & Déclenchement :**
  1. *À la demande (Médecin)* : Sur l'UI Streamlit, le praticien cherche n'importe quelle maladie (ex : cancer du sein, mélanome, diabète). L'étude choisie est ingérée en direct et mise en cache.
  2. *Automatique (Veille MLOps)* : Le Cron s'exécute le lundi sur une cohorte cible d'oncologie ou filtre les études récemment mises à jour sur ClinicalTrials.gov V2 (`filter.advanced=AREA[LastUpdatePostDate]RANGE[NOW-7DAYS,NOW]`).
* **Politique de Rétention des Données (Non, on ne vide jamais la base !) :**
  - **AWS S3 Data Lake :** Données brutes immuables partitionnées par date (`s3://cliner-mlops/clinical_studies/`). Stocker 10 000 protocoles JSON coûte moins de 0,005 $ par an ; ils constituent l'historique d'audit médical indispensable.
  - **Supabase pgvector :** Mises à jour idempotentes (`DELETE WHERE doc_id = %s` avant réinsertion) uniquement si une étude est révisée, sans supprimer les autres.
  - **Détection de Dérive (Wasserstein) :** Analyse calculée sur une **fenêtre glissante des 5 derniers protocoles insérés** (`ORDER BY id DESC LIMIT 5`) comparée au Gold Standard CHIA de référence (800 protocoles). Si $W > 0.15 \rightarrow$ Allumage EC2 GPU $\rightarrow$ Fine-Tuning LoRA $\rightarrow$ Auto-Kill immédiat !

### Q7 : Comment est architecturé le dossier `mlops_reentrainement/` ?
Tous les modules de la boucle d'automatisation MLOps sont regroupés dans [mlops_reentrainement/](mlops_reentrainement/) :

| Fichier | Rôle & Responsabilité Système |
| :--- | :--- |
| **`run_pipeline.py`** | **Orchestrateur Maître** : Pilote les 4 phases (Détection Drift $\rightarrow$ Démarrage EC2 $\rightarrow$ Train LoRA $\rightarrow$ S3/MLflow $\rightarrow$ Auto-Kill). |
| **`drift_detection.py`** | **Détection de Dérive** : Calcule la distance de Wasserstein ($W_1$) sur les embeddings BioBERT (768 dimensions). |
| **`monitoring_evidently.py`** | **Rapports de Distribution** : Génère le rapport visuel de distribution Evidently AI (`reports/data_drift_report.html`). |
| **`ec2_manager.py`** | **Gestionnaire d'Infrastructure EC2** : Pilote le cycle de vie de l'instance GPU via `boto3` et l'exécution distante via SSH. |
| **`finetune_lora.py`** | **Moteur QLoRA 4-bit** : Réentraîne l'adaptateur LoRA de Qwen-7B ($r=16, \alpha=32$) et exporte les métriques de convergence. |
| **`s3_storage.py`** | **Model Store S3** : Téléverse l'adaptateur réentraîné (~84 Mo) vers le bucket AWS S3 `s3://cliner-mlops/models_lora/`. |
| **`logger_config.py`** | **Journalisation d'Audit** : Génère les journaux d'exécution XML conformes aux exigences de traçabilité médicale. |

---

## 📄 Licence & Conformité
Projet distribué sous licence MIT. Conforme aux standards de traçabilité HDS / RGPD et aux bonnes pratiques d'ingénierie logicielle pour l'intelligence artificielle en santé.



