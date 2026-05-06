# ADR 003: Google Sheets sobre DynamoDB para persistencia de gastos

## Estado
Aceptado

## Contexto
El bot necesita persistir registros de gastos y permitir al usuario consultarlos y editarlos de forma simple.

## Decisión
Elegimos **Google Sheets** sobre DynamoDB o RDS como storage de datos.

## Consecuencias

### Por qué Google Sheets
- **Costo: $0**: DynamoDB on-demand costaría ~$0.25/millón de writes, RDS mínimo ~$15/mes
- **UI gratis**: el usuario puede ver, filtrar y editar datos directamente sin frontend
- **Fórmulas nativas**: totales por categoría, promedios mensuales — sin código adicional
- **Acceso compartido**: compartir el sheet con otras personas es trivial vs gestionar IAM
- **Exportación**: descarga a Excel/CSV en 1 click

### Cuándo NO usaríamos Google Sheets
- Volumen > 10.000 filas (performance degradada)
- Múltiples usuarios concurrentes escribiendo (race conditions)
- Datos sensibles que no pueden estar en Google
- Necesidad de queries complejas (JOINs, agregaciones avanzadas)

### Comparativa

| Criterio | Google Sheets | DynamoDB |
|---|---|---|
| Costo mensual | $0 | ~$0-5 |
| UI para el usuario | Nativa | Requiere frontend |
| Escalabilidad | Baja | Alta |
| Queries avanzadas | Limitado | Limitado (NoSQL) |
| Latencia de write | ~200ms | ~1-5ms |

Para un bot personal con < 100 registros/mes, Google Sheets es la elección correcta.
