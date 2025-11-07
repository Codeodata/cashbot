# 🚀 Guía de Despliegue - Asistente de Gastos con OpenAI

## 📋 Prerequisitos

- AWS CLI configurado con el perfil `user-lambda`
- Docker instalado
- Terraform >= 1.0
- Credenciales configuradas:
  - Token de Bot de Telegram
  - API Key de OpenAI
  - Google Service Account JSON
  - Google Sheet ID

---

## 🔧 Paso 1: Configurar AWS CLI Profile

```bash
# Verificar que el perfil user-lambda existe
aws configure list-profiles

# Si no existe, configurarlo
aws configure --profile user-lambda
# AWS Access Key ID: [tu_access_key]
# AWS Secret Access Key: [tu_secret_key]
# Default region: us-east-1
# Default output format: json

# Verificar configuración
aws sts get-caller-identity --profile user-lambda
```

---

## 🏗️ Paso 2: Preparar Terraform

```bash
# Ir al directorio de terraform
cd terraform

# Copiar el archivo de ejemplo
cp terraform.tfvars.example terraform.tfvars

# Editar con tus valores reales
nano terraform.tfvars
```

**Contenido de `terraform.tfvars`:**
```hcl
aws_region  = "us-east-1"
aws_profile = "user-lambda"
environment = "prod"

function_name       = "asistente-gastos"
ecr_repository_name = "asistente-gastos"
image_tag           = "v1"
lambda_timeout      = 60
lambda_memory       = 512

telegram_bot_token      = "TU_TOKEN_REAL"
openai_api_key          = "sk-TU_KEY_REAL"
google_sheet_id         = "TU_SHEET_ID"
google_credentials_json = "BASE64_DE_TU_JSON"
```

---

## 🎯 Paso 3: Crear Infraestructura con Terraform

```bash
# Inicializar Terraform
terraform init

# Ver plan de ejecución
terraform plan

# Aplicar cambios
terraform apply

# Guardar outputs importantes
terraform output ecr_repository_url > ../ecr_url.txt
terraform output lambda_function_url > ../lambda_url.txt
```

**Outputs que obtendrás:**
```
ecr_repository_url = "123456789012.dkr.ecr.us-east-1.amazonaws.com/asistente-gastos"
lambda_function_url = "https://abc123xyz.lambda-url.us-east-1.on.aws/"
lambda_function_name = "asistente-gastos"
```

---

## 🐳 Paso 4: Build y Push de Docker Image

```bash
# Volver al directorio raíz del proyecto
cd ..

# Obtener variables de Terraform
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile user-lambda --query Account --output text)
export AWS_REGION="us-east-1"
export ECR_REPO=$(terraform -chdir=terraform output -raw ecr_repository_url)
export IMAGE_TAG="v1"

# Login en ECR
aws ecr get-login-password --region $AWS_REGION --profile user-lambda | \
  docker login --username AWS --password-stdin $ECR_REPO

# Build de la imagen (multi-arquitectura)
docker buildx build --platform linux/amd64 -t asistente-gastos:$IMAGE_TAG .

# Tag de la imagen
docker tag asistente-gastos:$IMAGE_TAG $ECR_REPO:$IMAGE_TAG
docker tag asistente-gastos:$IMAGE_TAG $ECR_REPO:latest

# Push al ECR
docker push $ECR_REPO:$IMAGE_TAG
docker push $ECR_REPO:latest
```

---

## 🔄 Paso 5: Actualizar Lambda Function

```bash
# Actualizar código de la función
aws lambda update-function-code \
  --function-name asistente-gastos \
  --image-uri $ECR_REPO:$IMAGE_TAG \
  --region $AWS_REGION \
  --profile user-lambda

# Esperar a que termine la actualización
aws lambda wait function-updated \
  --function-name asistente-gastos \
  --region $AWS_REGION \
  --profile user-lambda

# Verificar el despliegue
aws lambda get-function \
  --function-name asistente-gastos \
  --region $AWS_REGION \
  --profile user-lambda \
  --query '{ImageUri: Code.ImageUri, LastModified: Configuration.LastModified, State: Configuration.State}'
```

---

## 🤖 Paso 6: Configurar Webhook de Telegram

```bash
# Obtener la URL de Lambda
export LAMBDA_URL=$(terraform -chdir=terraform output -raw lambda_function_url)
export TELEGRAM_TOKEN="tu_token_real"

# Configurar webhook
curl -X POST \
  "https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook" \
  -d "url=${LAMBDA_URL}webhook/$TELEGRAM_TOKEN"

# Verificar webhook
curl "https://api.telegram.org/bot$TELEGRAM_TOKEN/getWebhookInfo"
```

**Respuesta esperada:**
```json
{
  "ok": true,
  "result": {
    "url": "https://abc123xyz.lambda-url.us-east-1.on.aws/webhook/123456...",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## 🧪 Paso 7: Pruebas

### Prueba Local (antes de desplegar)
```bash
docker run -p 9000:8080 --env-file .env asistente-gastos:$IMAGE_TAG

curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{"message":{"text":"gasté 20000 en empanadas","chat":{"id":12345}}}'
```

### Prueba en Lambda
```bash
# Prueba directa a la Lambda URL
curl -X POST "${LAMBDA_URL}" \
  -H "Content-Type: application/json" \
  -d '{"message":{"text":"gasté 45000 en mercado","chat":{"id":98765}}}'
