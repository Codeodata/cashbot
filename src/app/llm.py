import os
import json
from datetime import datetime
from openai import OpenAI

def procesar_gasto_con_openai(texto):
    """
    Procesa el texto del usuario con OpenAI para extraer información del gasto
    """
    try:
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        prompt = f"""Extrae la información del siguiente gasto y devuelve un JSON con:
- monto (número, sin símbolos ni separadores)
- categoria (string: Comida, Transporte, Entretenimiento, Servicios, Compras, Salud, Otros)
- descripcion (string breve)
- fecha (formato YYYY-MM-DD, usa la fecha actual si no se especifica)

Texto: "{texto}"

Responde SOLO con el JSON válido, sin markdown ni texto adicional.

Ejemplo de respuesta:
{{"monto": 20000, "categoria": "Comida", "descripcion": "almuerzo", "fecha": "2025-11-03"}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente financiero que extrae información de gastos. Respondes SOLO con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        resultado = response.choices[0].message.content.strip()
        print(f"Respuesta OpenAI: {resultado}")
        
        # Limpiar markdown si existe
        if resultado.startswith('```'):
            resultado = resultado.split('```')[1]
            if resultado.startswith('json'):
                resultado = resultado[4:]
        resultado = resultado.strip()
        
        # Parsear JSON
        gasto_info = json.loads(resultado)
        
        # Validar campos requeridos
        if not all(k in gasto_info for k in ['monto', 'categoria', 'descripcion']):
            print("Error: Faltan campos requeridos")
            return None
            
        # Agregar fecha actual si no existe
        if 'fecha' not in gasto_info:
            gasto_info['fecha'] = datetime.now().strftime('%Y-%m-%d')
        
        # Convertir monto a número si es string
        if isinstance(gasto_info['monto'], str):
            gasto_info['monto'] = float(gasto_info['monto'].replace(',', '').replace('$', ''))
        
        print(f"Gasto procesado: {gasto_info}")
        return gasto_info
        
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON: {str(e)}")
        print(f"Respuesta recibida: {resultado}")
        return None
    except Exception as e:
        print(f"Error en OpenAI: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
