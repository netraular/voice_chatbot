# assistant.py
import os
import json
import datetime

from groq_api import GroqHandler
from llm_api import get_llm_handler
from google_cloud_api import GoogleTTSHandler
from utils import parse_and_clean_llm_response
from config import SYSTEM_PROMPT, CONVERSATIONS_DIR

class VoiceAssistant:
    """
    Manages the core voice assistant logic, decoupling it from the UI.
    """
    # Initializes the assistant's components and conversation setup.
    def __init__(self, conversation_id):
        self.transcription_handler = GroqHandler()
        self.llm_handler = get_llm_handler()
        self.tts_handler = GoogleTTSHandler()

        self.conversation_id = conversation_id
        self.conversation_path = os.path.join(CONVERSATIONS_DIR, self.conversation_id)
        os.makedirs(self.conversation_path, exist_ok=True)
        print(f"Assistant logic initialized. Saving conversation to: {self.conversation_path}")

        self.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Transcribes user audio and updates the chat history.
    def transcribe_and_update_history(self, user_audio_path):
        transcribed_text = self.transcription_handler.transcribe(user_audio_path)
        if not transcribed_text or transcribed_text.startswith("Error:"):
            return {"error": "Failed to understand the audio.", "user_text": ""}

        user_message = {"role": "user", "content": transcribed_text, "timestamp": datetime.datetime.now().isoformat()}
        self.chat_history.append(user_message)
        
        return {"user_text": transcribed_text, "error": None}

    # Generates the LLM response, synthesizes it to speech, and saves the history.
    def generate_assistant_response(self, turn_counter):
        # 1. Get response from the LLM
        llm_data = self.llm_handler.get_chat_completion(self.chat_history)
        if llm_data.get("error"):
            self.chat_history.append({"role": "system", "content": f"[ERROR] {llm_data['error']}"})
            self.save_chat_history()
            return {"error": llm_data["error"]}

        raw_llm_response = llm_data["response"]
        usage_info = llm_data["usage"]

        if not raw_llm_response or not raw_llm_response.strip():
            error_msg = "Could not generate a response. Please try again."
            self.chat_history.append({"role": "assistant", "content": f"[{error_msg}]"})
            self.save_chat_history()
            return {"error": error_msg}
        
        # 2. Process and clean text for UI and TTS
        processed_text = parse_and_clean_llm_response(raw_llm_response)

        expression = processed_text.get("expression")
        if expression:
            print(f"EXPRESSION DETECTED: {expression}")

        assistant_message = {
            "role": "assistant",
            "content_raw": raw_llm_response,
            "content_ui": processed_text["for_ui"],
            "content_tts": processed_text["for_tts"],
            "expression": expression
        }
        if usage_info:
            if "prompt_tokens" in usage_info:
                # User message is the second to last in history
                self.chat_history[-1]["prompt_tokens"] = usage_info["prompt_tokens"]
            if "completion_tokens" in usage_info:
                assistant_message["completion_tokens"] = usage_info["completion_tokens"]
            if "completion_time" in usage_info:
                assistant_message["completion_time"] = usage_info["completion_time"]
        
        self.chat_history.append(assistant_message)
        self.save_chat_history()

        # 3. Synthesize speech
        audio_content = self.tts_handler.synthesize_speech(processed_text["for_tts"])
        if audio_content:
            assistant_audio_path = os.path.join(self.conversation_path, f"assistant_{turn_counter}.mp3")
            with open(assistant_audio_path, "wb") as f:
                f.write(audio_content)

        return {
            "assistant_ui_text": processed_text["for_ui"],
            "audio_content": audio_content,
            "error": None
        }

    # Saves the current chat history to a JSON file.
    def save_chat_history(self):
        log_path = os.path.join(self.conversation_path, "chat_history.json")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            print(f"Chat history saved to {log_path}")
        except Exception as e:
            print(f"Failed to save chat history: {e}")