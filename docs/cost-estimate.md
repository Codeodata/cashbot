# Cost Estimate — CashBot

Estimación para uso personal (~50 mensajes/día, región us-east-1).

---

## Desglose mensual

### Compute

| Componente | Free Tier | Uso estimado | Costo/mes |
|---|---|---|---|
| Lambda invocaciones | 1M requests gratis | ~1,500/mes | $0.00 |
| Lambda duración | 400,000 GB-s gratis | ~150 GB-s | $0.00 |

### Storage

| Componente | Detalle | Costo/mes |
|---|---|---|
| ECR — imagen almacenada | ~200 MB | $0.02 |
| ECR — data transfer | Minimal | $0.00 |

### Observabilidad

| Componente | Free Tier | Uso estimado | Costo/mes |
|---|---|---|---|
| CloudWatch Logs ingestion | 5 GB/mes gratis | ~50 MB | $0.00 |
| CloudWatch Logs storage | 5 GB gratis | ~50 MB | $0.00 |

---

## Total estimado

| Escenario | Costo/mes |
|---|---|
| **Uso personal** (< 1,500 requests/mes) | **~$0.02** |
| **Uso moderado** (50,000 requests/mes) | **~$0.05** |
| **Uso alto** (500,000 requests/mes) | **~$0.30** |

---

## Comparativa con alternativas

| Arquitectura | Costo/mes | Observación |
|---|---|---|
| Lambda (este setup) | ~$0.02 | Ideal para bots personales |
| EC2 t3.micro | ~$8.50 | Se justifica con > 10M requests/mes |
| ECS Fargate (0.25 vCPU) | ~$12.00 | Overhead innecesario para este caso |

---

## Por qué este setup es casi gratuito

1. **Webhook over polling**: Lambda solo se invoca cuando llega un mensaje. Sin mensajes = sin costo.
2. **Serverless compute**: no hay instancias idle esperando tráfico.
3. **Google Sheets como DB**: elimina el costo de RDS (~$15-50/mes) o DynamoDB.

---

> El bot puede correr indefinidamente a costo prácticamente cero para uso personal,
> lo que valida la decisión de arquitectura serverless (ver ADR 001).
