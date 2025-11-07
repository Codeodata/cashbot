import json
import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("🚀 Lambda iniciada - Debug mode ACTIVADO")

def get_sheet():
    """Autenticación con Google Sheets con debug completo"""
    try:
        print("🔸 Intentando autenticar con Google Sheets...")
        GOOGLE_CREDS_JSON = os.environ.get("GOOGLE_CREDS_JSON", "{}")
        GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
        
        print(f"🔸 GOOGLE_SHEET_ID: {GOOGLE_SHEET_ID}")
        print(f"🔸 GOOGLE_CREDS_JSON length: {len(GOOGLE_CREDS_JSON)}")
        
        if GOOGLE_CREDS_JSON == "{}" or not GOOGLE_SHEET_ID:
            print("❌ Variables de Google no configuradas")
            return None
            
        creds_dict = json.loads(GOOGLE_CREDS_JSON)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict,
            ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        print("✅ Google Sheets autenticado EXITOSAMENTE")
        return sheet
        
    except Exception as e:
        print(f"❌ ERROR en get_sheet: {str(e)}")
        return None

def procesar_gasto(texto, chat_id):
    """Procesar comando de gasto con debug completo"""
    try:
        print(f"🔸 Procesando gasto: '{texto}' para chat_id: {chat_id}")
        
        partes = texto.split()
        if len(partes) < 3:
            return "❌ Formato incorrecto. Usa: /gasto [monto] [descripción]"
        
        monto = partes[1]
        descripcion = " ".join(partes[2:])
        
        print(f"🔸 Monto: {monto}, Descripción: {descripcion}")
        
        # Intentar guardar en Google Sheets
        sheet = get_sheet()
        if sheet:
            print("🔸 Sheet obtenido, agregando fila...")
            nueva_fila = [str(chat_id), monto, descripcion, "Pendiente"]
            print(f"🔸 Fila a agregar: {nueva_fila}")
            
            sheet.append_row(nueva_fila)
            print("✅ Fila agregada exitosamente a Google Sheets")
            return f"✅ Gasto registrado: ${monto} - {descripcion}"
        else:
            print("❌ No se pudo obtener el sheet")
            return "❌ Error conectando con Google Sheets"
            
    except Exception as e:
        print(f"❌ ERROR en procesar_gasto: {str(e)}")
        return f"❌ Error procesando gasto: {str(e)}"

def enviar_respuesta_telegram(chat_id, texto):
    """Enviar mensaje a Telegram con debug completo"""
    try:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        
        print(f"🔸 TELEGRAM_BOT_TOKEN: {bot_token}")
        
        if not bot_token or bot_token == "test_token":
            print("❌ TELEGRAM_BOT_TOKEN no configurado o es test")
            return
            
        print(f"🔸 Enviando a Telegram: chat_id={chat_id}, texto={texto}")
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": texto, 
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"🔸 Status Code Telegram: {response.status_code}")
        print(f"🔸 Response Telegram: {response.text}")
        
        response.raise_for_status()
        print("✅ Mensaje enviado EXITOSAMENTE a Telegram")
        
    except Exception as e:
        print(f"❌ ERROR enviando a Telegram: {str(e)}")

def lambda_handler(event, context):
    print("=" * 50)
    print("🔄 LAMBDA HANDLER INICIADO")
    print("=" * 50)
    
    try:
        # Debug completo del evento
        print("🔹 EVENTO RAW:")
        print(json.dumps(event, indent=2))
        
        # Parsear body
        body = event.get("body", "{}")
        print(f"🔹 BODY (raw): {body}")
        
        if isinstance(body, str):
            try:
                body = json.loads(body)
                print("🔹 BODY parseado como JSON")
            except json.JSONDecodeError as e:
                print(f"❌ ERROR parsing JSON: {e}")
                body = {}
        
        print(f"🔹 BODY (parsed): {json.dumps(body, indent=2)}")
        
        # Verificar si es mensaje de Telegram
        if "message" in body:
            message = body["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            print(f"🔹 Mensaje de Telegram recibido:")
            print(f"   Chat ID: {chat_id}")
            print(f"   Text: {text}")
            
            # Procesar comandos
            respuesta = "🤖 Comando no reconocido. Usa /gasto [monto] [descripción]"
            
            if text.startswith("/start"):
                respuesta = "🤖 Bot de Gastos activo! Usa:\n/gasto [monto] [descripción]\nEj: /gasto 100 comida"
            elif text.startswith("/gasto"):
                respuesta = procesar_gasto(text, chat_id)
            
            print(f"🔹 Respuesta generada: {respuesta}")
            
            # Enviar respuesta a Telegram
            enviar_respuesta_telegram(chat_id, respuesta)
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "success",
                    "message": "Mensaje procesado",
                    "respuesta": respuesta
                })
            }
        else:
            print("❌ No se encontró 'message' en el body")
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Formato inválido - no es mensaje de Telegram"
                })
            }

    except Exception as e:
        print(f"❌ ERROR GENERAL en handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"Error interno: {str(e)}"
            })
        }
