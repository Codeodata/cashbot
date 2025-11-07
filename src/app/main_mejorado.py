import json
import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

print("🚀 Lambda iniciada - Con formato mejorado")

def get_sheet():
    """Autenticación con Google Sheets"""
    try:
        GOOGLE_CREDS_JSON = os.environ.get("GOOGLE_CREDS_JSON")
        GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
        
        creds_dict = json.loads(GOOGLE_CREDS_JSON)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict,
            ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        return sheet
    except Exception as e:
        print(f"❌ Error Google Sheets: {e}")
        return None

def procesar_gasto(texto, chat_id):
    """Procesar comando de gasto con formato mejorado"""
    try:
        print(f"🔸 Procesando: '{texto}' para chat_id: {chat_id}")

        partes = texto.split()
        if len(partes) < 3:
            return "❌ Formato incorrecto. Usa: /gasto [monto] [descripción]"

        monto = partes[1]
        descripcion = " ".join(partes[2:])
        
        # Obtener fecha actual en formato legible
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        print(f"🔸 Monto: {monto}, Descripción: {descripcion}, Fecha: {fecha_actual}")

        # Guardar en Google Sheets
        sheet = get_sheet()
        if sheet:
            print("🔸 Sheet obtenido, agregando fila...")
            
            # NUEVO FORMATO: ChatID, Fecha, Monto, Descripción
            nueva_fila = [
                str(chat_id),    # Columna 1: Chat ID
                fecha_actual,    # Columna 2: Fecha y hora
                monto,           # Columna 3: Monto
                descripcion      # Columna 4: Descripción
                # ❌ ELIMINADO: Estado "Pendiente"
            ]
            
            print(f"🔸 Fila a agregar: {nueva_fila}")
            sheet.append_row(nueva_fila)
            print("✅ Fila agregada exitosamente")
            
            return f"✅ Gasto registrado:\n💵 ${monto}\n📝 {descripcion}\n📅 {fecha_actual}"
        else:
            print("❌ No se pudo obtener el sheet")
            return "❌ Error conectando con Google Sheets"

    except Exception as e:
        print(f"❌ ERROR en procesar_gasto: {str(e)}")
        return f"❌ Error: {str(e)}"

def enviar_respuesta_telegram(chat_id, texto):
    """Enviar mensaje a Telegram"""
    try:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return
            
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": texto, 
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"🔸 Telegram response: {response.status_code}")
        
    except Exception as e:
        print(f"❌ ERROR Telegram: {str(e)}")

def lambda_handler(event, context):
    print("=" * 50)
    print("🔄 LAMBDA HANDLER INICIADO")
    print("=" * 50)
    
    try:
        # Parsear body
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
        
        print(f"🔹 BODY: {json.dumps(body, indent=2)}")
        
        # Verificar si es mensaje de Telegram
        if "message" in body:
            message = body["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            print(f"🔹 Mensaje: {text} del chat {chat_id}")
            
            # Procesar comandos
            respuesta = "🤖 Comando no reconocido. Usa /gasto [monto] [descripción]"
            
            if text.startswith("/start"):
                respuesta = """🤖 <b>Bot de Gastos Mejorado</b>
                
💵 <b>Para registrar gastos:</b>
<code>/gasto [monto] [descripción]</code>

📝 <b>Ejemplos:</b>
<code>/gasto 100 comida</code>
<code>/gasto 50 transporte</code>
<code>/gasto 200 supermercado</code>

✅ <b>Ahora con fecha automática y mejor formato!</b>"""
            
            elif text.startswith("/gasto"):
                respuesta = procesar_gasto(text, chat_id)
            
            print(f"🔹 Respuesta: {respuesta}")
            
            # Enviar respuesta a Telegram
            enviar_respuesta_telegram(chat_id, respuesta)
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "success",
                    "message": "Procesado",
                    "respuesta": respuesta
                })
            }
        else:
            print("❌ No hay 'message' en el body")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Formato inválido"})
            }

    except Exception as e:
        print(f"❌ ERROR GENERAL: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
