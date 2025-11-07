import json
import os
import requests

def procesar_gasto(texto, chat_id):
    """Procesar gasto en modo simulación"""
    try:
        partes = texto.split()
        if len(partes) < 3:
            return "❌ Formato: /gasto [monto] [descripción]"

        monto = partes[1]
        descripcion = " ".join(partes[2:])
        
        # Modo simulación - siempre funciona
        return f"✅ Gasto registrado: ${monto} - {descripcion}\n📝 (Modo simulación - configurar Google Sheets para guardar)"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

# El resto del código permanece igual...
def lambda_handler(event, context):
    try:
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
        
        if "message" in body:
            message = body["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            respuesta = "🤖 Usa /gasto [monto] [descripción]"
            
            if text.startswith("/start"):
                respuesta = "🤖 Bot de Gastos activo! Usa /gasto [monto] [descripción]"
            elif text.startswith("/gasto"):
                respuesta = procesar_gasto(text, chat_id)
            
            # Enviar a Telegram
            bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
            if bot_token:
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", 
                             json={"chat_id": chat_id, "text": respuesta})
            
            return {"statusCode": 200, "body": json.dumps({"message": "OK"})}
        
        return {"statusCode": 400, "body": json.dumps({"error": "No message"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
