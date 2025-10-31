# groq_api.py
import os
from groq import Groq
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
TRANSCRIPTION_MODEL = "whisper-large-v3"
LLM_MODEL = "openai/gpt-oss-120b"

class GroqHandler:
    def __init__(self):
        try:
            self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            if not self.client.api_key:
                raise ValueError("GROQ_API_KEY not found in .env file or is invalid.")
            print("Groq client initialized successfully.")
        except Exception as e:
            print(f"Error initializing Groq client: {e}")
            self.client = None

    def transcribe(self, filepath):
        if not self.client:
            return "Error: Groq client not initialized."

        print(f"Sending {filepath} for transcription...")
        try:
            with open(filepath, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(filepath), file.read()),
                    model=TRANSCRIPTION_MODEL,
                    language="es"  # <-- AÑADIDO
                )
            print("Transcription successful.")
            return transcription.text
        except Exception as e:
            print(f"Transcription Error: {e}")
            return f"Error: Could not transcribe audio. {e}"

    def get_chat_completion(self, message_history):
        if not self.client:
            return "Error: Groq client not initialized."

        print(f"Sending message history to LLM ('{LLM_MODEL}')...")
        try:
            chat_completion = self.client.chat.completions.create(
                messages=message_history,
                model=LLM_MODEL,
            )
            response = chat_completion.choices[0].message.content
            print("LLM response received.")
            return response
        except Exception as e:
            print(f"LLM Chat Error: {e}")
            return f"Error: Could not get chat completion. {e}"