# Pitch de Présentation - Demo Day CliNER

Ce document formalise la trame narrative des 8 minutes de présentation du Demo Day pour l'application **CliNER**, répartie entre les 5 membres de l'équipe.

## Slide 1 & 2 : Contexte et Problématique (Jérémie) - 2 min
* **L'enjeu :** Les médecins (oncologues, chercheurs) passent des heures chaque semaine à lire des protocoles d'essais cliniques (PDF de 50 à 100 pages) pour vérifier si leurs patients y sont éligibles.
* **Le problème :** Ces données sont non structurées, complexes et le processus manuel est chronophage, retardant l'accès des patients aux traitements innovants.
* **La solution CliNER :** Un assistant IA hybride qui automatise l'extraction d'entités médicales clés (Pathologies, Traitements, Critères d'inclusion) avec un niveau de précision clinique (zéro hallucination).

## Slide 3 : Démo Live de l'Application (Christopher) - 1 min 45
* **Recherche :** Démonstration de l'interrogation en direct de l'API de ClinicalTrials.gov depuis l'interface Streamlit.
* **Extraction (GPU) :** Lancement de l'analyse sur un protocole. Affichage en quelques secondes du JSON structuré contenant les maladies et médicaments. Mention de l'appel au serveur Lightning AI et au modèle Qwen 7B.
* **Le "Cache Hit" (Effet Wow) :** Relance de l'analyse sur le même protocole pour montrer la vitesse de réponse (0.1s) permise par la base vectorielle Supabase, réduisant ainsi les coûts Cloud.
* **RAG Chatbot :** Démonstration du Chatbot permettant au médecin de poser une question en langage naturel sur le protocole.

## Slide 4 : Architecture Technique Globale (Arnaud) - 1 min
* Présentation du schéma d'architecture.
* Explication des choix technologiques de l'équipe :
  * **Frontend :** Streamlit pour l'interactivité.
  * **Backend & GPU :** Hébergement de l'inférence lourde sur Lightning AI avec **vLLM** pour optimiser la vitesse de Qwen 7B.
  * **Base de données :** Supabase (PostgreSQL avec pgvector) pour le stockage des embeddings et S3 pour les archives.
  * L'architecture est totalement distribuée et prête pour la production.

## Slide 5 : Pipeline ETL & Circuit de la donnée (Karim) - 1 min
* **Extract :** Comment les PDF et JSON sont rapatriés dynamiquement.
* **Load :** Stockage sécurisé et persistance de l'état.
* **Transform (Le cœur du réacteur hybride) :**
  1. Le texte est découpé (Chunking via LangChain).
  2. **BioBERT** transforme les chunks en vecteurs (Embeddings de 768 dimensions).
  3. Le système isole uniquement les paragraphes utiles par similarité cosinus (RAG).
  4. Le paragraphe filtré est envoyé au modèle **Qwen 2.5 7B** (doté de son adaptateur LoRA) qui extrait chirurgicalement l'information en format JSON.

## Slide 6 : Benchmark & Évaluation (Patrick) - 1 min 15
* Présentation du Gold Standard (132 études CHIA).
* Explication de la métrique exigeante (F1-score en Strict Matching).
* **Résultat clé :** Bond de +20 points grâce au Fine-Tuning (passage de 37% à 58.3%).
* **Défense clinique :** Une précision globale de 63% (et jusqu'à 100% sur les médicaments en RAG). Explication de la préférence vitale accordée à la précision sur le rappel (élimination des hallucinations).

## Slide 7 : Conclusion, MLOps et Perspectives (Christopher) - 1 min 20
* **Industrialisation MLOps :** Intégration de MLflow pour monitorer l'inférence vLLM et les expérimentations.
* **Lutte contre le Drift :** Mise en place cible d'une boucle **Human-in-the-Loop**. Les retours des médecins serviront à des campagnes de fine-tuning régulières.
* **Perspectives (Multimodalité) :** Ajout de modèles d'OCR (CNN) pour traiter les protocoles originaux scannés.
* **Conformité RGPD :** Implémentation future de tâches CRON (Auto-suppression / TTL) sur le bucket S3 Supabase pour détruire les documents bruts après extraction.
* Clôture et remerciements.
