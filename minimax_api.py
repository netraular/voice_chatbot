import os
import requests
from dotenv import load_dotenv
from config import MINIMAX_VOICE_ID, MINIMAX_MODEL

load_dotenv()

class MiniMaxTTSHandler:
    def __init__(self):
        self.api_key = os.environ.get("MINIMAX_API_KEY")
        self.voice_id = MINIMAX_VOICE_ID
        self.model = MINIMAX_MODEL
        self.url = "https://api.minimax.io/v1/t2a_v2"
        
        if not self.api_key:
            print("Warning: MINIMAX_API_KEY is not set. Please set it in your .env file.")


    def synthesize_speech(self, text):
        if not self.api_key:
            print("MiniMax API Key missing.")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": self.voice_id,
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0
            },
            "audio_setting": {
                "format": "mp3",
                "channel": 1,
                "sample_rate": 32000,
                "bitrate": 128000
            }
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API error status in body if status_code is 200 but logic failed
            if "base_resp" in data and data["base_resp"]["status_code"] != 0:
                 print(f"MiniMax API Error: {data['base_resp']['status_msg']}")
                 return None

            if "data" in data and "audio" in data["data"]:
                hex_audio = data["data"]["audio"]
                if hex_audio:
                    audio_content = bytes.fromhex(hex_audio)
                    print("MiniMax speech synthesized successfully.")
                    return audio_content
                else:
                    print("MiniMax returned empty audio data.")
                    return None
            else:
                print(f"Unexpected response format from MiniMax: {data}")
                return None

        except Exception as e:
            print(f"Error during MiniMax speech synthesis: {e}")
            if 'response' in locals():
                print(f"Response content: {response.text}")
            return None
