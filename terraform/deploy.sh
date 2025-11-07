#!/bin/bash
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
export AWS_PROFILE="user-lambda"
export AWS_REGION="us-east-1"
export IMAGE_TAG="${1:-latest}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Despliegue Asistente de Gastos${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Configuración:${NC}"
echo -e "  AWS Profile: ${GREEN}$AWS_PROFILE${NC}"
echo -e "  AWS Region: ${GREEN}$AWS_REGION${NC}"
echo -e "  Image Tag: ${GREEN}$IMAGE_TAG${NC}"
echo ""

# Verificar AWS CLI
echo -e "${YELLOW}🔍 Verificando AWS CLI...${NC}"
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no está instalado${NC}"
    exit 1
fi

# Verificar perfil
if ! aws configure list --profile $AWS_PROFILE &> /dev/null; then
    echo -e "${RED}❌ Perfil $AWS_PROFILE no configurado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ AWS CLI configurado correctamente${NC}"

# Verificar Docker
echo -e "${YELLOW}🔍 Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker disponible${NC}"

# Verificar Terraform
echo -e "${YELLOW}🔍 Verificando Terraform...${NC}"
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Terraform disponible${NC}"
echo ""

# Obtener ECR Repository URL
echo -e "${YELLOW}📦 Obteniendo información de ECR...${NC}"
if [ ! -d "terraform" ] || [ ! -f "terraform/terraform.tfstate" ]; then
    echo -e "${RED}❌ Terraform no ha sido inicializado. Ejecuta primero:${NC}"
    echo -e "   cd terraform && terraform init && terraform apply"
    exit 1
fi

export ECR_REPO=$(terraform -chdir=terraform output -raw ecr_repository_url 2>/dev/null || echo "")
if [ -z "$ECR_REPO" ]; then
    echo -e "${RED}❌ No se pudo obtener la URL del ECR${NC}"
    exit 1
fi
echo -e "${GREEN}✅ ECR Repository: $ECR_REPO${NC}"
echo ""

# Login en ECR
echo -e "${YELLOW}🔐 Autenticando en ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | \
  docker login --username AWS --password-stdin $ECR_REPO
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Login exitoso en ECR${NC}"
else
    echo -e "${RED}❌ Error en login de ECR${NC}"
    exit 1
fi
echo ""

# Build de la imagen
echo -e "${YELLOW}🐳 Construyendo imagen Docker...${NC}"
docker buildx build --platform linux/amd64 -t asistente-gastos:$IMAGE_TAG .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"
else
    echo -e "${RED}❌ Error construyendo imagen${NC}"
    exit 1
fi
echo ""

# Tag de la imagen
echo -e "${YELLOW}🏷️  Etiquetando imagen...${NC}"
docker tag asistente-gastos:$IMAGE_TAG $ECR_REPO:$IMAGE_TAG
docker tag asistente-gastos:$IMAGE_TAG $ECR_REPO:latest
echo -e "${GREEN}✅ Imagen etiquetada${NC}"
echo ""

# Push al ECR
echo -e "${YELLOW}📤 Subiendo imagen a ECR...${NC}"
docker push $ECR_REPO:$IMAGE_TAG
docker push $ECR_REPO:latest
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Imagen subida exitosamente${NC}"
else
    echo -e "${RED}❌ Error subiendo imagen${NC}"
    exit 1
fi
echo ""

# Actualizar Lambda
echo -e "${YELLOW}⚡ Actualizando función Lambda...${NC}"
aws lambda update-function-code \
  --function-name asistente-gastos \
  --image-uri $ECR_REPO:$IMAGE_TAG \
  --region $AWS_REGION \
  --profile $AWS_PROFILE \
  --no-cli-pager

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Lambda actualizada${NC}"
else
    echo -e "${RED}❌ Error actualizando Lambda${NC}"
    exit 1
fi
echo ""

# Esperar a que la función se actualice
echo -e "${YELLOW}⏳ Esperando a que Lambda termine de actualizarse...${NC}"
aws lambda wait function-updated \
  --function-name asistente-gastos \
  --region $AWS_REGION \
  --profile $AWS_PROFILE

echo -e "${GREEN}✅ Lambda lista${NC}"
echo ""

# Verificar estado
echo -e "${YELLOW}🔍 Verificando despliegue...${NC}"
LAMBDA_INFO=$(aws lambda get-function \
  --function-name asistente-gastos \
  --region $AWS_REGION \
  --profile $AWS_PROFILE \
  --query '{ImageUri: Code.ImageUri, LastModified: Configuration.LastModified, State: Configuration.State}' \
  --output json)

echo "$LAMBDA_INFO" | jq .
echo ""

# Obtener Lambda URL
export LAMBDA_URL=$(terraform -chdir=terraform output -raw lambda_function_url 2>/dev/null || echo "")
if [ -n "$LAMBDA_URL" ]; then
    echo -e "${GREEN}✅ Lambda URL: $LAMBDA_URL${NC}"
else
    echo -e "${YELLOW}⚠️  No se pudo obtener Lambda URL${NC}"
fi
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Despliegue completado exitosamente!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo -e "  1. Configurar webhook de Telegram:"
echo -e "     ${BLUE}curl -X POST \"https://api.telegram.org/bot\$TELEGRAM_TOKEN/setWebhook\" \\${NC}"
echo -e "     ${BLUE}  -d \"url=${LAMBDA_URL}webhook/\$TELEGRAM_TOKEN\"${NC}"
echo ""
echo -e "  2. Verificar logs:"
echo -e "     ${BLUE}aws logs tail /aws/lambda/asistente-gastos --profile $AWS_PROFILE --follow${NC}"
echo ""
echo -e "  3. Probar bot enviando mensaje en Telegram"
echo ""
