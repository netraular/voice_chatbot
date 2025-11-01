# audio_player.py
import pygame
import io

class AudioPlayer:
    """
    Plays audio data using pygame in a non-blocking way.
    """
    # Initializes the pygame mixer.
    def __init__(self):
        try:
            pygame.mixer.init()
            print("AudioPlayer (pygame) initialized.")
        except Exception as e:
            print(f"Could not initialize pygame mixer: {e}")

    # Starts playing audio from a byte stream.
    def play(self, audio_bytes):
        if not audio_bytes or not pygame.mixer.get_init():
            return
        
        try:
            audio_stream = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            print("Started playback of assistant's response...")
        except Exception as e:
            print(f"Error playing audio: {e}")

    # Stops any currently playing audio.
    def stop(self):
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            print("Audio playback interrupted.")