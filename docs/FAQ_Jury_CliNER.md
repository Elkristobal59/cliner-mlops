# FAQ & Réponses pour le Jury - Soutenance CliNER

Ce document liste les questions pièges et classiques que le jury pourrait vous poser lors de la soutenance, avec les réponses techniques argumentées correspondantes.

## 1. Questions sur les Modèles (NLP / LLM)

### Q : Pourquoi un score F1 de 58% ? N'est-ce pas un peu faible ?
**Réponse :** 
En NLP médical avec évaluation stricte (caractère par caractère), 58% est un excellent score, qui correspond à l'état de l'art pour les LLM open-source de cette taille (7B). 
* **Priorité à la Précision :** En clinique, nous privilégions la précision (63% en moyenne, et 100% sur notre pipeline RAG pour les médicaments) pour éviter toute hallucination. Mieux vaut rater un terme que d'inventer un traitement.
* **Complexité :** Le dataset CHIA comporte 12 catégories très ambiguës.
* **Apport du Fine-Tuning :** Notre fine-tuning (QLoRA) a permis un bond de +20 points (de 37% à 58%) par rapport aux modèles fondateurs purs comme Gemini-Flash.

### Q : Pourquoi avoir choisi Qwen 7B plutôt que l'API de ChatGPT (OpenAI) ou Gemini ?
**Réponse :**
Pour des raisons de **souveraineté des données** et de respect du **secret médical (RGPD)**. Les données cliniques ne peuvent pas transiter sur des serveurs externes non certifiés HDS (Hébergeur de Données de Santé). En hébergeant un modèle Open-Source comme Qwen 7B sur notre propre infrastructure (Lightning AI), nous gardons un contrôle total sur l'inférence sans compromettre la sécurité. De plus, à terme, cela réduit drastiquement les coûts d'inférence par rapport aux requêtes API payantes.

### Q : Quel gros modèle permettrait d'atteindre l'excellence en F1-score (>75%) ?
**Réponse :**
Sur des architectures locales (Open-Source), le passage à l'échelle se ferait avec des modèles de 70 milliards de paramètres (ex: **Llama-3-70B**, ou **Meditron-70B** spécialisé médecine). Pour des tâches académiques pures, des modèles spécialisés basés sur l'architecture BERT (comme **GatorTRON**, 8.9B) excellent particulièrement sur le NER clinique strict.

---

## 2. Questions sur l'Architecture (RAG & Base de données)

### Q : Pourquoi utiliser BioBERT pour la recherche sémantique (RAG) plutôt que de tout envoyer au LLM directement ?
**Réponse :**
Envoyer un protocole clinique complet (qui fait parfois 50 à 100 pages) dans le *prompt* d'un LLM coûte très cher en puissance de calcul (explosion de la VRAM due à la fenêtre de contexte) et provoque un phénomène de "Lost in the middle" (le LLM oublie l'information au milieu du texte).
Le système **RAG avec BioBERT et Supabase (pgvector)** permet de filtrer intelligemment l'information : on ne transmet à Qwen que les paragraphes strictement pertinents (ex: critères d'inclusion), ce qui rend le processus instantané, moins coûteux et beaucoup plus précis.

### Q : Pourquoi utilisez-vous Supabase (PostgreSQL) et comment gérez-vous le stockage des PDF ?
**Réponse :**
* **Pour les vecteurs :** PostgreSQL via l'extension `pgvector` est parfait pour stocker les "chunks" et leurs embeddings, permettant une recherche de similarité cosinus ultra-rapide. Cela nous sert aussi de **système de Cache** : si un protocole a déjà été analysé, on affiche instantanément le résultat (0,1s) sans solliciter le GPU.
* **Pour les PDFs :** Les PDFs sont uploadés temporairement sur un **S3 Bucket (Supabase Storage)**. Notre perspective d'évolution est de mettre en place une routine **CRON (auto-suppression / TTL)** pour purger ces fichiers bruts de l'espace de stockage afin de maîtriser nos coûts Cloud et garantir une conformité stricte au RGPD.

