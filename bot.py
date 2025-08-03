from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import Update
from dotenv import load_dotenv
import os
import google.generativeai as genai
import asyncio

# Cargar variables de entorno
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Diccionario para mantener historial por usuario
mensajes = {}

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
    user_id = message.from_user.id
    prompt = ""

    for msg in mensajes[user_id]["messages"]:
        if msg["role"] == "user":
            prompt += f"Usuario: {msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"Asistente: {msg['content']}\n"
        elif msg["role"] == "system":
            prompt = f"{msg['content']}\n\n" + prompt

    # Llamar a Gemini
    response = await asyncio.to_thread(model.generate_content, prompt)

    respuesta_texto = response.text.strip()

    # Guardar respuesta
    mensajes[user_id]["messages"].append({
        "role": "assistant",
        "content": respuesta_texto
    })

    return respuesta_texto

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