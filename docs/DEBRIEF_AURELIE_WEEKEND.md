# 🎤 Discours Oral Technico-Narratif pour Aurélie (Débriefing du Lundi Matin)
**Le parfait équilibre : à lire à l'oral comme une histoire fluide, mais gorgé de termes techniques, d'hyperparamètres et d'un détail millimétré du circuit de la donnée !**

---

## 🌟 1. Introduction & Baptême officiel du Projet
« Bonjour Aurélie ! Vendredi dernier, le 24 juillet, l'équipe a fait un bond technologique majeur. Pour commencer sur une note officielle, nous avons baptisé notre projet **CliNER** (la contraction de *Clinical* et *NER*, pour la reconnaissance d'entités médicales), un nom adopté à l'unanimité !

Vendredi dernier, nous avons fonctionné en véritable *task force* : nous avons résolu un goulot d'étranglement critique dans notre RAG, industrialisé notre inférence GPU et détaillé le circuit complet de nos données sous le prisme du **FinOps** et du **Privacy by Design**. Voici exactement comment nous nous sommes réparti les réalisations techniques lors de cette journée intensive : »

---

## 🧠 2. Mon travail (Christopher) : Lead IA, Fine-Tuning 7B & Intégration vLLM
« De mon côté, je me suis concentré sur le moteur d'inférence et le pont avec l'interface.
J'ai modifié notre backend **`FastAPI`** (`api/main.py`) pour y raccorder dynamiquement notre propre modèle fine-tuné **`Qwen2.5-7B-Instruct`** via l'extension **LoRA de `vLLM`**, hébergée sur instance GPU *Lightning AI*. C'est officiellement notre modèle 7B qui réalise l'extraction NER en production, avec un débit fulgurant de **75 tokens/seconde** (soit 2 à 4 secondes par essai clinique) !

Comme les LLM peuvent parfois entourer leurs réponses de texte conversationnel, j'ai implémenté un **parseur silencieux à la volée** dans l'API. Il intercepte les sorties brutes du modèle et les convertit instantanément en un **JSON strict** (`{condition: ..., medications: [...]}`) pour garantir 0% de crash sur le front-end `Streamlit`. 
Enfin, j'ai configuré notre API pour renvoyer un champ `inclusion_criteria` neutre afin de laisser la place au module TF-IDF de Jérémie, et j'ai finalisé notre slide deck **Reveal.js** autonome en encodant tous nos visuels en Base64. »

---

## 🏗️ 3. Le travail d'Arnaud : Architecte Flux, Optimisation RAG & Persistance Front
« Arnaud a réalisé un travail remarquable d'optimisation réseau et d'architecture front.
D'abord, il a fusionné nos requêtes vers l'API REST *ClinicalTrials.gov* : nous sommes passés de 2 appels redondants à **une seule requête optimisée** (`pageSize=50`), directement réutilisée en mémoire par notre *Summary Table*, divisant notre latence par deux !

Ensuite, il a résolu la perte de session lors d'un rafraîchissement (`F5`) en déployant une persistance côté client via le **`localStorage` du navigateur**. L'état de l'application (tableaux, sélections, historique du chat RAG) est restauré sans jamais écrire de données médicales sur les disques de nos serveurs — un argument incontestable de **Privacy by Design**.

Enfin, il a restructuré notre pipeline RAG (`build_rag_text`) en séparant le flux en deux branches spécialisées :
* 🛣️ **Branche 1 (IA / NER Qwen 7B) :** Reçoit le texte pour extraire chirurgicalement les entités (`condition` et `medications`).
* 🛣️ **Branche 2 (Algorithme TF-IDF) :** Reçoit le texte pour découper mathématiquement et à 100% le paragraphe des critères d'éligibilité (`inclusion_criteria`), sans risque d'hallucination.
Pour alimenter ce moteur biface, Arnaud a calibré nos hyperparamètres en montant le **`top-K` à 15** et le **`chunk_size` à 2000 tokens**. »

---

## ⚡ 4. Le travail de Karim (downloa27) : Diagnostic RAG & Correction Front
« Karim a mené un audit de code décisif qui a permis de lever notre plus gros goulot d'étranglement sémantique. 
Il a découvert qu'au niveau du front `Streamlit`, seul le champ `"eligibilityCriteria"` était transmis à notre index vectoriel BioBERT, privant le LLM des descriptions, phases, interventions et médicaments de l'essai ! 

Il a codé et poussé un correctif majeur (`fix(front)`) qui injecte **l'intégralité du protocole clinique dans le pipeline RAG**. Depuis sa mise en production, Qwen-7B accède à un contexte global, ce qui a propulsé la précision de nos extractions NER et nous permet de faire fonctionner notre RAG en pur mode **Zero-Shot** avec une fiabilité impressionnante ! »

---

## ☁️ 5. Le travail de Jérémie : Infrastructure Cloud Supabase, TF-IDF & Dataset bratEval
« Jérémie a formalisé notre urbanisme technique en réalisant la cartographie complète de notre architecture sur **Excalidraw**, modélisant tous les flux d'ingestion, de transformation et de stockage pour le jury.
Côté algorithmique, il a développé notre module **TF-IDF** pour isoler et extraire avec une précision mathématique les paragraphes d'éligibilité.

