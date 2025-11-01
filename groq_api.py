# groq_api.py
import os
from groq import Groq
from dotenv import load_dotenv

# --- CONFIGURATION (Imported) ---
from config import TRANSCRIPTION_MODEL

load_dotenv()

class GroqHandler:
    """
    Gestiona la transcripción de audio usando la API de Groq (Whisper).
    """
    def __init__(self):
        try:
            self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            if not self.client.api_key:
                raise ValueError("GROQ_API_KEY no encontrada en el fichero .env o es inválida.")
            print("Cliente de Groq inicializado correctamente (para transcripción).")
        except Exception as e:
            print(f"Error inicializando el cliente de Groq: {e}")
            self.client = None

    def transcribe(self, filepath):
        """ Transcribe un fichero de audio a texto usando el modelo Whisper. """
        if not self.client:
            return "Error: El cliente de Groq no está inicializado."

        print(f"Enviando {filepath} para transcripción...")
        try:
            with open(filepath, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(filepath), file.read()),
                    model=TRANSCRIPTION_MODEL,
                    language="es"
                )
            print("Transcripción completada con éxito.")
            return transcription.text
        except Exception as e:
            print(f"Error de transcripción: {e}")
            return f"Error: No se pudo transcribir el audio. {e}"