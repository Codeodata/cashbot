import json
import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

print("🚀 Lambda iniciada - Bot interactivo")

def get_sheet():
    """Autenticación con Google Sheets"""
    try:
        GOOGLE_CREDS_JSON = os.environ.get("GOOGLE_CREDS_JSON")
        GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
        
        if not GOOGLE_CREDS_JSON or not GOOGLE_SHEET_ID:
            print("❌ Variables de Google no configuradas")
            return None
            
        creds_dict = json.loads(GOOGLE_CREDS_JSON)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict,
            ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        print("✅ Google Sheets conectado")
        return sheet
    except Exception as e:
        print(f"❌ Error Google Sheets: {e}")
        return None

def procesar_gasto(texto, chat_id):
    """Procesar comando de gasto de forma interactiva"""
    try:
        print(f"🔸 Procesando gasto: '{texto}'")

        partes = texto.split()
        if len(partes) < 3:
            return "❌ ¡Ups! Formato incorrecto. 🤔\n\n💡 <b>Usa así:</b>\n<code>/gasto [monto] [descripción]</code>\n\n📝 <b>Ejemplo:</b>\n<code>/gasto 15000 almuerzo</code>"

        monto = partes[1]
        descripcion = " ".join(partes[2:])
        
        # Validar que el monto sea numérico
        try:
            float(monto)
        except ValueError:
            return f"❌ El monto '<b>{monto}</b>' no es válido. 🧮\n\n💡 <b>Usa solo números:</b>\n<code>/gasto 15000 comida</code>"
        
        # Obtener fecha actual
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        print(f"🔸 Registrando: ${monto} - {descripcion}")

        # Guardar en Google Sheets
        sheet = get_sheet()
        if sheet:
            # Formato: ChatID, Fecha, Monto, Descripción
            nueva_fila = [str(chat_id), fecha_actual, monto, descripcion]
            sheet.append_row(nueva_fila)
            
            # Respuesta interactiva y amigable
            return f"""✅ <b>¡Gasto registrado exitosamente! 🎉</b>

💵 <b>Monto:</b> ${monto}
📝 <b>Descripción:</b> {descripcion}
📅 <b>Fecha:</b> {fecha_actual}

💡 <b>¿Quieres registrar otro gasto?</b>
<code>/gasto [monto] [descripción]</code>"""
        else:
            return "❌ ¡Ups! No pude conectar con Google Sheets. 📊\n\n🔧 <b>Revisa la configuración o intenta más tarde.</b>"

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return f"❌ ¡Ups! Ocurrió un error inesperado. 🔧\n\n📞 <b>Error:</b> {str(e)}"

def enviar_respuesta_telegram(chat_id, texto):
    """Enviar mensaje a Telegram de forma robusta"""
    try:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            print("❌ No hay token de Telegram")
            return False
            
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": texto, 
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Mensaje enviado a Telegram")
            return True
        else:
            print(f"❌ Error Telegram: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR enviando a Telegram: {str(e)}")
        return False

def lambda_handler(event, context):
    print("=" * 50)
    print("🔄 LAMBDA INICIADA - Bot interactivo")
    print("=" * 50)
    
    try:
        # Debug del evento
        print("🔹 Evento recibido")
        
        # Parsear body
        body = event.get("body", "{}")
        if isinstance(body, str):
            try:
                body = json.loads(body)
                print("✅ Body parseado como JSON")
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON: {e}")
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "JSON inválido"})
                }
        
        print(f"🔹 Body: {json.dumps(body, indent=2)}")
        
        # Verificar si es mensaje de Telegram
        if "message" in body:
            message = body["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()
            
            print(f"🔹 Mensaje de {chat_id}: '{text}'")
            
            # Procesar comandos
            respuesta = """🤖 <b>¡Hola! Soy tu asistente de gastos 💰</b>

No reconozco ese comando. ¿En qué puedo ayudarte?

💡 <b>Comandos disponibles:</b>
<code>/start</code> - Ver mensaje de bienvenida
<code>/gasto [monto] [descripción]</code> - Registrar un gasto
<code>/help</code> - Ver ayuda

📝 <b>Ejemplo:</b>
<code>/gasto 25000 cena con amigos</code>"""
            
            if text.startswith("/start"):
                respuesta = """🤖 <b>¡Bienvenido a tu Asistente de Gastos! 💰</b>

Estoy aquí para ayudarte a registrar y organizar tus gastos de forma fácil y rápida.

💡 <b>¿Cómo usar?</b>
<code>/gasto [monto] [descripción]</code>

📝 <b>Ejemplos:</b>
<code>/gasto 15000 almuerzo</code>
<code>/gasto 50000 supermercado</code>
<code>/gasto 12000 transporte</code>

✅ <b>¡Empecemos! Escribe tu primer gasto:</b>"""
            
            elif text.startswith("/gasto"):
                respuesta = procesar_gasto(text, chat_id)
            
            elif text.startswith("/help") or text == "/ayuda":
                respuesta = """🆘 <b>Centro de Ayuda</b>

💡 <b>Comandos disponibles:</b>
<code>/start</code> - Mensaje de bienvenida
<code>/gasto [monto] [descripción]</code> - Registrar gasto
<code>/help</code> - Esta ayuda

📝 <b>Formato correcto:</b>
<code>/gasto [monto] [descripción]</code>

🎯 <b>Ejemplos válidos:</b>
<code>/gasto 15000 comida</code>
<code>/gasto 5000 café</code>
<code>/gasto 30000 gasolina</code>

❌ <b>Ejemplos incorrectos:</b>
<code>/gasto comida</code> (falta monto)
<code>/gasto 15000</code> (falta descripción)"""
            
            print(f"🔹 Respuesta: {respuesta}")
            
            # Enviar respuesta a Telegram
            enviado = enviar_respuesta_telegram(chat_id, respuesta)
            
            if enviado:
                return {
                    "statusCode": 200,
                    "body": json.dumps({"status": "success", "message": "Mensaje procesado"})
                }
            else:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Error enviando a Telegram"})
                }
                
        else:
            print("❌ No es mensaje de Telegram")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No es mensaje de Telegram"})
            }

    except Exception as e:
        print(f"❌ ERROR GENERAL: {str(e)}")
        # Intentar enviar mensaje de error al usuario
        try:
            if 'chat_id' in locals():
                error_msg = "❌ ¡Ups! Ocurrió un error inesperado. 🔧\n\nPor favor, intenta de nuevo en un momento."
                enviar_respuesta_telegram(chat_id, error_msg)
        except:
            pass
            
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
