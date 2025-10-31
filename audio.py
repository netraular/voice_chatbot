# audio.py
import os
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import datetime

# --- CONFIGURATION ---
SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_DIR = "audio_files"

class AudioRecorder:
    """Handles audio recording using sounddevice."""
    def __init__(self, waveform_callback=None):
        self.is_recording = False
        self.audio_data = []
        self.stream = None
        self.waveform_callback = waveform_callback
        os.makedirs(AUDIO_DIR, exist_ok=True)

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

    def save(self):
        if not self.audio_data:
            print("No audio data to save.")
            return None
        
        recording = np.concatenate(self.audio_data, axis=0)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rec_{timestamp}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        write(filepath, SAMPLE_RATE, recording)
        print(f"Audio saved to {filepath}")
        return filepath