Surtout, c'est Jérémie qui a préparé et structuré le jeu de données d'évaluation Gold Standard **`chia_with_pdf`** (dossiers `train` et `test`) pour notre benchmark scientifique officiel avec l'outil académique **`bratEval`**. 
Grâce à ce setup de test et à notre fine-tuning, nous avons pu mesurer l'impact spectaculaire de notre travail :
* **Sur l'évaluation académique stricte `bratEval` :** Nous obtenons un F1 Score de **16.8%**. Ce score s'explique par la sévérité absolue de l'outil sur les frontières exactes au caractère près (offsets `start`/`end`), alors que notre modèle est pensé pour la pertinence clinique en JSON.
* **Sur notre évaluation clinique (Test Set de 390 chunks) :** Notre modèle **Qwen2.5-7B-Instruct (QLoRA 4-bit) atteint un F1 Score spectaculaire de 58.31% !** (Soit **63.12% de Précision** et **54.18% de Rappel**, faisant un bond immense de +20 points face aux modèles Zéro-Shot bruts comme Gemini Flash ou Qwen 1.5 qui plafonnaient à ~37%).

💡 **L'argument clinique en or à donner à Aurélie sur ce résultat :**
> *« Sur une tâche aussi ardue que l'extraction d'entités médicales complexes, frôler les 60% de F1 avec un modèle 7B en 4-bit, c'est énorme ! Le point clé pour le jury, c'est que notre **Précision (63.1%) est supérieure à notre Rappel (54.2%)**. C'est exactement le comportement qu'on recherche en santé : cela prouve que le modèle est **prudent**. Quand il extrait une entité, il a souvent raison. Il vaut toujours mieux rater une information clinique (Rappel un peu plus bas) plutôt que d'inventer une fausse maladie par hallucination ! On est passés d'un LLM brut qui ne comprenait rien au médical à un véritable expert clinique ! »*

Côté Cloud, Jérémie a mis en place notre bucket **S3 (`clinical_pdfs`)** et notre base **PostgreSQL pgvector** sur **Supabase**, avec une politique **FinOps de purge automatique (TTL) à 7 jours**. »

---

## 🧪 6. Le travail de Patrick : Tests Unitaires & Assurance Qualité
« De son côté, Patrick s'est concentré sur la fiabilisation logicielle du projet. Il est en charge de la conception et du développement des **tests unitaires** de l'application. 
Son objectif est de construire un harnais de validation automatisé pour vérifier que chaque brique (API, parsers, fonctions de nettoyage) répond correctement, nous garantissant un pipeline d'extraction robuste et à l'abri des régressions lors des futurs déploiements. »

---

## 💎 7. Le Circuit Précis de la Donnée & Stockage (À expliquer en détail pour Aurélie)
« Pour être parfaitement transparent sur notre urbanisme technique devant Aurélie et le jury, voici exactement le trajet millimétré d'une donnée clinique dans CliNER, depuis le clic du médecin jusqu'au Cloud, structuré en 4 étapes clés :

### Étape 1 : Ingestion & Mémoire Éphémère (Privacy by Design)
Quand le médecin lance une recherche sur Streamlit, notre backend interroge l'API REST `ClinicalTrials.gov` en **une seule requête optimisée (`pageSize=50`)**. 
Le fichier JSON brut reçu **ne touche jamais le disque dur de nos serveurs**. Il est stocké uniquement en mémoire vive (`session_state`) et synchronisé dans le **`localStorage`** du navigateur du médecin. 
*Avantage :* Si le médecin fait `F5`, il ne perd rien. Et dès qu'il ferme son onglet, tout disparaît. C'est le respect absolu de la vie privée (zéro trace de recherche patient hébergée chez nous).

### Étape 2 : Extraction Binaire & Archivage Légal (Supabase S3)
Lorsque le protocole nécessite une analyse approfondie, notre script télécharge le document officiel depuis les serveurs américains. Il est lu instantanément en mémoire vive via `PyMuPDF`. 
En parallèle, une copie exacte du fichier binaire est envoyée dans notre bucket Cloud **Supabase Storage (dossier S3 `clinical_pdfs`)**. 
*Avantage :* Nous garantissons une **auditabilité totale**. Si un hôpital ou la FDA nous demande dans 6 mois de justifier pourquoi notre IA a pris une décision, nous aurons toujours le document source exact sous la main !

### Étape 3 : Indexation Sémantique & Purge FinOps (PostgreSQL / pgvector)
Le texte intégral du protocole (titre, conditions, interventions, médicaments, éligibilité) est découpé par notre pipeline (`chunk_size=2000 tokens`) puis converti en vecteurs par notre modèle d'embeddings **BioBERT**. 
Ces embeddings et les morceaux de texte sont indexés de manière durable dans la table relationnelle **`clinical_trials_data_biobert`** sur notre base de données **PostgreSQL Supabase** via l'extension **`pgvector`**. 
*Avantage FinOps :* Pour ne pas faire exploser notre facture Cloud avec des vecteurs qui s'accumulent à l'infini, nous avons instauré un **TTL (Time-To-Live) avec purge automatique tous les 7 jours**.

### Étape 4 : Inférence Haute Vitesse & Observabilité (vLLM & MLflow)
Lors du chat RAG ou de l'extraction, notre moteur vectoriel remonte les 15 passages les plus pertinents (**`top-K=15`**). Ils sont envoyés en pur mode **Zero-Shot** à notre modèle fine-tuné **Qwen2.5-7B-Instruct (QLoRA 4-bit)** tournant sur un GPU Lightning AI via le moteur ultra-rapide **`vLLM`** (débit de **75 tokens/seconde**, soit une réponse en 2 à 4 secondes). 
Le JSON propre généré par le modèle est affiché en direct au médecin ET enregistré dans notre serveur d'observabilité **MLflow**. 
*Avantage :* MLflow nous offre une traçabilité complète pour monitorer nos temps de latence, la consommation GPU et la précision du modèle en continu. »

---
*Tu as là un discours d'une précision chronologique, technique et médicale absolue pour briller demain à 9h00 !* 🚀🏆
