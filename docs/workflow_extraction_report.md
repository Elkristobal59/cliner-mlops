# Rapport de Workflow : Processus d'Extraction (CliNER)

Ce document détaille, étape par étape, le workflow technique suivi par une donnée depuis l'interface utilisateur jusqu'à l'extraction des entités médicales structurées.

## Étape 1 : Interrogation et Récupération des Données
1. L'utilisateur lance une recherche via le Frontend **Streamlit** (ex: "Asthme, Phase 3").
2. L'application interroge l'API publique de **ClinicalTrials.gov**.
3. Les protocoles correspondants sont téléchargés sous deux formes :
   * Les métadonnées en **JSON** (directement affichées dans la "Summary Table" du navigateur).
   * Les textes complets au format **PDF** qui sont temporairement uploadés sur notre bucket S3 (Supabase Storage).

## Étape 2 : Pré-traitement et Découpage (Chunking)
Une fois un essai sélectionné par le médecin pour analyse :
1. Le texte brut du protocole est envoyé vers notre backend GPU (**Lightning AI**).
2. Il est nettoyé (retrait du bruit, caractères spéciaux).
3. Le texte passe par l'outil de **Chunking** de LangChain : il est découpé en blocs de texte d'environ 1000 caractères, avec un léger chevauchement (overlap) pour ne pas casser de phrases importantes.

## Étape 3 : Vectorisation et Mise en Cache (BioBERT)
1. Chacun de ces blocs (chunks) passe dans le modèle d'encodage **BioBERT**.
2. BioBERT transforme le texte médical en une liste de 768 nombres (un Embedding / Vecteur).
3. Ces vecteurs, accompagnés de leur texte d'origine, sont insérés dans notre base de données **PostgreSQL** via l'extension **pgvector** sur Supabase.
   * *Note : Ce système agit comme un "Cache". Si l'étude a déjà été vectorisée dans la base, on court-circuite cette étape et on passe directement au point 4 en moins de 0.1s.*

## Étape 4 : Recherche Sémantique (Filtrage RAG)
Il serait trop lourd (et risqué en termes d'hallucination) d'envoyer tout le PDF à notre LLM principal. Nous appliquons donc le principe du RAG (Retrieval-Augmented Generation) :
1. Une requête cible prédéfinie (ex: "Quels sont les critères d'inclusion et les médicaments ?") est également vectorisée par BioBERT.
2. Une recherche de **similarité cosinus** est exécutée dans PostgreSQL.
3. Seuls les paragraphes les plus pertinents (ex: la section exacte des critères d'éligibilité) sont extraits de la base.

## Étape 5 : Extraction des Entités (Modèle Qwen 7B)
C'est le cœur cognitif de l'application :
1. Le(s) paragraphe(s) filtré(s) est/sont inséré(s) dans un "Prompt" très strict.
2. La requête est envoyée au modèle **Qwen 2.5 7B** hébergé sur le GPU.
3. Grâce au serveur d'inférence **vLLM**, l'adaptateur spécialisé **LoRA** (issu de notre Fine-Tuning) est greffé à la volée sur Qwen.
4. Le modèle lit le texte et génère en sortie un fichier **JSON standardisé** contenant la liste exacte des pathologies, traitements, posologies, et mesures.

## Étape 6 : Restitution et Archivage (MLOps)
1. Le JSON est renvoyé au Frontend (Streamlit) et s'affiche dans un tableau de bord lisible pour le médecin.
2. En parallèle, pour le suivi **MLOps**, ce JSON extrait est sauvegardé de manière persistante sur Supabase pour analyse future.
3. Le médecin peut également utiliser l'onglet "Chatbot" pour dialoguer en temps réel avec le système, en s'appuyant sur les mêmes chunks récupérés lors de l'étape 4.
