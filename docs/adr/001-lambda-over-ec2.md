# ADR 001: Lambda sobre EC2 para ejecución del bot

## Estado
Aceptado

## Contexto
El bot de Telegram procesa mensajes de gastos de forma reactiva. El volumen es bajo e impredecible (0 a ~50 mensajes/día).

## Decisión
Elegimos **AWS Lambda** sobre EC2 o ECS para ejecutar el bot.

## Consecuencias

### Por qué Lambda
- **Costo casi cero**: con < 1M requests/mes se mantiene en free tier (~$0/mes)
- **Escala a 0**: sin mensajes, sin costo. Un t3.micro EC2 costaría ~$8/mes idle
- **No hay infraestructura que mantener**: sin OS patching, sin gestión de uptime
- **Integración nativa**: ECR → Lambda actualización en 1 comando

### Costo comparativo
| Solución | Costo/mes (50 msgs/día) |
|---|---|
| Lambda | ~$0 (free tier) |
| EC2 t3.micro (always on) | ~$8.50 |
| ECS Fargate (always on) | ~$12 |

### Trade-offs aceptados
- Cold start: 2-5 segundos en primera invocación tras período de inactividad
- Límite de 15 minutos de ejecución (no relevante para este use case)
- Sin estado local entre invocaciones (resuelto con Google Sheets como storage)

### Cuándo elegiríamos EC2/ECS
- Bot con polling activo (no webhook-based)
- Procesamiento de mensajes > 15 minutos
- Necesidad de estado en memoria entre requests