```

### Prueba con Telegram
Envía un mensaje directo a tu bot:
```
Gasté 20000 en empanadas
```

---

## 📊 Paso 8: Monitoreo y Logs

```bash
# Ver logs en tiempo real
aws logs tail /aws/lambda/asistente-gastos \
  --region $AWS_REGION \
  --profile user-lambda \
  --since 5m \
  --follow

# Ver métricas de la Lambda
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=asistente-gastos \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region $AWS_REGION \
  --profile user-lambda

# Ver alarmas activas
aws cloudwatch describe-alarms \
  --alarm-name-prefix asistente-gastos \
  --region $AWS_REGION \
  --profile user-lambda
```

---

## 🔄 Actualizaciones Posteriores

### Actualizar código (nueva versión)

```bash
# 1. Incrementar versión
export IMAGE_TAG="v2"

# 2. Build y push
docker buildx build --platform linux/amd64 -t asistente-gastos:$IMAGE_TAG .
docker tag asistente-gastos:$IMAGE_TAG $ECR_REPO:$IMAGE_TAG
docker push $ECR_REPO:$IMAGE_TAG

# 3. Actualizar Lambda
aws lambda update-function-code \
  --function-name asistente-gastos \
  --image-uri $ECR_REPO:$IMAGE_TAG \
  --region $AWS_REGION \
  --profile user-lambda

# 4. Actualizar terraform
cd terraform
terraform apply -var="image_tag=$IMAGE_TAG"
```

### Actualizar variables de entorno

```bash
aws lambda update-function-configuration \
  --function-name asistente-gastos \
  --environment Variables="{
    TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN,
    OPENAI_API_KEY=$OPENAI_KEY,
    GOOGLE_SHEET_ID=$SHEET_ID,
    GOOGLE_CREDENTIALS_JSON=$GOOGLE_CREDS
  }" \
  --region $AWS_REGION \
  --profile user-lambda
```

---

## 🧹 Limpieza y Destrucción

```bash
# Eliminar webhook de Telegram
curl -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/deleteWebhook"

# Destruir infraestructura
cd terraform
terraform destroy

# Eliminar imágenes de ECR manualmente si es necesario
aws ecr batch-delete-image \
  --repository-name asistente-gastos \
  --image-ids imageTag=v1 imageTag=v2 imageTag=latest \
  --region $AWS_REGION \
  --profile user-lambda
```

---

## 📝 Script de Despliegue Rápido

Crea un archivo `deploy.sh`:

```bash
#!/bin/bash
set -e

export AWS_PROFILE="user-lambda"
export AWS_REGION="us-east-1"
export IMAGE_TAG="${1:-v1}"

echo "🚀 Iniciando despliegue con tag: $IMAGE_TAG"

# Variables
export ECR_REPO=$(terraform -chdir=terraform output -raw ecr_repository_url)

# Login ECR
echo "🔐 Login en ECR..."
aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | \
  docker login --username AWS --password-stdin $ECR_REPO

# Build
echo "🐳 Building imagen..."
docker buildx build --platform linux/amd64 -t asistente-gastos:$IMAGE_TAG .

# Tag y Push
echo "📤 Pusheando a ECR..."
docker tag asistente-gastos:$IMAGE_TAG $ECR_REPO:$IMAGE_TAG
docker push $ECR_REPO:$IMAGE_TAG

# Actualizar Lambda
echo "⚡ Actualizando Lambda..."
aws lambda update-function-code \
  --function-name asistente-gastos \
  --image-uri $ECR_REPO:$IMAGE_TAG \
  --region $AWS_REGION \
  --profile $AWS_PROFILE

echo "✅ Despliegue completado!"
```

Uso:
```bash
chmod +x deploy.sh
./deploy.sh v3
```

---

## 🆘 Troubleshooting

### Error: "No se puede conectar a AWS"
```bash
# Verificar configuración del perfil
aws configure list --profile user-lambda

# Verificar credenciales
aws sts get-caller-identity --profile user-lambda
```

### Error: "Lambda timeout"
```bash
# Aumentar timeout
aws lambda update-function-configuration \
  --function-name asistente-gastos \
  --timeout 120 \
  --region $AWS_REGION \
  --profile user-lambda
```

### Error: "Memoria insuficiente"
```bash
# Aumentar memoria
aws lambda update-function-configuration \
  --function-name asistente-gastos \
  --memory-size 1024 \
  --region $AWS_REGION \
  --profile user-lambda
```

### Ver errores específicos
```bash
# Últimos 50 eventos con ERROR
aws logs filter-log-events \
  --log-group-name /aws/lambda/asistente-gastos \
  --filter-pattern "ERROR" \
  --max-items 50 \
  --region $AWS_REGION \
  --profile user-lambda
```

---

## ✅ Checklist de Despliegue

- [ ] AWS CLI configurado con perfil `user-lambda`
- [ ] Terraform instalado y configurado
- [ ] Variables sensibles en `terraform.tfvars`
- [ ] `terraform apply` ejecutado exitosamente
- [ ] Imagen Docker buildeada y pusheada
- [ ] Lambda actualizada con nueva imagen
- [ ] Webhook de Telegram configurado
- [ ] Prueba exitosa enviando mensaje al bot
- [ ] Logs visibles en CloudWatch
- [ ] Alarmas configuradas y funcionando

---

## 📚 Recursos Útiles

- [Documentación Terraform AWS](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda con Contenedores](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Google Sheets API](https://developers.google.com/sheets/api)
