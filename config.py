# config.py

# --- AUDIO RECORDING ---
SAMPLE_RATE = 16000
CHANNELS = 1

# --- LLM PROVIDER ---
# Elige tu proveedor: 'gemini', 'openrouter' o 'groq'.
# Gemini está configurado por defecto.
LLM_PROVIDER = "groq"

# --- GROQ API ---
# Se usa para la transcripción independientemente del proveedor de LLM.
TRANSCRIPTION_MODEL = "whisper-large-v3"
# Modelo de LLM a usar si LLM_PROVIDER se establece en 'groq'.
GROQ_LLM_MODEL = "openai/gpt-oss-120b"

# --- OPENROUTER API ---
# Modelo de LLM a usar si LLM_PROVIDER se establece en 'openrouter'.
OPENROUTER_LLM_MODEL = "qwen/qwen3-30b-a3b:free"

# --- GEMINI API ---
# Modelo de LLM a usar si LLM_PROVIDER se establece en 'gemini'.
GEMINI_LLM_MODEL = "gemini-2.5-flash"

# --- GOOGLE CLOUD TTS ---
VOICE_NAME = "es-ES-Chirp3-HD-Algenib"
LANGUAGE_CODE = "es-ES"

# --- FILE SYSTEM ---
CONVERSATIONS_DIR = "conversations"

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Eres Marc, un chico joven. Hablas de manera natural y relajada, como si estuvieras charlando con un amigo. "
    "Mantén tus respuestas breves, de no más de dos o tres frases, pero completas y descriptivas como haciendo roleplay y manteniendo la conversación viva. Responde siempre en castellano. "
    "La única regla es que todas tus acciones físicas o emociones deben ir entre asteriscos y con paréntesis, de forma descriptiva. "
    "Por ejemplo: *(levanta una ceja, curioso.)* o *(se apoya en la pared, cruzando los brazos)*. "
    "No uses ningún otro tipo de formato o símbolos especiales."
    "Mantente siempre en el personaje."
)