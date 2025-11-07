output "ecr_repository_url" {
  value = aws_ecr_repository.asistente_gastos.repository_url
}


output "aws_account_id" {
  description = "ID de la cuenta de AWS"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "Región de AWS utilizada"
  value       = var.aws_region
}
