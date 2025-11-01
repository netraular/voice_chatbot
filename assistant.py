# assistant.py
import os
import json
import datetime

from groq_api import GroqHandler
from google_cloud_api import GoogleTTSHandler
from utils import parse_and_clean_llm_response
from config import SYSTEM_PROMPT, CONVERSATIONS_DIR

class VoiceAssistant:
    """
    Manages the core logic of the voice assistant, decoupling it from the UI.
    """
    def __init__(self, conversation_id):
        self.groq_handler = GroqHandler()
        self.tts_handler = GoogleTTSHandler()

        self.conversation_id = conversation_id
        self.conversation_path = os.path.join(CONVERSATIONS_DIR, self.conversation_id)
        os.makedirs(self.conversation_path, exist_ok=True)
        print(f"Assistant logic initialized. Saving conversation to: {self.conversation_path}")

        self.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def process_turn(self, user_audio_path, turn_counter):
        """
        Handles a full conversation turn: transcribe, get LLM response, synthesize speech.
        Returns a dictionary with results for the UI.
        """
        # 1. Transcribe audio
        transcribed_text = self.groq_handler.transcribe(user_audio_path)
        if not transcribed_text or transcribed_text.startswith("Error:"):
            return {"error": "Could not understand the audio.", "user_text": ""}

        user_message = {
            "role": "user", "content": transcribed_text,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.chat_history.append(user_message)

        # 2. Get LLM response
        llm_data = self.groq_handler.get_chat_completion(self.chat_history)
        if llm_data.get("error"):
            self.chat_history.append({"role": "system", "content": f"[ERROR] {llm_data['error']}"})
            self.save_chat_history()
            return {"error": llm_data["error"], "user_text": transcribed_text}

        raw_llm_response = llm_data["response"]
        usage_info = llm_data["usage"]

        if not raw_llm_response or not raw_llm_response.strip():
            error_msg = "Could not generate a response. Please try again."
            self.chat_history.append({"role": "assistant", "content": f"[{error_msg}]"})
            self.save_chat_history()
            return {"error": error_msg, "user_text": transcribed_text}
        
        # 3. Process and clean text for UI and TTS
        processed_text = parse_and_clean_llm_response(raw_llm_response)

        assistant_message = {
            "role": "assistant",
            "content_raw": raw_llm_response,
            "content_ui": processed_text["for_ui"],
            "content_tts": processed_text["for_tts"]
        }
        if usage_info:
            self.chat_history[-2]["prompt_tokens"] = usage_info["prompt_tokens"] # Add to user message
            assistant_message["completion_tokens"] = usage_info["completion_tokens"]
            assistant_message["completion_time"] = usage_info["completion_time"]
        
        self.chat_history.append(assistant_message)
        self.save_chat_history()

        # 4. Synthesize speech
        audio_content = self.tts_handler.synthesize_speech(processed_text["for_tts"])
        if audio_content:
            assistant_audio_path = os.path.join(self.conversation_path, f"assistant_{turn_counter}.mp3")
            with open(assistant_audio_path, "wb") as f:
                f.write(audio_content)

        return {
            "user_text": transcribed_text,
            "assistant_ui_text": processed_text["for_ui"],
            "audio_content": audio_content,
            "error": None
        }

    def save_chat_history(self):
        log_path = os.path.join(self.conversation_path, "chat_history.json")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            print(f"Chat history saved to {log_path}")
        except Exception as e:
            print(f"Failed to save chat history: {e}")