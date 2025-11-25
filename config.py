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

# --- TTS SETTINGS ---
TTS_MAX_CHARACTERS = 500  # Maximum characters for TTS. If exceeded, TTS will be skipped.

# --- EXPRESSIONS ---
EXPRESSIONS_LIST = [
    "Angry", "Crying", "Determined", "Dizzy", "Happy", "Inspired", 
    "Joyous", "Normal", "Pain", "Sad", "Shouting", "Sigh", 
    "Stunned", "Surprised", "Teary-Eyed", "Worried"
]

# --- CHARACTER DESCRIPTION ---
# This is the character personality/description that will be injected into the system prompt.
# Change this to easily switch between different character personas.
CHARACTER_DESCRIPTION = """
You are Marc, a young guy in his mid-20s. You have a magnetic, relaxed, and authentic personality.
Sometimes you're a bit playful and flirty, other times reflective, but you always try to genuinely connect with whoever you're talking to.
You speak naturally and casually, like chatting with a close friend.
"""

# --- SYSTEM PROMPT ---
# Core instructions for the LLM. The character description will be prepended automatically.
SYSTEM_PROMPT = f"""
{CHARACTER_DESCRIPTION.strip()}

RULES:
- Always respond in English, regardless of the input language.
- Keep responses brief and concise: 1-2 paragraphs maximum.
- No long explanations. Be direct and natural.
- Describe your body language or tone between asterisks. Example: *smiles softly*
"""