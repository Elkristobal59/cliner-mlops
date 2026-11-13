variable "aws_region" {
  description = "Région AWS pour le Data Lake S3 et le Worker EC2 GPU (Paris)"
  type        = string
  default     = "eu-west-3"
}

variable "s3_bucket_name" {
  description = "Nom du bucket AWS S3 (Data Lake PDF, datasets CHIA & Registry LoRA)"
  type        = string
  default     = "cliner-mlops"
}

variable "ec2_instance_type" {
  description = "Type d'instance EC2 GPU pour l'inférence vLLM et le Fine-Tuning QLoRA (Nvidia Tesla T4 16 Go)"
  type        = string
  default     = "g4dn.xlarge"
}

variable "ec2_ami_id" {
  description = "AMI Deep Learning Ubuntu PyTorch/CUDA (eu-west-3)"
  type        = string
  default     = "ami-0c4c4bd6cf0c5fe52"
}

variable "supabase_db_url" {
  description = "URL de connexion PostgreSQL Supabase (SUPABASE_DATABASE_URL)"
  type        = string
  sensitive   = true
}
