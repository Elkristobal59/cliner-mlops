# ============================================================================
# Infrastructure-as-Code (IaC) — Projet CliNER-MLOps (RNCP 41993 - Bloc 4)
# ----------------------------------------------------------------------------
# Ce module Terraform déclaratif provisionne de manière reproductible :
#   1. Le socle PostgreSQL Supabase (pgvector, index HNSW, cache NER, pg_cron).
#   2. Le Data Lake & Model Registry AWS S3 (versionné pour le Rollback LoRA
#      et chiffré en AES-256 pour la conformité RGPD/HDS).
#   3. L'instance AWS EC2 GPU (g4dn.xlarge - Nvidia Tesla T4 16 Go) et son
#      Security Group (port 8000 FastAPI). Une fois créée par Terraform, son
#      allumage/extinction à la demande (Auto-Kill FinOps) est piloté par Boto3.
# ============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.21.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2.0"
    }
  }
}

# ----------------------------------------------------------------------------
# 1. PROVIDERS (AWS Paris eu-west-3 & Supabase PostgreSQL SSL)
# ----------------------------------------------------------------------------
provider "aws" {
  region = var.aws_region
}

provider "postgresql" {
  connect_string = "${var.supabase_db_url}?sslmode=require"
}

# ----------------------------------------------------------------------------
# 2. BASE VECTORIELLE, CACHE NER & PURGE RGPD (SUPABASE POSTGRESQL)
# ----------------------------------------------------------------------------
resource "postgresql_extension" "pgvector" {
  name = "vector"
}

resource "null_resource" "supabase_schema" {
  triggers = {
    # Idempotence : ne rejoue le script SQL que si le contenu de schema.sql change
    schema_sha1 = sha1(file("${path.module}/schema.sql"))
  }

  provisioner "local-exec" {
    command = "psql \"${var.supabase_db_url}\" -f ${path.module}/schema.sql"
  }

  depends_on = [
    postgresql_extension.pgvector
  ]
}

# ----------------------------------------------------------------------------
# 3. DATA LAKE & MODEL REGISTRY LoRA VERSIONNÉ (AWS S3)
# ----------------------------------------------------------------------------
resource "aws_s3_bucket" "cliner_storage" {
  bucket = var.s3_bucket_name

  tags = {
    Project     = "CliNER-MLOps"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

# Activation du versionnage natif S3 (permet le Rollback instantané des poids LoRA)
resource "aws_s3_bucket_versioning" "cliner_storage_versioning" {
  bucket = aws_s3_bucket.cliner_storage.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Chiffrement serveur AES-256 par défaut (Sécurité des données de santé / RGPD)
resource "aws_s3_bucket_server_side_encryption_configuration" "cliner_storage_encryption" {
  bucket = aws_s3_bucket.cliner_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ----------------------------------------------------------------------------
# 4. WORKER GPU D'INFÉRENCE & CONTINUOUS TRAINING (AWS EC2 g4dn.xlarge)
# ----------------------------------------------------------------------------
resource "aws_security_group" "cliner_gpu_sg" {
  name        = "cliner-mlops-gpu-sg"
  description = "Autorise le flux HTTPS/HTTP FastAPI (8000) et l'administration SSH (22)"

  ingress {
    description = "API REST FastAPI / vLLM (Swagger /docs)"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Orchestration SSH MLOps"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project   = "CliNER-MLOps"
    ManagedBy = "Terraform"
  }
}

resource "aws_instance" "cliner_gpu_worker" {
  ami                    = var.ec2_ami_id
  instance_type          = var.ec2_instance_type
  vpc_security_group_ids = [aws_security_group.cliner_gpu_sg.id]

  root_block_device {
    volume_size           = 50
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = false
  }

  user_data = <<-EOF
              #!/bin/bash
              systemctl enable fastapi.service
              systemctl start fastapi.service
              EOF

  tags = {
    Name      = "cliner-mlops-gpu-t4-worker"
    Project   = "CliNER-MLOps"
    FinOps    = "AutoKill-Managed-By-Boto3"
    ManagedBy = "Terraform"
  }
}
