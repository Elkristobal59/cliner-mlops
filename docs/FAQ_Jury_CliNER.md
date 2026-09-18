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

### Q : Pourquoi une architecture hybride AWS S3 + Supabase (PostgreSQL pgvector) ? Pourquoi ne pas tout mettre sur S3 ?
**Réponse :**
Dans une architecture de niveau production (Lead AI / RNCP 41993), il est fondamental de dissocier le **Stockage Objet (Data Lake)** du **Moteur Vectoriel & Base Opérationnelle** :
1. **Ce que S3 fait (Data Lake & Model Registry) :**
   * Stockage massif, illimité et économique (~0,02 $/Go/mois) pour les données lourdes : les protocoles PDF bruts complets (100 pages chacun), les jeux de données annotés CHIA (`.jsonl`), les checkpoints d'adaptateurs LoRA réentraînés (~84 Mo par version) et les logs/artefacts MLflow.
   * Cela évite de saturer le quota gratuit de 1 Go du stockage Supabase.
2. **Ce que Supabase (PostgreSQL + `pgvector`) est le seul à pouvoir faire (Base Opérationnelle temps réel) :**
   * **Recherche vectorielle mathématique native :** S3 est un stockage passif incapable de calculer un produit scalaire ou une distance cosinus (`ORDER BY embedding <=> %s::vector LIMIT 5`). Si on utilisait S3 pour le RAG, l'API devrait télécharger les fichiers en local et calculer les distances en RAM Python à chaque requête, ce qui ferait exploser la latence de **15 millisecondes à plus de 25 secondes** !
   * **Cache d'inférence instantané (`clinical_ner_cache`) :** Recherche par index B-tree en 0,01s qui court-circuite tout calcul GPU coûteux si l'étude a déjà été extraite.
   * **Transactions relationnelles ACID :** Gestion multi-utilisateurs concurrente et recueil des feedbacks médicaux pour surveiller la dérive conceptuelle.

### Q : Pourquoi être passé sur AWS EC2 (GPU `g4dn.xlarge`) avec Auto-Kill au lieu de Lightning AI ?
**Réponse :**
* **Souveraineté & Dépendance Réseau :** Lightning AI Studio nécessitait un tunnel réseau instable (`localtunnel` ou `ngrok`) pour exposer les ports vers le frontend, avec des coupures aléatoires et des IP changeantes.
* **Standardisation Cloud Entreprise :** Déployer sur AWS EC2 dans un VPC privé avec des Security Groups stricts répond aux standards réels des entreprises et aux exigences du titre Architecte IA.
* **Gestion FinOps Stricte :** Grâce à notre module Python `boto3` ([ec2_manager.py](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/07_mlops_reentrainement/ec2_manager.py)) et à notre workflow GitHub Actions ([deploy_ec2_autokill.yml](file:///d:/AIL-FT-02/CERTIF%20AIL/cliner-mlops/.github/workflows/deploy_ec2_autokill.yml)), la machine GPU n'est allumée qu'à la demande et s'éteint automatiquement (Auto-Kill) après 45 minutes de démo ou à la fin du réentraînement LoRA. Coût résiduel = 0,00 €.

### Q : Quelle est la différence et le cloisonnement entre ce projet et votre projet Fullstack CDSD (`clinicalapp`) ?
**Réponse :**
* **Deux périmètres académiques distincts :**
  - Le projet **CDSD** (`clinicalapp` sur `d:\AIFS01\PROJET FINAL\stack_equipe`) visait la conception applicative Data Science Fullstack (FastAPI, Streamlit, première extraction NER).
  - Le projet **Lead AI RNCP 41993** (`cliner-mlops` sur `d:\AIL-FT-02\CERTIF AIL\cliner-mlops`) est centré sur l'ingénierie système et le MLOps : migration Full AWS (EC2 GPU, S3), pipeline automatisé de Continuous Training avec détection de dérive statistique Wasserstein sur embeddings BioBERT, gouvernance FinOps Auto-Kill et CI/CD Quality Gate.
* **Étanchéité technique totale :** Deux dépôts Git isolés, aucun fichier commun écrasé, et non-régression garantie sur la base Supabase qui n'est consultée qu'en lecture pour les embeddings de référence.

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