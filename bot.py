from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import Update
from dotenv import load_dotenv
import os
import google.generativeai as genai
import asyncio
import time
import json

# Cargar variables de entorno
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Cargar resoluciones JCE
def load_jce_resolutions():
    """Cargar resoluciones oficiales de la JCE"""
    resolutions = {}
    try:
        if os.path.exists("jce_resolutions.json"):
            with open("jce_resolutions.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                for category, category_resolutions in data.items():
                    if category != "fecha_actualizacion":
                        resolutions.update(category_resolutions)
        return resolutions
    except Exception as e:
        print(f"Error cargando resoluciones: {e}")
        return {}

# Cargar resoluciones al inicio
JCE_RESOLUTIONS = load_jce_resolutions()

# Diccionario para mantener historial por usuario
mensajes = {}

# Respuestas predefinidas para cuando Gemini no esté disponible
RESPUESTAS_PREDEFINIDAS = {
    "acta_nacimiento": """📋 **Documentos para Acta de Nacimiento en RD:**

• Cédula de identidad del solicitante
• Si es para un menor: cédula de los padres
• Pago de la tasa correspondiente (RD$ 500-800)
• Solicitud en formulario oficial de la JCE
• Dirección: Oficina Central de la JCE, Santo Domingo

⏰ **Tiempo de entrega:** 3-5 días hábiles

**Oficinas JCE:**
📍 Santo Domingo: Av. 27 de Febrero
📍 Santiago: Av. Estrella Sadhalá
📍 La Romana: Av. Libertad
📍 San Pedro: Av. Independencia""",

    "cambio_nombre": """🔄 **Cambio de Nombre en RD:**

**Requisitos:**
• Solicitud formal con justificación
• Acta de nacimiento original
• Cédula de identidad
• Certificado de buena conducta
• Pago de tasas (RD$ 1,500-2,000)

**Proceso:**
1. Solicitud en JCE
2. Publicación en periódico (3 veces)
3. Audiencia judicial
4. Resolución final

⏰ **Duración:** 3-6 meses

**Justificaciones válidas:**
• Error ortográfico en el registro
• Nombres ofensivos o ridículos
• Adopción
• Matrimonio (apellido del cónyuge)""",

    "naturalizacion": """🇩🇴 **Naturalización en República Dominicana:**

**Requisitos:**
• Residencia legal por 2 años
• Acta de nacimiento apostillada
• Certificado de buena conducta
• Certificado médico
• Pago de tasas (RD$ 5,000-8,000)

**Documentos adicionales:**
• Pasaporte vigente
• Certificado de trabajo
• Comprobante de domicilio

⏰ **Proceso:** 6-12 meses

**Tipos de naturalización:**
• Por residencia (2 años)
• Por matrimonio (1 año)
• Por inversión (RD$ 200,000+)
• Por nacimiento en RD""",

    "apostilla": """📜 **Apostilla en República Dominicana:**

**¿Qué es?**
Certificación internacional que valida documentos para uso en el extranjero.

**Documentos que requieren apostilla:**
• Actas de nacimiento
• Certificados de estudios
• Documentos notariales
• Certificados de buena conducta

**Proceso:**
1. Solicitud en Ministerio de Relaciones Exteriores
2. Pago de tasa (RD$ 300-500)
3. Entrega en 24-48 horas

📍 **Ubicación:** Ministerio de Relaciones Exteriores, Santo Domingo

**Países que aceptan apostilla:**
• Estados Unidos, Canadá, México
• España, Francia, Alemania
• Reino Unido, Italia, Portugal
• Y otros 120+ países""",

    "cedula": """🆔 **Cédula de Identidad en RD:**

**Primera vez:**
• Acta de nacimiento
• Certificado médico
• Pago de tasa (RD$ 400)
• Foto reciente

**Renovación:**
• Cédula anterior
• Pago de tasa (RD$ 300)
• Foto reciente

**Pérdida/Robo:**
• Denuncia policial
• Pago de tasa (RD$ 500)
• Foto reciente

⏰ **Entrega:** 15-30 días hábiles

**Edad mínima:** 16 años
**Vigencia:** 10 años""",

    "matrimonio": """💒 **Matrimonio Civil en RD:**

**Requisitos:**
• Acta de nacimiento (ambos)
• Cédula de identidad (ambos)
• Certificado de soltería
• Certificado médico
• Pago de tasas (RD$ 1,000-1,500)

**Documentos adicionales:**
• Si es extranjero: pasaporte y certificado de soltería apostillado
• Si es divorciado: sentencia de divorcio
• Si es viudo: acta de defunción del cónyuge

**Proceso:**
1. Solicitud en JCE
2. Publicación de edictos (15 días)
3. Celebración del matrimonio
4. Entrega de acta

⏰ **Duración total:** 3-4 semanas""",

    "divorcio": """💔 **Divorcio en República Dominicana:**

**Tipos de divorcio:**
• Divorcio por mutuo acuerdo
• Divorcio por incompatibilidad
• Divorcio por falta

**Requisitos:**
• Acta de matrimonio
• Cédulas de identidad (ambos)
• Acuerdo de divorcio (si aplica)
• Pago de tasas (RD$ 2,000-4,000)

**Proceso:**
1. Solicitud en JCE
2. Audiencia de conciliación
3. Sentencia de divorcio
4. Inscripción en registro civil

⏰ **Duración:** 2-6 meses

**Documentos adicionales:**
• Acuerdo sobre custodia (si hay hijos)
• Acuerdo sobre bienes
• Certificado de buena conducta""",

    "adopcion": """👶 **Adopción en República Dominicana:**

**Requisitos para adoptantes:**
• Ser mayor de 25 años
• Tener al menos 15 años más que el adoptado
• Certificado de idoneidad
• Estabilidad económica y emocional

**Documentos necesarios:**
• Solicitud formal
• Certificado de idoneidad
• Acta de nacimiento del adoptado
• Sentencia de adopción
• Pago de tasas (RD$ 3,000-5,000)

**Proceso:**
1. Solicitud inicial
2. Evaluación psicológica y social
3. Audiencia judicial
4. Sentencia de adopción
5. Inscripción en registro civil

⏰ **Duración:** 6-12 meses

**Tipos de adopción:**
• Adopción simple
• Adopción plena
• Adopción internacional""",

    "defuncion": """⚰️ **Acta de Defunción en RD:**

**Requisitos:**
• Certificado médico de defunción
• Cédula de identidad del fallecido
• Cédula de identidad del declarante
• Pago de tasas (RD$ 300-500)

**Quién puede declarar:**
• Familiares directos
• Autoridades médicas
• Autoridades policiales
• Cualquier persona con conocimiento

**Proceso:**
1. Obtener certificado médico
2. Solicitar acta en JCE
3. Pago de tasas
4. Entrega inmediata

⏰ **Tiempo:** 1-3 días hábiles

**Documentos adicionales:**
• Si es extranjero: pasaporte
• Si es menor: acta de nacimiento
• Si es por accidente: reporte policial""",

    "certificados": """📜 **Certificados en la JCE:**

**Tipos de certificados disponibles:**
• Certificado de buena conducta
• Certificado de soltería
• Certificado de nacionalidad
• Certificado de residencia
• Certificado de votación

**Requisitos generales:**
• Cédula de identidad
• Pago de tasas (RD$ 200-500)
• Solicitud en formulario oficial

**Tiempos de entrega:**
• Certificado de buena conducta: 3-5 días
• Certificado de soltería: 1-2 días
• Certificado de nacionalidad: 5-7 días
• Certificado de residencia: 2-3 días

**Oficinas donde solicitarlos:**
• Cualquier oficina de la JCE
• En línea (algunos certificados)
• Por correo (certificados especiales)""",

    "general": """🏛️ **Junta Central Electoral (JCE) - República Dominicana**

**Servicios principales:**
• Actas de nacimiento, matrimonio, defunción
• Cédulas de identidad
• Cambios de nombre
• Naturalización
• Certificados varios

**Contacto:**
📞 Tel: (809) 537-0100
🌐 Web: www.jce.gob.do
📍 Dirección: Av. 27 de Febrero, Santo Domingo

**Horarios:**
Lunes a Viernes: 8:00 AM - 4:00 PM
Sábados: 8:00 AM - 12:00 PM

**Oficinas principales:**
• Santo Domingo (Central)
• Santiago
• La Romana
• San Pedro de Macorís
• San Francisco de Macorís
• Barahona
• Azua
• San Juan de la Maguana"""
}

# Control de límites
ultima_llamada = 0
llamadas_por_minuto = 0

def obtener_respuesta_predefinida(texto):
    """Obtener respuesta predefinida basada en el texto del usuario"""
    texto_lower = texto.lower()
    
    # Primero buscar en resoluciones oficiales
    resolution_response = buscar_en_resoluciones(texto_lower)
    if resolution_response:
        return resolution_response
    
    # Si no hay resolución específica, usar respuestas predefinidas
    if any(palabra in texto_lower for palabra in ["acta", "nacimiento", "certificado", "partida"]):
        return RESPUESTAS_PREDEFINIDAS["acta_nacimiento"]
    elif any(palabra in texto_lower for palabra in ["cambio", "nombre", "modificar", "corregir", "apellido"]):
        return RESPUESTAS_PREDEFINIDAS["cambio_nombre"]
    elif any(palabra in texto_lower for palabra in ["naturalizacion", "nacionalidad", "ciudadania", "extranjero", "inmigrante"]):
        return RESPUESTAS_PREDEFINIDAS["naturalizacion"]
    elif any(palabra in texto_lower for palabra in ["apostilla", "internacional", "extranjero", "validar", "legalizar"]):
        return RESPUESTAS_PREDEFINIDAS["apostilla"]
    elif any(palabra in texto_lower for palabra in ["cedula", "identidad", "documento", "carnet"]):
        return RESPUESTAS_PREDEFINIDAS["cedula"]
    elif any(palabra in texto_lower for palabra in ["matrimonio", "casarse", "boda", "casamiento"]):
        return RESPUESTAS_PREDEFINIDAS["matrimonio"]
    elif any(palabra in texto_lower for palabra in ["divorcio", "separar", "separacion", "disolver"]):
        return RESPUESTAS_PREDEFINIDAS["divorcio"]
    elif any(palabra in texto_lower for palabra in ["adopcion", "adoptar", "hijo", "menor"]):
        return RESPUESTAS_PREDEFINIDAS["adopcion"]
    elif any(palabra in texto_lower for palabra in ["defuncion", "muerte", "fallecimiento", "fallecido"]):
        return RESPUESTAS_PREDEFINIDAS["defuncion"]
    elif any(palabra in texto_lower for palabra in ["certificado", "buena conducta", "solteria", "nacionalidad", "residencia"]):
        return RESPUESTAS_PREDEFINIDAS["certificados"]
    else:
        return RESPUESTAS_PREDEFINIDAS["general"]

def buscar_en_resoluciones(texto):
    """Buscar información en las resoluciones oficiales de la JCE"""
    for title, resolution in JCE_RESOLUTIONS.items():
        content = resolution.get("contenido", "").lower()
        processed = resolution.get("contenido_procesado", {})
        
        # Buscar coincidencias en el contenido
        if any(palabra in content for palabra in texto.split()):
            # Crear respuesta basada en la resolución
            response = f"📋 **Información Oficial JCE**\n\n"
            response += f"**Resolución:** {title}\n"
            
            if processed.get("numero_resolucion"):
                response += f"**Número:** {processed['numero_resolucion']}\n"
            
            if processed.get("fecha"):
                response += f"**Fecha:** {processed['fecha']}\n\n"
            
            # Agregar artículos relevantes
            if processed.get("articulos"):
                response += "**Disposiciones relevantes:**\n"
                for article in processed["articulos"][:3]:
                    response += f"• Artículo {article['numero']}: {article['contenido']}\n"
                response += "\n"
            
            # Agregar información de aplicación
            if processed.get("aplicacion"):
                response += "**Aplicación:**\n"
                for app in processed["aplicacion"][:2]:
                    response += f"• {app}\n"
                response += "\n"
            
            response += "ℹ️ *Esta información está basada en resoluciones oficiales de la JCE*"
            return response
    
    return None

# Guardar el mensaje del usuario
def handle_user_message(message):
    user_id = message.from_user.id
    if user_id not in mensajes:
        mensajes[user_id] = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente virtual especializado en Registro Civil de República Dominicana. "
                        "Responde a los gestores usando resoluciones y reglas oficiales de la Junta Central Electoral."
                    )
                }
            ]
        }

    mensajes[user_id]["messages"].append({
        "role": "user",
        "content": message.text
    })

    # Limitar historial para evitar exceso
    mensajes[user_id]["messages"] = mensajes[user_id]["messages"][-20:]

