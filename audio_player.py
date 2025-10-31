# audio_player.py
import pygame
import io
import time

class AudioPlayer:
    """
    Plays audio data using pygame.
    """
    def __init__(self):
        try:
            pygame.mixer.init()
            print("AudioPlayer (pygame) initialized.")
        except Exception as e:
            print(f"Could not initialize pygame mixer: {e}")

    def play(self, audio_bytes):
        """
        Plays audio from bytes. This method blocks until playback is complete.
        """
        if not audio_bytes or not pygame.mixer.get_init():
            return
        
        try:
            # Use BytesIO to treat the byte string as a file
            audio_stream = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            print("Playing assistant's response...")
            
            # Block and wait for the music to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            print("Playback finished.")

        except Exception as e:
            print(f"Error playing audio: {e}")