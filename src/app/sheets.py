import os
import json
import base64
import gspread
from google.oauth2.service_account import Credentials

def registrar_en_sheets(gasto_info):
    """
    Registra el gasto en Google Sheets
    """
    try:
        # Decodificar credenciales
        creds_base64 = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        
        if not creds_base64:
            print("Error: GOOGLE_CREDENTIALS_JSON no está definido")
            return False
            
        creds_json = base64.b64decode(creds_base64).decode('utf-8')
        creds_dict = json.loads(creds_json)
        
        # Autenticar
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        
        # Abrir hoja
        sheet_id = os.environ.get('GOOGLE_SHEET_ID')
        
        if not sheet_id:
            print("Error: GOOGLE_SHEET_ID no está definido")
            return False
            
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1  # Primera hoja
        
        # Verificar si hay headers, si no, agregarlos
        try:
            headers = worksheet.row_values(1)
            if not headers or len(headers) == 0:
                worksheet.append_row(['Fecha', 'Monto', 'Categoría', 'Descripción'])
                print("Headers agregados a la hoja")
        except Exception as e:
            print(f"Error verificando headers: {str(e)}")
            worksheet.append_row(['Fecha', 'Monto', 'Categoría', 'Descripción'])
        
        # Agregar fila
        nueva_fila = [
            gasto_info['fecha'],
            gasto_info['monto'],
            gasto_info['categoria'],
            gasto_info['descripcion']
        ]
        
        worksheet.append_row(nueva_fila)
        print(f"Gasto registrado en Sheets: {nueva_fila}")
        
        return True
        
    except Exception as e:
        print(f"Error en Sheets: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
