# DR Runbook — CashBot

## Objetivos de Recuperación

| Métrica | Target | Justificación |
|---|---|---|
| **RTO** | < 5 minutos | `terraform apply` recrea Lambda + webhook en menos de 5 min |
| **RPO** | 0 minutos | Google Sheets es la fuente de verdad — persiste independientemente |

> El bajo RTO/RPO es una consecuencia directa de elegir arquitectura serverless + storage externo.

---

## Escenarios de Falla

### Escenario 1: Lambda no responde a mensajes de Telegram

**Síntomas:** Bot no responde, sin errores en CloudWatch.

**Diagnóstico:**
```bash
# Verificar que el webhook está activo
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo

# Ver últimas invocaciones en CloudWatch
aws logs tail /aws/lambda/<function-name> --since 1h

# Verificar que Lambda tiene permisos para escribir en Sheets
aws lambda get-function-configuration --function-name <function-name>
```

**Resolución:**
```bash
# Reconfigurar webhook
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -d "url=<LAMBDA_URL>"
```

---

### Escenario 2: Imagen Docker corrompida en ECR

**RTO:** ~3 minutos.

```bash
# Rebuildear y pushear imagen
docker buildx build --platform linux/amd64 -t cashbot:latest .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ECR_URI>
docker tag cashbot:latest <ECR_URI>:latest
docker push <ECR_URI>:latest

# Actualizar Lambda para usar nueva imagen
aws lambda update-function-code \
  --function-name <function-name> \
  --image-uri <ECR_URI>:latest
```

---

### Escenario 3: Pérdida completa de infraestructura AWS

**RTO:** < 5 minutos.
**RPO:** 0 minutos (datos en Google Sheets, código en Git).

```bash
# 1. Clonar repo
git clone https://github.com/Codeodata/cashbot.git && cd cashbot

# 2. Configurar variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Editar con los valores correctos

# 3. Recrear toda la infraestructura
cd terraform
terraform init
terraform apply

# 4. Buildear y pushear imagen
./deploy.sh

# 5. Verificar
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

**Total:** ~5 minutos desde cero.

---

### Escenario 4: Google Sheets accidentalmente borrado

**RPO:** Depende de la frecuencia de backups manuales (recomendado: exportar a Drive mensualmente).

```
Google Sheets → File → Download → Excel (.xlsx)
Almacenar en Google Drive con nombre: cashbot-backup-YYYY-MM.xlsx
```

---

## Checklist post-recuperación

- [ ] Bot responde a `/start` en Telegram
- [ ] Registrar un gasto de prueba y verificar que aparece en Google Sheets
- [ ] CloudWatch muestra invocaciones exitosas (status 200)
- [ ] Sin errores en CloudWatch Logs
