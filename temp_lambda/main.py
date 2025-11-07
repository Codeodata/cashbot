import json
import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ----------------------
# Configuración de Google Sheets
# ----------------------
GOOGLE_CREDS_JSON = os.environ.get("GOOGLE_CREDS_JSON")  # JSON de credenciales como string
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")      # ID del Sheet

def get_sheet():
    """Autenticación con Google Sheets"""
    try:
        creds_dict = json.loads(GOOGLE_CREDS_JSON)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict,
            ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        return sheet
    except Exception as e:
        print(f"❌ Error al autenticar Google Sheets: {e}")
        return None

# ----------------------
# Función para enviar mensaje a Telegram
# ----------------------
def enviar_respuesta_telegram(chat_id, texto):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        print(f"✅ Mensaje enviado a Telegram: {texto}")
    except Exception as e:
        print(f"❌ Error enviando mensaje a Telegram: {e}")

# ----------------------
# Handler principal
# ----------------------
def lambda_handler(event, context):
    try:
        print("🔹 EVENTO COMPLETO:", json.dumps(event))

        # Parsear body
        body = event.get("body", event)
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError as e:
                print("❌ ERROR JSON:", str(e))
                return {"statusCode": 400, "body": json.dumps({"message": "Invalid JSON"})}

        print("🔹 BODY PARSEADO:", json.dumps(body))

        # Verificar message
        message = body.get("message")
        if not message:
            print("❌ NO HAY 'message'")
            return {"statusCode": 400, "body": json.dumps({"message": "No message in body"})}

        chat_id = message["chat"]["id"]
        text = message["text"]
        print(f"🔹 Mensaje del chat {chat_id}: {text}")

        # Aquí iría la llamada a Google Sheets y Telegram
        return {"statusCode": 200, "body": json.dumps({"message": "Processed successfully"})}

    except Exception as e:
        print("❌ ERROR GENERAL:", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
