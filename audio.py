# audio.py
import os
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import datetime

# --- CONFIGURATION (Imported) ---
from config import SAMPLE_RATE, CHANNELS

class AudioRecorder:
    def __init__(self, waveform_callback=None):
        self.is_recording = False
        self.audio_data = []
        self.stream = None
        self.waveform_callback = waveform_callback

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_data.append(indata.copy())
        if self.waveform_callback:
            self.waveform_callback(indata.copy())

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

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.is_recording = False
        print("Recording stopped.")

    def save(self, filepath):
        """
        Saves the recorded audio to the specified filepath.
        Returns the filepath if successful, otherwise None.
        """
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