# Generar respuesta con Gemini
async def generate_response(message):
    global ultima_llamada, llamadas_por_minuto
    
    # Control de límites
    tiempo_actual = time.time()
    if tiempo_actual - ultima_llamada < 60:  # Menos de 1 minuto
        llamadas_por_minuto += 1
        if llamadas_por_minuto > 10:  # Límite conservador
            return obtener_respuesta_predefinida(message.text)
    else:
        llamadas_por_minuto = 1
        ultima_llamada = tiempo_actual

    user_id = message.from_user.id
    prompt = ""

    for msg in mensajes[user_id]["messages"]:
        if msg["role"] == "user":
            prompt += f"Usuario: {msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"Asistente: {msg['content']}\n"
        elif msg["role"] == "system":
            prompt = f"{msg['content']}\n\n" + prompt

    try:
        # Llamar a Gemini
        response = await asyncio.to_thread(model.generate_content, prompt)
        respuesta_texto = response.text.strip()

        # Guardar respuesta
        mensajes[user_id]["messages"].append({
            "role": "assistant",
            "content": respuesta_texto
        })

        return respuesta_texto
        
    except Exception as e:
        print(f"Error de Gemini: {e}")
        # Usar respuesta predefinida como respaldo
        return obtener_respuesta_predefinida(message.text)

# Manejar mensajes entrantes
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        handle_user_message(update.message)
        response = await generate_response(update.message)
        await update.message.reply_text(response)
    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("⚠️ Ocurrió un error al procesar tu mensaje.")

# Función principal
def main():
    bot = Application.builder().token(TELEGRAM_TOKEN).build()
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("🤖 Bot ejecutándose...")
    bot.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()