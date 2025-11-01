# google_cloud_api.py
from google.cloud import texttospeech

# --- CONFIGURATION (Imported) ---
from config import VOICE_NAME, LANGUAGE_CODE

class GoogleTTSHandler:
    """
    Manages Text-to-Speech synthesis using Google Cloud API.
    """
    def __init__(self):
        try:
            self.client = texttospeech.TextToSpeechClient()
            self.voice_params = texttospeech.VoiceSelectionParams(
                language_code=LANGUAGE_CODE, name=VOICE_NAME
            )
            self.audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            print("Google Cloud TTS client initialized successfully.")
        except Exception as e:
            print(f"Error initializing Google Cloud TTS client: {e}")
            print("Please ensure you have authenticated with 'gcloud auth application-default login'")
            self.client = None

    def synthesize_speech(self, text):
        """
        Synthesizes speech from the input text.
        Returns the audio content as bytes.
        """
        if not self.client:
            print("TTS client not available.")
            return None

        try:
            input_text = texttospeech.SynthesisInput(text=text)
            response = self.client.synthesize_speech(
                input=input_text, voice=self.voice_params, audio_config=self.audio_config
            )
            print("Speech synthesized successfully.")
            return response.audio_content
        except Exception as e:
            print(f"Error during speech synthesis: {e}")
            return None