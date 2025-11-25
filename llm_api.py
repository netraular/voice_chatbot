# llm_api.py
import os
import json
import enum
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing_extensions import TypedDict

# Import API clients
from groq import Groq
from openai import OpenAI
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Import configuration
from config import (
    LLM_PROVIDER, GROQ_LLM_MODEL, OPENROUTER_LLM_MODEL, GEMINI_LLM_MODEL, EXPRESSIONS_LIST
)

# --- Structured Output Schema for Groq (JSON Schema format) ---
GROQ_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "response_text": {
            "type": "string",
            "description": "The assistant's response text including actions in asterisks."
        },
        "expression": {
            "type": "string",
            "description": "The emotional expression that best represents the assistant's current state.",
            "enum": EXPRESSIONS_LIST
        }
    },
    "required": ["response_text", "expression"],
    "additionalProperties": False
}

# --- Structured Output Schema for Gemini (using Python types) ---
class ExpressionEnum(enum.Enum):
    ANGRY = "Angry"
    CRYING = "Crying"
    DETERMINED = "Determined"
    DIZZY = "Dizzy"
    HAPPY = "Happy"
    INSPIRED = "Inspired"
    JOYOUS = "Joyous"
    NORMAL = "Normal"
    PAIN = "Pain"
    SAD = "Sad"
    SHOUTING = "Shouting"
    SIGH = "Sigh"
    STUNNED = "Stunned"
    SURPRISED = "Surprised"
    TEARY_EYED = "Teary-Eyed"
    WORRIED = "Worried"

class GeminiResponseSchema(TypedDict):
    response_text: str
    expression: ExpressionEnum

load_dotenv()

class LLMHandler(ABC):
    """Abstract base class for LLM handlers."""
    # Initializes the handler and its specific API client.
    def __init__(self):
        self.client = self._initialize_client()
        if not self.client:
            raise ConnectionError(f"Failed to initialize {self.__class__.__name__} client.")
        print(f"{self.__class__.__name__} initialized successfully.")
    
    # Abstract method to initialize the specific API client.
    @abstractmethod
    def _initialize_client(self):
        pass
        
    # Abstract method to get a chat completion from the LLM.
    @abstractmethod
    def get_chat_completion(self, message_history):
        pass
        
    # Prepares messages for OpenAI-formatted APIs (Groq, OpenRouter).
    def _clean_messages_openai_format(self, message_history):
        clean_messages = []
        for msg in message_history:
            role = msg.get("role")
            content = msg.get("content_raw") if role == "assistant" else msg.get("content")
            if role and content:
                clean_messages.append({"role": role, "content": content})
        return clean_messages

class GroqLLMHandler(LLMHandler):
    """LLM handler for the Groq API with structured output support."""
    # Initializes the Groq client.
    def _initialize_client(self):
        try:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key: raise ValueError("GROQ_API_KEY not found.")
            return Groq(api_key=api_key)
        except Exception as e:
            print(f"Error initializing Groq LLM client: {e}")
            return None
            
    # Gets a chat completion from the Groq LLM with structured output.
    def get_chat_completion(self, message_history):
        print(f"Sending message history to Groq LLM ('{GROQ_LLM_MODEL}') with structured output...")
        try:
            chat_completion = self.client.chat.completions.create(
                messages=self._clean_messages_openai_format(message_history),
                model=GROQ_LLM_MODEL,
                max_tokens=500,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "assistant_response",
                        "schema": GROQ_RESPONSE_SCHEMA
                    }
                }
            )
            response_content = chat_completion.choices[0].message.content
            
            # Parse structured JSON response
            response_json = json.loads(response_content)
            response_text = response_json.get("response_text", "")
            expression = response_json.get("expression", "Normal")
            
            # Format response with expression appended (for compatibility with existing parsing)
            formatted_response = f"{response_text}\n{expression}"
            
            usage_info = {
                "prompt_tokens": chat_completion.usage.prompt_tokens,
                "completion_tokens": chat_completion.usage.completion_tokens,
                "completion_time": getattr(chat_completion.usage, 'completion_time', None)
            }
            return {"response": formatted_response, "usage": usage_info, "error": None}
        except Exception as e:
            print(f"Error in Groq LLM chat: {e}")
            return {"response": None, "usage": None, "error": str(e)}

class OpenRouterLLMHandler(LLMHandler):
    """LLM handler for the OpenRouter API."""
    # Initializes the OpenRouter client.
    def _initialize_client(self):
        try:
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key: raise ValueError("OPENROUTER_API_KEY not found.")
            return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        except Exception as e:
            print(f"Error initializing OpenRouter LLM client: {e}")
            return None

    # Gets a chat completion from the OpenRouter LLM.
    def get_chat_completion(self, message_history):
        print(f"Sending message history to OpenRouter ('{OPENROUTER_LLM_MODEL}')...")
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
    """LLM handler for the Google Gemini API with structured output support."""
    # Initializes the Gemini client.
    def _initialize_client(self):
        try:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key: raise ValueError("GOOGLE_API_KEY not found.")
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(GEMINI_LLM_MODEL)
        except Exception as e:
            print(f"Error initializing Gemini LLM client: {e}")
            return None

    # Gets a chat completion from the Gemini LLM with structured output.
    def get_chat_completion(self, message_history):
        print(f"Sending message history to Gemini ('{GEMINI_LLM_MODEL}') with structured output...")
        
        system_prompt = None
        gemini_history = []
        for msg in message_history:
            role = msg.get("role")
            content = msg.get("content_raw") if role == "assistant" else msg.get("content")
            
            if role == "system":
                system_prompt = content
                continue
            
            # Gemini uses 'model' instead of 'assistant' for the AI's role
            gemini_role = "model" if role == "assistant" else "user"
            gemini_history.append({"role": gemini_role, "parts": [content]})
            
        try:
            # Gemini's API with structured output configuration using TypedDict
            model = genai.GenerativeModel(
                GEMINI_LLM_MODEL, 
                system_instruction=system_prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": GeminiResponseSchema
                }
            )
            chat = model.start_chat(history=gemini_history[:-1]) # History without the last user message
            response = chat.send_message(
                gemini_history[-1]['parts'], # Send only the last user message
                safety_settings={ # Safety settings to prevent unnecessary blocks
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                }
            )
            
            # Parse structured JSON response
            response_json = json.loads(response.text)
            response_text = response_json.get("response_text", "")
            expression = response_json.get("expression", "Normal")
            
            # Format response with expression appended (for compatibility with existing parsing)
            formatted_response = f"{response_text}\n{expression}"
            
            # Gemini returns usage info in 'usage_metadata'
            usage_info = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count
            }
            return {"response": formatted_response, "usage": usage_info, "error": None}

        except Exception as e:
            print(f"Error in Gemini LLM chat: {e}")
            return {"response": None, "usage": None, "error": str(e)}

# Factory function to get the configured LLM handler.
def get_llm_handler() -> LLMHandler:
    provider = LLM_PROVIDER.lower()
    if provider == 'groq':
        return GroqLLMHandler()
    elif provider == 'gemini':
        return GeminiLLMHandler()
    elif provider == 'openrouter':
        return OpenRouterLLMHandler()
    else:
        raise ValueError(f"Unsupported LLM provider: '{LLM_PROVIDER}'. Check config.py.")