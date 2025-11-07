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
        
        # SIMULAR éxito hasta que tengamos las credenciales reales
        print("🔸 SIMULANDO guardado en Google Sheets (credenciales no configuradas)")
        
        # Aquí iría la lógica real con Google Sheets
        # sheet = get_sheet()
        # if sheet:
        #     nueva_fila = [str(chat_id), monto, descripcion, "Pendiente"]
        #     sheet.append_row(nueva_fila)
        #     return f"✅ Gasto registrado: ${monto} - {descripcion}"
        # else:
        #     return "❌ Error conectando con Google Sheets"
        
        return f"✅ [SIMULADO] Gasto registrado: ${monto} - {descripcion}\n🔧 Configura credenciales para guardar en Google Sheets"
            
    except Exception as e:
        print(f"❌ ERROR en procesar_gasto: {str(e)}")
        return f"❌ Error procesando gasto: {str(e)}"
