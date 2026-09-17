📊 Résumé Architecture : Stockage & Base de Données

Afin de garantir des performances optimales (RAG hyper rapide) et de maîtriser nos coûts Cloud, voici comment est gérée la donnée sur notre infrastructure Supabase :

1. La Base de Données (PostgreSQL / pgvector)

Table unique : clinical_trials_data_biobert
Ce qu'on y stocke : Uniquement les paragraphes de textes découpés (chunks = raw_text) et leurs représentations mathématiques (embeddings = vector(768)).
Quand est-ce stocké ? À chaque fois qu'un document passe dans l'API. (À noter : l'API purge automatiquement les anciens vecteurs d'un document avant de le réinsérer pour éviter les doublons).
Comment est-ce purgé ? Nous avons mis en place un CRON natif (pg_cron) dans la base. Tous les jours à minuit, la base exécute automatiquement une requête qui supprime tous les vecteurs vieux de plus de 7 jours. La base reste ainsi légère, rapide, et on ne paie pas pour du stockage inutile.

2. Le Stockage Fichiers (S3 / Supabase Storage)

Bucket unique : clinical_pdfs (le bucket raw-pdfs et l'ancienne table clinical_trials_data ont été supprimés pour nettoyer l'architecture).
Ce qu'on y stocke :
Les PDF originaux (si uploadés pour traitement).
Les résultats finaux de l'IA au format JSON (dans le dossier extracted_json/).
Quand est-ce stocké ? L'API FastAPI génère le JSON final grâce au LLM et l'envoie en direct à Streamlit. Dans la même seconde, elle sauvegarde ce JSON sur le bucket S3 pour garder une trace (MLOps Data Lake).
Comment est-ce purgé ? Contrairement à la base vectorielle qui est volatile (7 jours), le bucket S3 sert d'Archive MLOps. C'est ici qu'on garde la trace de nos extractions (les JSON) sur le long terme pour pouvoir analyser les performances de notre LLM plus tard sans surcharger la base SQL. (Les PDF temporaires, eux, sont soumis aux règles de TTL / auto-suppression du bucket pour optimiser les coûts