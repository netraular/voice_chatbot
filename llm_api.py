# llm_api.py
import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod

# Import API clients
from groq import Groq
from openai import OpenAI
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Import configuration
from config import (
    LLM_PROVIDER, GROQ_LLM_MODEL, OPENROUTER_LLM_MODEL, GEMINI_LLM_MODEL
)

load_dotenv()

class LLMHandler(ABC):
    """Clase base abstracta para los manejadores de LLM."""
    def __init__(self):
        self.client = self._initialize_client()
        if not self.client:
            raise ConnectionError(f"Fallo al inicializar el cliente {self.__class__.__name__}.")
        print(f"{self.__class__.__name__} inicializado correctamente.")
    
    @abstractmethod
    def _initialize_client(self):
        """Inicializa el cliente de la API específica."""
        pass
        
    @abstractmethod
    def get_chat_completion(self, message_history):
        """Obtiene una respuesta del LLM basada en el historial de mensajes."""
        pass
        
    def _clean_messages_openai_format(self, message_history):
        """Prepara los mensajes para APIs con formato OpenAI (Groq, OpenRouter)."""
        clean_messages = []
        for msg in message_history:
            role = msg.get("role")
            content = msg.get("content_raw") if role == "assistant" else msg.get("content")
            if role and content:
                clean_messages.append({"role": role, "content": content})
        return clean_messages

class GroqLLMHandler(LLMHandler):
    """Manejador de LLM para la API de Groq."""
    def _initialize_client(self):
        try:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key: raise ValueError("GROQ_API_KEY no encontrada.")
            return Groq(api_key=api_key)
        except Exception as e:
            print(f"Error inicializando el cliente LLM de Groq: {e}")
            return None
            
    def get_chat_completion(self, message_history):
        print(f"Enviando historial de mensajes al LLM de Groq ('{GROQ_LLM_MODEL}')...")
        try:
            chat_completion = self.client.chat.completions.create(
                messages=self._clean_messages_openai_format(message_history),
                model=GROQ_LLM_MODEL, max_tokens=500
            )
            response = chat_completion.choices[0].message.content
            usage_info = {
                "prompt_tokens": chat_completion.usage.prompt_tokens,
                "completion_tokens": chat_completion.usage.completion_tokens,
                "completion_time": chat_completion.usage.completion_time
            }
            return {"response": response, "usage": usage_info, "error": None}
        except Exception as e:
            return {"response": None, "usage": None, "error": str(e)}

class OpenRouterLLMHandler(LLMHandler):
    """Manejador de LLM para la API de OpenRouter."""
    def _initialize_client(self):
        try:
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key: raise ValueError("OPENROUTER_API_KEY no encontrada.")
            return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        except Exception as e:
            print(f"Error inicializando el cliente LLM de OpenRouter: {e}")
            return None

    def get_chat_completion(self, message_history):
        print(f"Enviando historial de mensajes a OpenRouter ('{OPENROUTER_LLM_MODEL}')...")
        try:
            chat_completion = self.client.chat.completions.create(
                model=OPENROUTER_LLM_MODEL,
                messages=self._clean_messages_openai_format(message_history),
                max_tokens=500
            )
            response = chat_completion.choices[0].message.content
            usage_info = {
                "prompt_tokens": chat_completion.usage.prompt_tokens,
                "completion_tokens": chat_completion.usage.completion_tokens
            }
            return {"response": response, "usage": usage_info, "error": None}
        except Exception as e:
            return {"response": None, "usage": None, "error": str(e)}

class GeminiLLMHandler(LLMHandler):
    """Manejador de LLM para la API de Google Gemini."""
    def _initialize_client(self):
        try:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key: raise ValueError("GOOGLE_API_KEY no encontrada.")
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(GEMINI_LLM_MODEL)
        except Exception as e:
            print(f"Error inicializando el cliente LLM de Gemini: {e}")
            return None

    def get_chat_completion(self, message_history):
        print(f"Enviando historial de mensajes a Gemini ('{GEMINI_LLM_MODEL}')...")
        
        system_prompt = None
        gemini_history = []
        for msg in message_history:
            role = msg.get("role")
            content = msg.get("content_raw") if role == "assistant" else msg.get("content")
            
            if role == "system":
                system_prompt = content
                continue
            
            # Gemini usa 'model' en lugar de 'assistant' para el rol de la IA
            gemini_role = "model" if role == "assistant" else "user"
            gemini_history.append({"role": gemini_role, "parts": [content]})
            
        try:
            # La API de Gemini separa el 'system_instruction' del historial
            model = genai.GenerativeModel(GEMINI_LLM_MODEL, system_instruction=system_prompt)
            chat = model.start_chat(history=gemini_history[:-1]) # Historial sin el último mensaje del usuario
            response = chat.send_message(
                gemini_history[-1]['parts'], # Envía solo el último mensaje del usuario
                safety_settings={ # Configuraciones de seguridad para evitar bloqueos innecesarios
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                }
            )
            
            # Gemini devuelve la información de uso en 'usage_metadata'
            usage_info = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count
            }
            return {"response": response.text, "usage": usage_info, "error": None}

        except Exception as e:
            print(f"Error en el chat con LLM de Gemini: {e}")
            return {"response": None, "usage": None, "error": str(e)}


def get_llm_handler() -> LLMHandler:
    """Función factory para obtener el manejador de LLM configurado."""
    provider = LLM_PROVIDER.lower()
    if provider == 'gemini':
        return GeminiLLMHandler()
    elif provider == 'openrouter':
        return OpenRouterLLMHandler()
    elif provider == 'groq':
        return GroqLLMHandler()
    else:
        raise ValueError(f"Proveedor de LLM no soportado: '{LLM_PROVIDER}'. Revisa config.py.")