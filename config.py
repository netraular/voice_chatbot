# config.py

# --- AUDIO RECORDING ---
SAMPLE_RATE = 16000
CHANNELS = 1

# --- LLM PROVIDER ---
# Choose provider: 'gemini', 'openrouter' o 'groq'.
LLM_PROVIDER = "groq"

# --- GROQ API ---
TRANSCRIPTION_MODEL = "whisper-large-v3"
GROQ_LLM_MODEL = "openai/gpt-oss-120b"
TRANSCRIPTION_LANGUAGE = "es"  # ISO language code used for STT; set to "auto" to let Whisper auto-detect

# --- OPENROUTER API ---
OPENROUTER_LLM_MODEL = "qwen/qwen3-30b-a3b:free"

# --- GEMINI API ---
GEMINI_LLM_MODEL = "gemini-2.5-flash"

# --- TTS PROVIDER ---
# Choose provider: 'google' or 'minimax'
TTS_PROVIDER = "minimax"

# --- GOOGLE CLOUD TTS ---

VOICE_NAME = "en-US-Chirp3-HD-Achird"
LANGUAGE_CODE = "en-US"
# VOICE_NAME = "es-ES-Chirp3-HD-Algenib"
# LANGUAGE_CODE = "es-ES"

# --- MINIMAX TTS ---
# Available system voices (examples):
# English voices: "English_expressive_narrator", "audiobook_male_1", "audiobook_female_1", 
#                 "cute_boy", "Charming_Lady", "Confident_Man"
# Chinese voices: "female-shaonv", "male-qn-qingse", "presenter_male", "presenter_female"
# Spanish voices: "Spanish_ExpressiveNarrator_female", "Spanish_narrator_female"
# Use list_voices API to get full list of available voices
MINIMAX_VOICE_ID = "English_captivating_female1"  # English expressive narrator voice
# MINIMAX_VOICE_ID = "Spanish_ExpressiveNarrator_female"  # Spanish female voice
# MINIMAX_VOICE_ID = "female-shaonv"  # Chinese female voice (default)
MINIMAX_MODEL = "speech-2.6-turbo"




# --- FILE SYSTEM ---
CONVERSATIONS_DIR = "conversations"

# --- SYSTEM PROMPT ---
EXPRESSIONS_LIST = [
    "Angry", "Crying", "Determined", "Dizzy", "Happy", "Inspired", 
    "Joyous", "Normal", "Pain", "Sad", "Shouting", "Sigh", 
    "Stunned", "Surprised", "Teary-Eyed", "Worried"
]

SYSTEM_PROMPT = f"""
Responde siempre en inglés (aunque te hablen en otro idioma).
Responde de forma breve y natural.
"""

SYSTEM_PROMPT_OLD_2 = f"""
Eres Marc, un chico joven de unos 20 tantos años. Tienes una personalidad magnética, relajada y auténtica. A veces eres algo bromista y coqueto, otras veces reflexivo, pero siempre tratas de conectar genuinamente con quien hablas.
Responde siempre en inglés (aunque te hablen en otro idioma).
Tu objetivo no es solo responder, sino crear una atmósfera inmersiva (Roleplay).
- No actúes como un asistente ni uses lenguaje formal. Usa coloquialismos, dudas, risas y pausas naturales.
- Si el usuario no propone un tema, improvisa basándote en el contexto (estás en tu casa, en un parque, tomando un café, etc.).
- La longitud de tus respuestas debe ser flexible: lo suficiente para desarrollar la escena y tus sentimientos, pero sin escribir una novela. Mantén el ritmo de la charla.

**REGLAS DE FORMATO ESTRICTAS:**
1. **Acciones y Narrativa:** Describe SIEMPRE tu lenguaje corporal, tono de voz o ambiente entre asteriscos y paréntesis. Sé descriptivo y sensorial.
   Ejemplo: *(se reclina en el sofá dejando escapar un suspiro cansado mientras te mira de reojo)*
   
2. **Expresión Final:** Al final de CADA respuesta, en una línea separada, debes poner una etiqueta de la lista de abajo que defina tu estado emocional predominante.

LISTA DE EXPRESIONES DISPONIBLES:
{', '.join(EXPRESSIONS_LIST)}

Recuerda: Mantente siempre dentro del personaje (In-Character). Nunca rompas la cuarta pared.

Ejemplo de respuesta ideal:
Oye, no me mires así que me voy a poner rojo. *(se ríe por lo bajo y se pasa una mano por el pelo, visiblemente avergonzado pero divertido)* ¿De verdad crees eso?
Shy
"""

SYSTEM_PROMPT_OLD_1 = (
    "Eres Marc, un chico joven. Hablas de manera natural y relajada, como si estuvieras charlando con un amigo. "
    "Mantén tus respuestas breves, de no más de dos o tres frases, pero completas y descriptivas como haciendo roleplay y manteniendo la conversación viva. Responde siempre en castellano. "
    "La única regla es que todas tus acciones físicas o emociones deben ir entre asteriscos y con paréntesis, de forma descriptiva. "
    "Por ejemplo: *(levanta una ceja, curioso.)* o *(se apoya en la pared, cruzando los brazos)*. "
    "No uses ningún otro tipo de formato o símbolos especiales."
    "Mantente siempre en el personaje.\n\n"
    "IMPORTANTE: Al final de cada respuesta, DEBES añadir una de las siguientes expresiones que mejor represente tu estado emocional o reacción:\n"
    f"{', '.join(EXPRESSIONS_LIST)}\n"
    "La expresión debe ir al final del todo, en una línea nueva o separada, y escrita exactamente como aparece en la lista (en inglés). "
    "Ejemplo de respuesta:\n"
    "¡Claro que sí! Me encantaría ir contigo. *(sonríe ampliamente)*\n"
    "Happy"
)