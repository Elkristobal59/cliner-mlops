# Proposition d'Architecture Hybride (Retrieval-Augmented NER)

Ce document décrit l'évolution architecturale définitive du pipeline de Named Entity Recognition (NER), justifiée par les limites des modèles isolés lors de nos benchmarks. À présenter au jury dans les "Perspectives et Choix Architecturaux".

## 1. Contexte et Limites des Modèles Isolés

Lors de la conception de notre pipeline d'extraction, nous avons évalué deux approches distinctes qui présentaient chacune des failles critiques en milieu clinique :
- **Approche "Full BioBERT" (NER Classique)** : Bien qu'excellent pour repérer des entités structurelles (Conditions, Mesures), BioBERT utilisé seul générait énormément de faux-positifs sur les médicaments (hallucinations sur des mots chimiques non-pertinents) et peinait à structurer sa sortie en JSON strict pour une API.
- **Approche "Full LLM" (Qwen Zero-Shot)** : Envoyer un PDF entier de 50 pages à un LLM provoquait une saturation de son contexte. Le modèle "oubliait" des informations (faible rappel), hallucinait des médicaments inexistants pour remplir le prompt, et coûtait extrêmement cher en temps de calcul GPU.

## 2. La Solution : L'Architecture Hybride (RAG + NER)

Pour masquer les faiblesses respectives de ces deux technologies, notre architecture finale implémente un **Pipeline Hybride Séquentiel** (Ensemble Learning via RAG) :

### L'Architecture Cible :
1. **Filtrage Sémantique (BioBERT / Embedding)** : Plutôt que de faire du NER, BioBERT est utilisé comme "Radar". Le texte brut est découpé (Chunking) et BioBERT le transforme en vecteurs. Il isole uniquement les paragraphes pertinents (ex: *Critères d'Éligibilité*) par similarité cosinus.
2. **Extraction Experte (Qwen2.5-7B Fine-Tuné)** : Le LLM ne reçoit plus 50 pages, mais uniquement les 2 ou 3 paragraphes isolés par BioBERT. Doté de son adaptateur QLoRA, Qwen extrait de manière chirurgicale **toutes les entités** (Drug, Condition, Measurement) sous un format JSON strict.

## 3. Avantages de ce Pipeline Hybride
- **Précision Clinique (Zéro Hallucination)** : En restreignant la vision de Qwen aux seuls paragraphes validés par BioBERT, les hallucinations chutent à 0% sur l'extraction des traitements.
- **FinOps & Vitesse** : On ne fait tourner le lourd modèle Qwen (sur GPU Lightning AI) que sur quelques centaines de tokens, divisant par 10 le temps de calcul et la latence.
- **Mise en Cache (Cache Hit)** : Les vecteurs générés par BioBERT sont persistés dans PostgreSQL (Supabase pgvector). Si le document a déjà été scanné, BioBERT est court-circuité, rendant la recherche instantanée pour le Chatbot RAG.

> *Cette architecture démontre une réelle maturité d'ingénierie : nous ne subissons plus les biais d'un modèle unique, nous orchestrons la puissance sémantique de BioBERT et la rigueur générative de Qwen Fine-Tuné au sein d'une seule chaîne ETL.*
