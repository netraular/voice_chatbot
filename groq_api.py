# groq_api.py
import os
from groq import Groq
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
TRANSCRIPTION_MODEL = "whisper-large-v3"
LLM_MODEL = "openai/gpt-oss-120b"

class GroqHandler:
    # Initializes the Groq API client.
    def __init__(self):
        try:
            self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            if not self.client.api_key:
                raise ValueError("GROQ_API_KEY not found in .env file or is invalid.")
            print("Groq client initialized successfully.")
        except Exception as e:
            print(f"Error initializing Groq client: {e}")
            self.client = None

    # Transcribes an audio file to text using the Whisper model.
    def transcribe(self, filepath):
        if not self.client:
            return "Error: Groq client not initialized."

        print(f"Sending {filepath} for transcription...")
        try:
            with open(filepath, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(filepath), file.read()),
                    model=TRANSCRIPTION_MODEL,
                    language="es"
                )
            print("Transcription successful.")
            return transcription.text
        except Exception as e:
            print(f"Transcription Error: {e}")
            return f"Error: Could not transcribe audio. {e}"

    # Gets a chat completion from the LLM based on the message history.
    def get_chat_completion(self, message_history):
        if not self.client:
            return {"response": None, "usage": None, "error": "Groq client not initialized."}

        print(f"Sending message history to LLM ('{LLM_MODEL}')...")
        try:
            # Create a clean version of the history for the API, containing only 'role' and 'content'.
            clean_messages = [
                {"role": msg["role"], "content": msg["content"]} for msg in message_history
            ]

            chat_completion = self.client.chat.completions.create(
                messages=clean_messages,
                model=LLM_MODEL,
                max_completion_tokens=500,
                reasoning_effort="low",
                user="123"
            )
            response = chat_completion.choices[0].message.content
            
            usage_info = None
            if chat_completion.usage:
                usage_info = {
                    "prompt_tokens": chat_completion.usage.prompt_tokens,
                    "completion_tokens": chat_completion.usage.completion_tokens,
                    "completion_time": chat_completion.usage.completion_time
                }
                print(f"Token Usage: {usage_info}")

            print("LLM response received.")
            # Return a dictionary with the response and no error on success.
            return {"response": response, "usage": usage_info, "error": None}
            
        except Exception as e:
            print(f"LLM Chat Error: {e}")
            # Return a dictionary with the error message on failure.
            return {"response": None, "usage": None, "error": str(e)}