# ui.py
import tkinter as tk
from tkinter import scrolledtext
import threading
import os
import datetime
import json

# ... (otras importaciones no cambian)
from audio import AudioRecorder
from groq_api import GroqHandler
from google_cloud_api import GoogleTTSHandler
from audio_player import AudioPlayer

CONVERSATIONS_DIR = "conversations"

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        # ... (configuración de la ventana no cambia)
        self.title("Groq Voice Assistant")
        self.geometry("480x480")
        self.resizable(False, False)

        # Initialize handlers (no cambia)
        self.groq_handler = GroqHandler()
        self.recorder = AudioRecorder(waveform_callback=self.update_waveform)
        self.tts_handler = GoogleTTSHandler()
        self.audio_player = AudioPlayer()
        
        ## NUEVA LÓGICA DE GESTIÓN DE SESIÓN ##
        self.turn_counter = 0
        self.conversation_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_path = os.path.join(CONVERSATIONS_DIR, self.conversation_id)
        os.makedirs(self.conversation_path, exist_ok=True)
        print(f"Saving conversation to: {self.conversation_path}")

        # Initialize chat history (no cambia)
        self.chat_history = [
            {"role": "system", "content": "Eres un asistente servicial. Mantén tus respuestas concisas y en español."}
        ]

        self.create_widgets()
        self.setup_idle_ui()

    ## MÉTODO PRINCIPAL MODIFICADO ##
    def process_and_respond(self, user_audio_path):
        # Step 1: Transcribe the audio
        transcribed_text = self.groq_handler.transcribe(user_audio_path)
        if not transcribed_text or transcribed_text.startswith("Error:"):
            self.after(0, self.add_message, "System", "No pude entender el audio. Por favor, inténtalo de nuevo.")
            self.after(0, self.setup_idle_ui)
            return

        self.after(0, self.add_message, "Tú", transcribed_text)
        self.chat_history.append({"role": "user", "content": transcribed_text})

        # Step 2: Send history to LLM
        self.after(0, self.add_message, "Groq", "Pensando...")
        llm_response = self.groq_handler.get_chat_completion(self.chat_history)
        self.chat_history.append({"role": "assistant", "content": llm_response})
        
        # Step 3: Save the updated conversation log
        self.save_chat_history()

        # Step 4: Synthesize speech from LLM response
        audio_content = self.tts_handler.synthesize_speech(llm_response)

        # Step 5: Save the assistant's audio response
        if audio_content:
            assistant_audio_path = os.path.join(self.conversation_path, f"assistant_{self.turn_counter}.mp3")
            with open(assistant_audio_path, "wb") as f:
                f.write(audio_content)
            print(f"Assistant audio saved to {assistant_audio_path}")

        # Step 6: Update UI and play audio
        self.after(0, self.update_last_message, llm_response)
        self.audio_player.play(audio_content)

        # Step 7: Increment turn counter and reset UI
        self.turn_counter += 1
        self.after(0, self.setup_idle_ui)

    def send_recording_flow(self):
        self.send_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        self.recorder.stop()
        self.add_message("Sistema", "Procesando audio...")
        
        # Construye la ruta para el audio del usuario y lo guarda
        user_audio_path = os.path.join(self.conversation_path, f"user_{self.turn_counter}.wav")
        saved_path = self.recorder.save(user_audio_path)
        
        if saved_path:
            threading.Thread(target=self.process_and_respond, args=(saved_path,)).start()
        else:
            self.add_message("Sistema", "No se grabó audio.")
            self.setup_idle_ui()
    
    ## NUEVA FUNCIÓN AUXILIAR ##
    def save_chat_history(self):
        log_path = os.path.join(self.conversation_path, "chat_history.json")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            print(f"Chat history saved to {log_path}")
        except Exception as e:
            print(f"Failed to save chat history: {e}")

    # ... El resto del archivo (widgets, etc.) no necesita cambios ...
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

    def setup_idle_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        self.record_button = tk.Button(self.control_frame, text="Grabar", font=("Arial", 12), command=self.start_recording_flow)
        self.record_button.place(relx=0.5, rely=0.5, anchor="center")

    def setup_recording_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        self.cancel_button = tk.Button(self.control_frame, text="Cancelar", command=self.cancel_recording_flow)
        self.cancel_button.grid(row=0, column=0, sticky="w")
        self.waveform_canvas = tk.Canvas(self.control_frame, height=40, bg="black")
        self.waveform_canvas.grid(row=0, column=1, sticky="ew", padx=10)
        self.send_button = tk.Button(self.control_frame, text="Enviar", command=self.send_recording_flow)
        self.send_button.grid(row=0, column=2, sticky="e")

    def start_recording_flow(self):
        self.setup_recording_ui()
        self.recorder.start()
        self.add_message("Sistema", "Escuchando... Pulsa 'Enviar' cuando termines.")

    def cancel_recording_flow(self):
        self.recorder.stop()
        self.setup_idle_ui()
        self.add_message("Sistema", "Grabación cancelada.")

    def add_message(self, sender, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"{sender}: {text}\n\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)
    
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

    def update_waveform(self, data):
        self.after(0, self._draw_waveform, data)

    def _draw_waveform(self, data):
        import numpy as np
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