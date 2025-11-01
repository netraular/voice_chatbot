# audio.py
import os
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import datetime

from config import SAMPLE_RATE, CHANNELS

class AudioRecorder:
    # Initializes the audio recorder.
    def __init__(self, waveform_callback=None):
        self.is_recording = False
        self.audio_data = []
        self.stream = None
        self.waveform_callback = waveform_callback

    # Callback function to process audio chunks during recording.
    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_data.append(indata.copy())
        if self.waveform_callback:
            self.waveform_callback(indata.copy())

    # Starts the audio recording stream.
    def start(self):
        self.audio_data = []
        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=self._audio_callback,
            dtype='int16'
        )
        self.stream.start()
        print("Recording started.")

    # Stops the audio recording stream.
    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.is_recording = False
        print("Recording stopped.")

    # Saves the recorded audio to a WAV file.
    def save(self, filepath):
        if not self.audio_data:
            print("No audio data to save.")
            return None
        
        recording = np.concatenate(self.audio_data, axis=0)
        
        try:
            write(filepath, SAMPLE_RATE, recording)
            print(f"Audio saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"Failed to save audio to {filepath}: {e}")
            return None