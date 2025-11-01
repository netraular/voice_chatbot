# ui.py
import tkinter as tk
from tkinter import scrolledtext, font
import threading
import os
import datetime
import json
import numpy as np

from audio import AudioRecorder
from groq_api import GroqHandler
from google_cloud_api import GoogleTTSHandler
from audio_player import AudioPlayer

CONVERSATIONS_DIR = "conversations"

class Application(tk.Tk):
    # Initializes the main application window and components.
    def __init__(self):
        super().__init__()
        self.title("Groq Voice Assistant")
        self.geometry("480x480")
        self.resizable(False, False)

        self.groq_handler = GroqHandler()
        self.recorder = AudioRecorder(waveform_callback=self.update_waveform)
        self.tts_handler = GoogleTTSHandler()
        self.audio_player = AudioPlayer()
        
        self.turn_counter = 0
        self.conversation_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_path = os.path.join(CONVERSATIONS_DIR, self.conversation_id)
        os.makedirs(self.conversation_path, exist_ok=True)
        print(f"Saving conversation to: {self.conversation_path}")
        
        self.chat_history = [
            {"role": "system", "content": "Eres un asistente servicial. Tus respuestas deben ser muy cortas, no más de dos o tres frases. Ve directo al punto. Responde siempre en español."}
        ]
        
        self.create_widgets()
        self.setup_idle_ui()

    # Changes the UI to a "Thinking..." state.
    def setup_processing_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        loading_font = font.Font(family='Helvetica', size=14)
        self.loading_label = tk.Label(self.control_frame, text="Pensando...", font=loading_font)
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")

    # Resets the UI to its initial state with the "Record" button.
    def setup_idle_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        self.record_button = tk.Button(self.control_frame, text="Grabar", font=("Arial", 12), command=self.start_recording_flow)
        self.record_button.place(relx=0.5, rely=0.5, anchor="center")
    
    # Starts the audio recording process.
    def start_recording_flow(self):
        self.audio_player.stop()
        self.setup_recording_ui()
        self.recorder.start()
        self.add_message("Sistema", "Escuchando... Pulsa 'Enviar' cuando termines.")

    # Handles the "Send" button click to start processing.
    def send_recording_flow(self):
        self.setup_processing_ui()
        self.add_message("Sistema", "Procesando audio...")
        threading.Thread(target=self._process_audio_thread).start()

    # Runs in a separate thread to avoid freezing the UI.
    def _process_audio_thread(self):
        self.recorder.stop()
        user_audio_path = os.path.join(self.conversation_path, f"user_{self.turn_counter}.wav")
        saved_path = self.recorder.save(user_audio_path)
        
        if saved_path:
            self.process_and_respond(saved_path)
        else:
            self.after(0, self.add_message, "Sistema", "No se grabó audio.")
            self.after(0, self.setup_idle_ui)

    # Full logic loop: transcribe, get LLM response, and prepare audio.
    def process_and_respond(self, user_audio_path):
        transcribed_text = self.groq_handler.transcribe(user_audio_path)
        if not transcribed_text or transcribed_text.startswith("Error:"):
            self.after(0, self.add_message, "Sistema", "No pude entender el audio.")
            self.after(0, self.setup_idle_ui)
            return

        self.after(0, self.add_message, "Tú", transcribed_text)
        
        user_message = {
            "role": "user", 
            "content": transcribed_text,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.chat_history.append(user_message)
        
        self.after(0, self.add_message, "Groq", "Pensando...")
        
        llm_data = self.groq_handler.get_chat_completion(self.chat_history)
        
        # Explicitly check for an error from the API handler.
        if llm_data.get("error"):
            error_message = llm_data["error"]
            print(f"An error occurred: {error_message}")
            self.after(0, self.update_last_message, "Ha ocurrido un error.")
            self.chat_history.append({"role": "system", "content": f"[ERROR] {error_message}"})
            self.save_chat_history()
            self.after(0, self.setup_idle_ui)
            return

        llm_response = llm_data["response"]
        usage_info = llm_data["usage"]

        if not llm_response or not llm_response.strip():
            error_message = "No pude generar una respuesta. Inténtalo de nuevo."
            self.after(0, self.update_last_message, error_message)
            self.chat_history.append({"role": "assistant", "content": f"[{error_message}]"})
            self.save_chat_history()
            self.after(0, self.setup_idle_ui)
            return

        assistant_message = {"role": "assistant", "content": llm_response}
        
        if usage_info:
            self.chat_history[-1]["prompt_tokens"] = usage_info["prompt_tokens"]
            assistant_message["completion_tokens"] = usage_info["completion_tokens"]
            assistant_message["completion_time"] = usage_info["completion_time"]

        self.chat_history.append(assistant_message)
        self.save_chat_history()
        
        audio_content = self.tts_handler.synthesize_speech(llm_response)
        if audio_content:
            assistant_audio_path = os.path.join(self.conversation_path, f"assistant_{self.turn_counter}.mp3")
            with open(assistant_audio_path, "wb") as f:
                f.write(audio_content)
        self.after(0, self.handle_response_playback, llm_response, audio_content)

    # Updates the UI with the final response and plays the audio.
    def handle_response_playback(self, llm_response, audio_content):
        self.update_last_message(llm_response)
        self.setup_idle_ui()
        self.audio_player.play(audio_content)
        self.turn_counter += 1
    
    # Creates the initial GUI widgets.
    def create_widgets(self):
        self.control_frame = tk.Frame(self, height=60)
        self.control_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.control_frame.pack_propagate(False)
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 12))
        self.text_area.pack(pady=(10, 0), padx=10, expand=True, fill="both")
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=2)
        self.control_frame.grid_columnconfigure(2, weight=1)
        self.add_message("Sistema", "¡Bienvenido! Presiona 'Grabar' para hablar con el asistente.")

    # Changes the UI to the recording state.
    def setup_recording_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        self.cancel_button = tk.Button(self.control_frame, text="Cancelar", command=self.cancel_recording_flow)
        self.cancel_button.grid(row=0, column=0, sticky="w")
        self.waveform_canvas = tk.Canvas(self.control_frame, height=40, bg="black")
        self.waveform_canvas.grid(row=0, column=1, sticky="ew", padx=10)
        self.send_button = tk.Button(self.control_frame, text="Enviar", command=self.send_recording_flow)
        self.send_button.grid(row=0, column=2, sticky="e")

    # Handles the cancellation of a recording.
    def cancel_recording_flow(self):
        self.recorder.stop()
        self.setup_idle_ui()
        self.add_message("Sistema", "Grabación cancelada.")

    # Adds a new message to the chat text area.
    def add_message(self, sender, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"{sender}: {text}\n\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)
    
    # Replaces the "Thinking..." placeholder with the final LLM response.
    def update_last_message(self, new_text):
        self.text_area.config(state=tk.NORMAL)
        start_index = self.text_area.search("Groq: Pensando...", "1.0", stopindex="end", backwards=True)
        if start_index:
            end_index = f"{start_index} + {len('Groq: Pensando...')} chars"
            self.text_area.delete(start_index, end_index)
            self.text_area.insert(start_index, f"Groq: {new_text}")
        else:
            self.add_message("Groq", new_text)
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    # Receives audio data and schedules the waveform to be redrawn.
    def update_waveform(self, data):
        self.after(0, self._draw_waveform, data)

    # Draws the audio waveform on the canvas.
    def _draw_waveform(self, data):
        if not hasattr(self, 'waveform_canvas') or not self.waveform_canvas.winfo_exists():
            return
        canvas = self.waveform_canvas
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        center_y = height / 2
        if width <= 1 or height <= 1: return
        normalized_data = (data.flatten() / 32768.0) * center_y
        step = max(1, len(normalized_data) // width)
        coords = []
        for i, sample in enumerate(normalized_data[::step]):
            x = (i / (len(normalized_data[::step]) -1)) * width if len(normalized_data[::step]) > 1 else width / 2
            coords.append((x, center_y - sample))
        if len(coords) > 1:
            canvas.create_line(coords, fill="lime", width=1)
            
    # Saves the entire conversation history to a JSON file.
    def save_chat_history(self):
        log_path = os.path.join(self.conversation_path, "chat_history.json")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            print(f"Chat history saved to {log_path}")
        except Exception as e:
            print(f"Failed to save chat history: {e}")