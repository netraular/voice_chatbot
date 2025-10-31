# audio_player.py
import pygame
import io

class AudioPlayer:
    """
    Plays audio data using pygame in a non-blocking way.
    """
    def __init__(self):
        try:
            pygame.mixer.init()
            print("AudioPlayer (pygame) initialized.")
        except Exception as e:
            print(f"Could not initialize pygame mixer: {e}")

    def play(self, audio_bytes):
        """
        Starts playing audio from bytes. This is NON-BLOCKING.
        """
        if not audio_bytes or not pygame.mixer.get_init():
            return
        
        try:
            audio_stream = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            print("Started playback of assistant's response...")
        except Exception as e:
            print(f"Error playing audio: {e}")

    def stop(self):
        """
        Stops any currently playing audio immediately.
        """
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            print("Audio playback interrupted.")