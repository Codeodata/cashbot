variable "aws_region" {
  description = "Región de AWS donde se desplegará la infraestructura"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Perfil de AWS CLI a utilizar"
  type        = string
  default     = "user-lambda"
}

variable "environment" {
  description = "Ambiente de despliegue (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "function_name" {
  description = "Nombre de la función Lambda"
  type        = string
  default     = "asistente-gastos"
}

variable "ecr_repository_name" {
  description = "Nombre del repositorio ECR"
  type        = string
  default     = "asistente-gastos"
}

variable "image_tag" {
  description = "Tag de la imagen Docker a desplegar"
  type        = string
  default     = "latest"
}

variable "lambda_timeout" {
  description = "Timeout de la función Lambda en segundos"
  type        = number
  default     = 60
}

variable "lambda_memory" {
  description = "Memoria asignada a la función Lambda en MB"
  type        = number
  default     = 512
}

variable "log_retention_days" {
  description = "Días de retención de logs en CloudWatch"
  type        = number
  default     = 7
}

# Variables sensibles - deben pasarse de forma segura
variable "telegram_bot_token" {
  description = "Token del bot de Telegram"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "API Key de OpenAI"
  type        = string
  sensitive   = true
}

variable "google_sheet_id" {
  description = "ID de la hoja de Google Sheets"
  type        = string
  sensitive   = true
}

variable "google_credentials_json" {
  description = "Credenciales de Google Service Account en formato JSON (base64)"
  type        = string
  sensitive   = true
}
