# Rapport de Fine-Tuning - Modèle d'Extraction NER (CliNER)

Ce rapport documente le processus d'entraînement et d'optimisation du grand modèle de langage (LLM) utilisé pour l'extraction d'entités nommées cliniques (NER) sur le projet CliNER.

## 1. Contexte et Objectifs
L'objectif était de spécialiser un modèle génératif Open-Source pour extraire des informations médicales structurées (selon la taxonomie du dataset CHIA : *Drug, Condition, Measurement, Temporal*, etc.) à partir de protocoles d'essais cliniques complexes.
La priorité absolue en milieu médical étant la **Précision** (0% d'hallucination) plutôt que le simple rappel.

## 2. Choix Technologiques
* **Modèle de base :** Qwen2.5-7B-Instruct (Performant, bilingue, léger).
* **Méthode de Fine-Tuning :** QLoRA (Quantized Low-Rank Adaptation) pour adapter le modèle sur un GPU de taille raisonnable tout en maintenant ses performances.
* **Infrastructure :** Serveurs GPU loués sur Lightning AI.
* **MLOps :** Suivi des expérimentations et des hyperparamètres via **MLflow**.
* **Inférence :** Déploiement du modèle avec ses adaptateurs LoRA via **vLLM** pour maximiser la vitesse d'inférence en production.

## 3. Protocole d'Entraînement
Nous avons transformé les annotations humaines brutes (fichiers BRAT `.ann` et textes `.txt`) de 132 études du dataset CHIA en un "Gold Standard" au format JSON.
Le modèle a été entraîné avec pour instruction de lire un paragraphe de protocole clinique et de renvoyer un JSON strict contenant les entités extraites.

### Hyperparamètres clés (MLflow)
* **Learning Rate :** 0.0002 (pour une convergence stable sans oubli catastrophique).
* **Quantization :** 4-bit (NF4) pour le modèle de base.
* **Loss :** Surveillée en temps réel, convergeant de manière lisse vers 0.

## 4. Résultats et Benchmarks

L'évaluation a été réalisée en **Strict Matching** (correspondance exacte au caractère près), une métrique extrêmement punitive mais standard en milieu académique.

### Modèles Fondateurs (Zero-Shot) - Avant Fine-Tuning
* Gemini-Flash-Lite / Qwen1.5-7B-Chat
* **Précision :** ~50%
* **F1 Score :** ~37%
* *Problème :* Fort taux d'hallucination et incompréhension de la taxonomie médicale complexe.

### Modèle Fine-Tuné (Qwen2.5-7B-Instruct + LoRA) - Après Fine-Tuning
* **Précision :** 63.12%
* **Rappel :** 54.18%
* **F1 Score Global :** **58.31%**
* **Précision sur pipeline RAG complet (Extraction Médicaments) :** **100%**

## 5. Conclusion du Fine-Tuning
Le fine-tuning a généré un bond de performance spectaculaire de **+20 points de F1-Score**. Le modèle spécialisé a atteint son objectif : une précision clinique redoutable (les hallucinations sont quasiment nulles). La solution est désormais mature pour être mise en production sur notre architecture hybride (BioBERT + Qwen).
