# 🏆 Stratégie de Certification RNCP41993 — Projet Final CliNER-MLOPS

> **Document de Référence :** Guide & Alignement Stratégique MLOps / LLMOps pour la Certification Architecte en Intelligence Artificielle (RNCP41993 - Niveau 7 / Bac+5)  
> **Repository :** [cliner-mlops](https://github.com/Elkristobal59/cliner-mlops)  
> **Dernière mise à jour :** 17 Septembre 2026  

---

## 📌 1. Contexte & Objectif Visé

La certification **RNCP41993 – Niveau 7 (Architecte en Intelligence Artificielle)** exige de démontrer la capacité à concevoir, industrialiser et piloter des systèmes d’IA à l’échelle d’une organisation, en intégrant :
- **La gouvernance et la conformité** (RGPD, AI Act, éthique).
- **L'infrastructure Cloud et de calcul** (FinOps, GreenOps, CPU/GPU, Terraform, conteneurisation).
- **Les pipelines de données pour l'IA** (ETL/ELT, vectorisation, ingestion continue).
- **L'industrialisation et le cycle de vie MLOps / LLMOps** (CI/CD/CT, Model Registry, monitoring de dérive, rollback, Human-in-the-Loop).

---

## 🛑 2. Démystification du « Continuous Training » en LLMOps

### Le faux dilemme : « On a un LLM, on n'a rien à réentraîner tous les jours, donc pas besoin d'Airflow ni de GitHub Actions ? »

Dans les projets MLOps de première génération (modèles tabulaires Scikit-Learn ou XGBoost), le réentraînement est souvent planifié de manière chronologique (ex: CRON tous les lundis à 2h du matin) car l'entraînement prend 1 minute sur CPU.

**Dans un projet d'IA Générative / LLM Médical (CliNER) :**
1. Le modèle est un **LLM de 7 Milliards de paramètres (Qwen-7B)** fine-tuné avec adaptateurs **LoRA/QLoRA (4-bit)**.
2. **Réentraîner un 7B LLM tous les jours à heure fixe serait une aberration technique, financière (FinOps) et écologique (GreenOps).**
3. Devant un jury d'Architecte IA, affirmer que l'on réentraîne un LLM 7B sur chaque commit ou tous les matins démontre un manque de maturité architecturale.

### Ce que le Jury Attend d'un Architecte IA :
En LLMOps de pointe, le cycle d'automatisation se décline sous **4 piliers concrets et justifiés** :

---

## 🏗️ 3. Les 4 Piliers d'Automatisation de CliNER-MLOPS

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │           PIPELINE MLOPS / LLMOPS CLINER               │
                                  └────────────────────────────────────────────────────────┘
                                                              │
         ┌───────────────────────────┬────────────────────────┴────────────────────────┬───────────────────────────┐
         ▼                           ▼                                                 ▼                           ▼
 ┌───────────────┐           ┌───────────────┐                                 ┌───────────────┐           ┌───────────────┐
 │ GITHUB ACTIONS│           │APACHE AIRFLOW │                                 │ EVIDENTLY AI  │           │ACTIVE LEARNING│
 │  (CI/CD/CT)   │           │ (ORCHESTRATION)                                 │ (MONITORING)  │           │ (RETRAINING)  │
 ├───────────────┤           ├───────────────┤                                 ├───────────────┤           ├───────────────┤
 │• Lint & Tests │           │• Ingestion API│                                 │• Latence GPU  │           │• Feedback UI  │
 │• Schema Pydant│           │  ClinicalTrial│                                 │• Format JSON  │           │  (Médecins)   │
 │• MERIDIAN GATE│           │• Parsing PDF  │                                 │• Data Drift   │           │• Seuil atteint│
 │  (Golden Set) │           │• BioBERT Embed│                                 │  (Vocabulaire)│           │  (ex: N=100)  │
 │• Docker Build │           │• Supabase DB  │                                 │• Alerting     │           │• QLoRA Retrain│
 └───────────────┘           └───────────────┘                                 └───────────────┘           └───────────────┘
```

### 1️⃣ Pilier 1 : CI/CD avec GitHub Actions & « Meridian Gate » (m05-d01)
Le pipeline GitHub Actions ne lance pas un entraînement lourd, mais garantit l'intégrité de la production :
* **Tests unitaires et syntaxiques (`pytest`, `flake8`) :** Validation de l'API FastAPI et de la logique de tokenisation.
* **Validation stricte des contrats de données (Pydantic) :** Les réponses de l'API doivent impérativement respecter le schéma JSON médical attendu (`condition`, `treatment`, `dosage`, `eligibility`).
* **Continuous Evaluation Gate (Meridian Gate) :**
  * À chaque Pull Request, un test d'inférence est exécuté sur un **Golden Set** de 5 protocoles cliniques de référence.
  * Si la précision ou le F1-Score chute sous **85%**, ou si le modèle produit un JSON mal formé (hallucination de syntaxe), le pipeline bloque automatiquement le merge !
* **Continuous Deployment (CD) :**
  * Build automatique des images Docker (Frontend Streamlit + Backend FastAPI).
  * Push sur Docker Hub / Registry et déclenchement du webhook de déploiement (Render / Cloud).

### 2️⃣ Pilier 2 : Apache Airflow pour l'Ingestion & l'Indexation Vectorielle (ETL pour l'IA)
Airflow ne sert pas à faire `.fit()`, il orchestre la **tuyauterie de données continue** indispensable au RAG :
* **`dag_clinicaltrials_ingestion` (Hebdomadaire) :**
  1. Interroge l'API ClinicalTrials.gov pour récupérer les nouvelles études cliniques publiées dans les spécialités cibles (Oncologie, Cardiologie).
  2. Télécharge les documents PDF bruts associés.
  3. Lance le pipeline de parsing (`pdf_parser`), découpage en sections et chunking sémantique.
  4. Calcule les vecteurs via le modèle d'embedding (BioBERT) et les insère dans **Supabase `pgvector`**.
  5. Invalide ou met à jour le cache sémantique (`clinical_ner_cache`).
* **`dag_drift_monitoring` (Quotidien) :**
  1. Extrait les logs d'inférence de la journée (prompts, latences, métadonnées).
  2. Calcule les métriques de dérive et génère le rapport de surveillance.

### 3️⃣ Pilier 3 : Monitoring Continu de la Dérive avec Evidently AI & MLflow
* **Data Drift (Dérive des Données) :**
  * Évolution statistique de la longueur des textes soumis.
  * Détection de nouveaux termes médicaux ou protocoles non représentés dans le dataset initial (CHIA).
* **Concept Drift (Dérive de Performance) :**
  * Taux de validité syntaxique des JSON générés.
  * Latence moyenne d'inférence (alerte si > 3.5s sur GPU).
  * Taux de retours utilisateurs (pouce rouge / pouce vert des médecins sur Streamlit).
* **Alerte Proactive :**
  * Envoi d'une alerte (Slack / Webhook) si le taux d'erreur dépasse 5%.

### 4️⃣ Pilier 4 : Réentraînement Continu Déclenché (Event-Driven / Active Learning)
* **Pas de réentraînement à heure fixe**, mais un réentraînement **déclenché par la valeur métier** :
  * Lorsque les cliniciens utilisent l'interface Streamlit, ils peuvent corriger une entité mal extraite (*Human-in-the-Loop*).
  * Ces corrections sont stockées dans une table Supabase dédiée (`ner_expert_feedback`).
  * **Règle d'automatisation :** Dès que 100 nouvelles annotations validées sont collectées :
    1. Déclenchement automatique d'un run de fine-tuning QLoRA sur GPU.
    2. Enregistrement du nouveau checkpoint dans **MLflow Model Registry** en statut `Staging`.
    3. Benchmark automatique contre le Test Set.
    4. Si le F1-Score surpasse la version actuelle : promotion en `Production` sans interruption de service.

---

## 📋 4. Grille de Correspondance avec le Référentiel RNCP41993

| Compétence Clé du Référentiel | Implémentation Réelle dans CliNER-MLOPS |
| :--- | :--- |
| **Gouvernance, RGPD & AI Act (Bloc 1)** | Classification "Système à Haut Risque" (Santé). Zéro PII patient stockée (anonymisation native des protocoles). Traçabilité intégrale des sources citées dans le PDF. Fiche de modèle (Model Card). |
| **Architecture & Infrastructure Cloud (Bloc 2)** | Découplage CPU (Streamlit sur Render) vs GPU (vLLM Qwen sur Lightning AI). Économie FinOps grâce au cache Supabase (0.1s de latence, zéro coût GPU sur les requêtes déjà vues). Infrastructure as Code via Terraform (`terraform/main.tf`). |
| **Pipelines de Données pour l'IA (Bloc 3)** | Ingestion automatisée ClinicalTrials.gov, parsing PDF, chunking sémantique, génération d'embeddings BioBERT et indexation vectorielle Supabase `pgvector`. Orchestration via Airflow. |
| **MLOps, CI/CD, Dérive & Monitoring (Bloc 4)** | CI/CD GitHub Actions avec Meridian Gate (bloquant si F1 < 85%). Tracking et Model Registry avec MLflow. Détection de Data & Concept Drift avec Evidently AI. Réentraînement événementiel (Active Learning). |

---

## ⏱️ 5. Trame Recommandée pour l'Oral de 5 Minutes (Bloc 4)

1. **Minute 1 — Enjeu Métier & Défi Scientifique :**  
   *« Les protocoles cliniques font 100+ pages de jargon médical non standardisé. Notre mission : automatiser l'extraction d'entités avec un LLM spécialisé tout en garantissant une fiabilité critique (zéro hallucination). »*
2. **Minute 2 — Architecture FinOps Hybride :**  
   *« Pour éviter l'explosion des coûts Cloud, nous avons conçu une architecture découplée : Frontend léger CPU sur Render, Moteur GPU vLLM Qwen-7B LoRA sur Lightning AI, et un cache sémantique Supabase qui traite les requêtes récurrentes en 0.1s sans consommer de GPU. »*
3. **Minute 3 — Pipeline de Données & Ingestion Vectorielle :**  
   *« Le RAG est alimenté par un pipeline d'ingestion automatisé (Airflow) qui télécharge les PDF de ClinicalTrials.gov, extrait le texte avec notre parser sur-mesure, et vectorise les paragraphes avec BioBERT dans Supabase pgvector. »*
4. **Minute 4 — MLOps, CI/CD & Meridian Gate :**  
   *« Nous ne réentraînons pas un modèle 7B à l'aveugle. Notre CI/CD GitHub Actions intègre un Meridian Gate : chaque modification teste le modèle sur un Golden Set clinique. Si le format JSON ou le F1-score régresse, le déploiement est bloqué. Les modèles sont versionnés sous MLflow. »*
5. **Minute 5 — Surveillance de Dérive & IA Responsable :**  
   *« En production, Evidently AI surveille la dérive des requêtes et la latence. Les corrections des médecins alimentent une boucle Human-in-the-Loop qui déclenche un réentraînement QLoRA uniquement lorsque 100 nouvelles annotations de haute qualité sont accumulées. Le tout est documenté avec une Model Card conforme à l'AI Act. »*
