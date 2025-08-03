from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import Update
from dotenv import load_dotenv
import os
import google.generativeai as genai
import asyncio
import time

# Cargar variables de entorno
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

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
    
    # Detectar temas específicos
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
    else:
        return RESPUESTAS_PREDEFINIDAS["general"]

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