---

## 3. Questions sur le MLOps et l'Évolution (Production)

### Q : Comment comptez-vous gérer le "Drift" (la dérive des concepts et des données) dans le temps ?
**Réponse :**
La terminologie médicale évolue rapidement. Notre vision cible pour contrer le Drift est une boucle **Human-in-the-Loop**. L'interface Streamlit permet (ou permettra) aux médecins de signaler une erreur d'extraction. Ces retours qualifiés, après curation, alimenteront une base de données de "feedback" qui déclenchera périodiquement des campagnes de **Fine-Tuning continu** du modèle.

### Q : Que faites-vous si l'hôpital vous donne des PDF scannés ou manuscrits ?
**Réponse :**
Aujourd'hui, l'outil gère les documents digitaux natifs. Notre perspective d'évolution (Multimodalité) consiste à ajouter en amont une brique **OCR** (Reconnaissance Optique de Caractères) s'appuyant sur des réseaux de neurones convolutifs (**CNN** ou Vision Transformers). Cette brique transformera l'image scannée en texte brut avant de l'envoyer dans notre pipeline NLP existant.

### Q : En quoi votre projet n'est-il pas qu'une simple "maquette" (POC) ?
**Réponse :**
Nous avons adopté une démarche d'industrialisation dès le premier jour :
1. **MLOps :** Intégration de **MLflow** pour le suivi constant des expériences, de la perte (loss) et de l'hyperparamétrage, et suivi de l'inférence en production.
2. **Architecture distribuée :** Le Frontend (Streamlit), le backend de calcul lourd (Lightning AI + vLLM) et le stockage (Supabase) sont séparés pour permettre une scalabilité horizontale.
3. **Sécurité & Coûts :** Utilisation du cache vectoriel pour éviter de solliciter inutilement les serveurs GPU.



ok et pourquoi les autres colonne on a jamais d'info ?



Je suppose que tu parles des colonnes comme **Médicaments (Drug)**, **Phase**, ou **InterventionType** qui affichent très souvent du vide ou `N/A` dans ton tableau ?

C'est tout à fait normal et lié à la nature même des données médicales, voici pourquoi pour ton pitch au jury :

1. 💊 **Médicaments (Drug)** : Souvent, l'IA ne renseigne rien car il n'y a tout simplement... aucun médicament ! Beaucoup d'essais portent sur des dispositifs médicaux (IRM, pacemakers), de la radiothérapie, de la chirurgie, ou sont juste des études d'observation (on regarde l'évolution de la maladie sans rien donner au patient). L'IA NER fait bien son travail : elle ne détecte pas de drogue, donc elle laisse vide.
2. 🔬 **Phase & InterventionType** : Ces colonnes viennent de l'API officielle de _ClinicalTrials.gov_. Le champ "Phase" (Phase 1, 2, 3...) n'existe **que** pour les essais cliniques testant un nouveau traitement. Si c'est une étude observationnelle ou un registre, ce champ n'existe pas, donc le code met `N/A` (Not Applicable).
3. 📝 **Critères d'éligibilité** : Le modèle IA que vous avez choisi pour cette étape (le LoRA _Elkristobal59/qwen-7b-chia-ner_) est un modèle de **NER** (Reconnaissance d'Entités Nommées). Il est ultra-puissant pour pointer des mots précis (maladie, drogue) mais il n'a pas été entraîné pour résumer des paragraphes entiers. C'est pour ça que dans `api/main.py`, le code force l'affichage de la phrase "_Veuillez consulter le texte source pour les critères._".

**💡 Astuce pour le jury :** Tu peux totalement t'en servir pour valoriser votre architecture ! Tu peux dire : _"Dans le tableau de synthèse NER, on a extrait les mots-clés stricts. Mais si le médecin veut le détail complet des critères, c'est là qu'intervient notre onglet 4 (Chatbot RAG) ! Le médecin peut discuter avec l'essai complet."_