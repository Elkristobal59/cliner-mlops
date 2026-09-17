# ==============================================================================
# Dockerfile : Environnement d'Exécution MLOps & Continuous Training (LoRA)
# Projet : CliNER-MLOPS (Certification RNCP41993 - Niveau 7)
# ==============================================================================

FROM python:3.10-slim

# Empêcher Python d'écrire des fichiers .pyc et forcer l'affichage direct des logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Installation des dépendances système de base (git, curl, compilateurs C pour psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements_mlops.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_mlops.txt

# Copie du code source MLOps
COPY drift_detection.py /app/
COPY ec2_manager.py /app/
COPY finetune_lora.py /app/
COPY run_pipeline.py /app/

# Déclaration du volume pour la persistance des modèles réentraînés
VOLUME ["/app/models"]

# Commande par défaut : Déclencher le pipeline complet d'évaluation et de réentraînement
ENTRYPOINT ["python", "run_pipeline.py"]
CMD ["--dry-run", "--force-retrain"]
