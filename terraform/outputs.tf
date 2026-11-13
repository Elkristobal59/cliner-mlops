output "s3_bucket_name" {
  description = "Bucket AWS S3 provisionné pour le Data Lake et le Model Registry LoRA"
  value       = aws_s3_bucket.cliner_storage.bucket
}

output "s3_bucket_arn" {
  description = "ARN du bucket S3 CliNER-MLOps"
  value       = aws_s3_bucket.cliner_storage.arn
}

output "ec2_gpu_instance_id" {
  description = "ID de l'instance EC2 GPU (utilisé par ec2_manager.py pour le Start/Stop FinOps)"
  value       = aws_instance.cliner_gpu_worker.id
}

output "fastapi_swagger_url" {
  description = "URL de la documentation interactive OpenAPI (Swagger /docs)"
  value       = "http://${aws_instance.cliner_gpu_worker.public_ip}:8000/docs"
}

