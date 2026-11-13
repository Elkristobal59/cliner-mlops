-- ============================================================================
-- Script : schema.sql (Provisionné par Terraform sur Supabase PostgreSQL)
-- Rôle   : Initialise l'extension pgvector, la table vectorielle BioBERT (768d),
--          l'index HNSW cosinus, la table de cache NER et la purge RGPD (7j).
-- ============================================================================

-- 1. Activation de l'extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Table principale des embeddings cliniques BioBERT (768 dimensions)
CREATE TABLE IF NOT EXISTS clinical_trials_data_biobert (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(255) NOT NULL,
    chunk_id VARCHAR(255) UNIQUE NOT NULL,
    raw_text TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Index HNSW pour accélérer la recherche par similarité cosinus (< 12 ms)
CREATE INDEX IF NOT EXISTS clinical_trials_biobert_embedding_idx 
ON clinical_trials_data_biobert 
USING hnsw (embedding vector_cosine_ops);

-- 4. Table de Cache d'Inférence NER (Réponse instantanée en 0.01s / 0 € GPU)
CREATE TABLE IF NOT EXISTS clinical_ner_cache (
    doc_id TEXT PRIMARY KEY,
    disease TEXT,
    extraction TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 🛡️ GOUVERNANCE RGPD & FINOPS : PURGE AUTOMATIQUE (Data Lifecycle)
-- ============================================================================
-- 5. Activation du planificateur PostgreSQL (pg_cron)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 6. Tâche quotidienne à minuit (0 0 * * *) : purge des vecteurs > 7 jours
SELECT cron.schedule(
  'nettoyage-vecteurs-obsoletes',
  '0 0 * * *',
  $$ DELETE FROM clinical_trials_data_biobert WHERE created_at < NOW() - INTERVAL '7 days' $$
);
