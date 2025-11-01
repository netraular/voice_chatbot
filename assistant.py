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
    Gestiona la lógica central del asistente de voz, desacoplándola de la UI.
    """
    def __init__(self, conversation_id):
        self.transcription_handler = GroqHandler()
        self.llm_handler = get_llm_handler()
        self.tts_handler = GoogleTTSHandler()

        self.conversation_id = conversation_id
        self.conversation_path = os.path.join(CONVERSATIONS_DIR, self.conversation_id)
        os.makedirs(self.conversation_path, exist_ok=True)
        print(f"Lógica del asistente inicializada. Guardando conversación en: {self.conversation_path}")

        self.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def transcribe_and_update_history(self, user_audio_path):
        """
        Paso 1: Transcribe el audio del usuario y actualiza el historial de chat.
        Devuelve el texto transcrito o un error.
        """
        transcribed_text = self.transcription_handler.transcribe(user_audio_path)
        if not transcribed_text or transcribed_text.startswith("Error:"):
            return {"error": "No se pudo entender el audio.", "user_text": ""}

        user_message = {"role": "user", "content": transcribed_text, "timestamp": datetime.datetime.now().isoformat()}
        self.chat_history.append(user_message)
        
        return {"user_text": transcribed_text, "error": None}

    def generate_assistant_response(self, turn_counter):
        """
        Paso 2: Genera la respuesta del LLM, la sintetiza a voz y guarda el historial.
        """
        # 1. Obtener respuesta del LLM
        llm_data = self.llm_handler.get_chat_completion(self.chat_history)
        if llm_data.get("error"):
            self.chat_history.append({"role": "system", "content": f"[ERROR] {llm_data['error']}"})
            self.save_chat_history()
            return {"error": llm_data["error"]}

        raw_llm_response = llm_data["response"]
        usage_info = llm_data["usage"]

        if not raw_llm_response or not raw_llm_response.strip():
            error_msg = "No se pudo generar una respuesta. Por favor, inténtalo de nuevo."
            self.chat_history.append({"role": "assistant", "content": f"[{error_msg}]"})
            self.save_chat_history()
            return {"error": error_msg}
        
        # 2. Procesar y limpiar texto para UI y TTS
        processed_text = parse_and_clean_llm_response(raw_llm_response)

        assistant_message = {
            "role": "assistant",
            "content_raw": raw_llm_response,
            "content_ui": processed_text["for_ui"],
            "content_tts": processed_text["for_tts"]
        }
        if usage_info:
            if "prompt_tokens" in usage_info:
                # El mensaje de usuario es el penúltimo en el historial
                self.chat_history[-1]["prompt_tokens"] = usage_info["prompt_tokens"]
            if "completion_tokens" in usage_info:
                assistant_message["completion_tokens"] = usage_info["completion_tokens"]
            if "completion_time" in usage_info:
                assistant_message["completion_time"] = usage_info["completion_time"]
        
        self.chat_history.append(assistant_message)
        self.save_chat_history()

        # 3. Sintetizar voz
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

    def save_chat_history(self):
        log_path = os.path.join(self.conversation_path, "chat_history.json")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            print(f"Historial de chat guardado en {log_path}")
        except Exception as e:
            print(f"Fallo al guardar el historial de chat: {e}")