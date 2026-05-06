# ADR 002: Amazon ECR sobre DockerHub para registry de imágenes

## Estado
Aceptado

## Contexto
Lambda Container Images requieren un registry de donde pullear la imagen. Necesitábamos elegir entre un registry privado de AWS o uno externo.

## Decisión
Elegimos **Amazon ECR** sobre DockerHub.

## Consecuencias

### Por qué ECR
- **Integración nativa con Lambda**: no requiere credenciales adicionales — IAM role es suficiente
- **Sin rate limiting**: DockerHub limita pulls a 100/6h para cuentas free (puede bloquear deploys en CI)
- **Latencia reducida**: imagen en la misma región que Lambda → cold starts más rápidos
- **Escaneo de vulnerabilidades**: ECR Basic Scanning gratis detecta CVEs en la imagen
- **Lifecycle policies**: limpieza automática de imágenes antiguas

### Costo
- ECR: $0.10/GB/mes. Una imagen de ~200MB = ~$0.02/mes
- DockerHub Free: 1 repo privado incluido, pero con rate limits

### Trade-offs aceptados
- Vendor lock-in con AWS (menor que alternativas como GitHub Registry en este contexto)
- Requiere `aws ecr get-login-password` antes de cada push

### Cuándo elegiríamos DockerHub/GitHub Registry
- Imagen pública que beneficia de CDN global de DockerHub
- Proyecto open source donde la visibilidad importa
- Multi-cloud deployment donde queremos un registry agnóstico
