# groq_api.py
import os
from groq import Groq
from dotenv import load_dotenv

from config import TRANSCRIPTION_MODEL

load_dotenv()

class GroqHandler:
    """
    Manages audio transcription using the Groq API (Whisper).
    """
    # Initializes the Groq API client.
    def __init__(self):
        try:
            self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            if not self.client.api_key:
                raise ValueError("GROQ_API_KEY not found in .env file or is invalid.")
            print("Groq client initialized successfully (for transcription).")
        except Exception as e:
            print(f"Error initializing Groq client: {e}")
            self.client = None

    # Transcribes an audio file to text using the Whisper model.
    def transcribe(self, filepath):
        if not self.client:
            return "Error: Groq client is not initialized."

        print(f"Sending {filepath} for transcription...")
        try:
            with open(filepath, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(filepath), file.read()),
                    model=TRANSCRIPTION_MODEL,
                    language="en"
                )
            print("Transcription completed successfully.")
            return transcription.text
        except Exception as e:
            print(f"Transcription error: {e}")
            return f"Error: Could not transcribe the audio. {e}"