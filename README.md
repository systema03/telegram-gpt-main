# 🤖 Bot de Telegram - Asistente de Registro Civil RD

Bot de Telegram especializado en **Registro Civil de República Dominicana**, que utiliza **Google Gemini AI** para responder consultas sobre resoluciones y reglas oficiales de la Junta Central Electoral.

## 🚀 Características

- **Especialización**: Asistente virtual especializado en Registro Civil RD
- **IA Avanzada**: Utiliza Google Gemini Pro para respuestas inteligentes
- **Historial por Usuario**: Mantiene contexto de conversación individual
- **Manejo de Errores**: Respuestas robustas ante errores
- **Async/Await**: Mejor rendimiento y escalabilidad

## 📋 Requisitos

- Python 3.8+
- Token de Telegram Bot
- API Key de Google Gemini AI

## 🛠️ Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/systema03/telegram-gpt-main.git
cd telegram-gpt-main
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:
Crear archivo `.env` con:
```env
TELEGRAM_TOKEN=tu_token_de_telegram
GEMINI_API_KEY=tu_api_key_de_gemini
```

4. **Ejecutar el bot**:
```bash
python bot.py
```

## 🔧 Configuración

### Obtener Token de Telegram:
1. Habla con [@BotFather](https://t.me/botfather) en Telegram
2. Usa el comando `/newbot`
3. Sigue las instrucciones para crear tu bot
4. Copia el token proporcionado

### Obtener API Key de Gemini:
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva API key
3. Copia la clave generada

## 📝 Uso

Una vez ejecutado, el bot responderá automáticamente a todos los mensajes de texto con información especializada sobre Registro Civil de República Dominicana.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
