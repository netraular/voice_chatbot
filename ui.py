# ui.py
import tkinter as tk
from tkinter import scrolledtext, font
import threading
import os
import datetime
import json
import numpy as np
import re

from audio import AudioRecorder
from groq_api import GroqHandler
from google_cloud_api import GoogleTTSHandler
from audio_player import AudioPlayer

CONVERSATIONS_DIR = "conversations"

# --- UPDATED PARSING FUNCTION ---
# Parses and cleans the LLM response for UI display and Text-to-Speech.
def parse_and_clean_llm_response(text: str) -> dict:
    if not isinstance(text, str):
        return {"for_ui": "", "for_tts": ""}

    raw_text = text

    # --- 1. Generate text for the UI ---
    # Remove unsupported markdown: code blocks, images. Keep link text.
    ui_text = re.sub(r'```.*?```', '', raw_text, flags=re.DOTALL)
    ui_text = re.sub(r'`[^`]*`', '', ui_text) # <-- Removes inline code like `this`
    ui_text = re.sub(r'!\[.*?\]\(.*?\)', '', ui_text)
    ui_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', ui_text)
    ui_text = re.sub(r'(\*\*|__|\*|_)\s*\1', '', ui_text)
    ui_text = ui_text.strip()

    # --- 2. Generate text for TTS (aggressive cleaning) ---
    tts_text = raw_text
    
    # CORRECTED: Remove code snippets first
    tts_text = re.sub(r'`[^`]*`', '', tts_text)
    tts_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', tts_text)
    tts_text = re.sub(r'\s?\*.*?\*\s?', ' ', tts_text)
    tts_text = re.sub(r'\*\*(.*?)\*\*', r'\1', tts_text)
    tts_text = re.sub(r'^\s*[-*#]+\s*', '', tts_text, flags=re.MULTILINE)
    tts_text = re.sub(r'[^\w\s.,¡!¿?áéíóúÁÉÍÓÚñÑ]', '', tts_text)
    tts_text = re.sub(r'\s+', ' ', tts_text).strip()

    return {
        "for_ui": ui_text,
        "for_tts": tts_text
    }

# Main application class inheriting from tkinter.Tk.
class Application(tk.Tk):
    # Initializes the main application window and its components.
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
            {
                "role": "system", 
                "content": (
                    "Eres Marc, un chico joven. Hablas de manera natural y relajada, como si estuvieras charlando con un amigo. "
                    "Mantén tus respuestas breves, de una o dos frases, pero completas y descriptivas como haciendo roleplay. Responde siempre en castellano. "
                    "La única regla es que todas tus acciones físicas o emociones deben ir entre asteriscos, de forma descriptiva. "
                    "Por ejemplo: *(levanta una ceja, curioso.)* o *(se apoya en la pared, cruzando los brazos)*. "
                    "No uses ningún otro tipo de formato o símbolos especiales."
                    "Mantente siempre en el personaje."
                )
            }
        ]
        
        self.create_widgets()
        self.setup_idle_ui()

    # Configures text styles (tags) for the chat text area.
    def setup_text_styles(self):
        action_font = font.Font(family="Arial", size=12, slant="italic")
        self.text_area.tag_configure("action", foreground="grey", font=action_font)

        bold_font = font.Font(family="Arial", size=12, weight="bold")
        self.text_area.tag_configure("bold", font=bold_font)
        
        self.text_area.tag_configure("list_item", lmargin1=20, lmargin2=20)

    # Inserts text with markdown-like styling (bold, italic, lists) into the text area.
    def _insert_styled_text(self, text, prefix=""):
        """
        Inserts text line by line, applying block styles (lists)
        and then inline styles (bold, italic) to allow nesting.
        """
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, prefix)

        # Pattern for inline styles only (bold and italic/action)
        inline_pattern = re.compile(r'(\*\*.*?\*\*)|(\*.*?\*)')
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Save the start position of the line to apply the list tag later
            line_start_index = self.text_area.index(tk.END)
            
            last_end = 0
            for match in inline_pattern.finditer(line):
                start, end = match.span()
                
                # Insert plain text before the styled fragment
                self.text_area.insert(tk.END, line[last_end:start])
                
                matched_text = match.group(0)
                if matched_text.startswith('**') and matched_text.endswith('**'):
                    content = matched_text[2:-2]
                    self.text_area.insert(tk.END, content, "bold")
                elif matched_text.startswith('*') and matched_text.endswith('*'):
                    content = matched_text[1:-1]
                    self.text_area.insert(tk.END, content, "action")
                
                last_end = end
            
            # Insert the rest of the line
            self.text_area.insert(tk.END, line[last_end:])

            # Apply list style to the entire line if applicable
            if line.strip().startswith(('-', '*')) or re.match(r'^\s*\d+\.', line.strip()):
                self.text_area.tag_add("list_item", line_start_index, f"{line_start_index} lineend")

            # Add a newline, except for the last line of the message
            if i < len(lines) - 1:
                self.text_area.insert(tk.END, '\n')

        # Add final spacing between messages
        self.text_area.insert(tk.END, "\n\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    # Handles the entire conversation turn from user audio to assistant response.
    def process_and_respond(self, user_audio_path):
        transcribed_text = self.groq_handler.transcribe(user_audio_path)
        if not transcribed_text or transcribed_text.startswith("Error:"):
            self.after(0, self.add_message, "System", "Could not understand the audio.")
            self.after(0, self.setup_idle_ui)
            return

        self.after(0, self.add_message, "You", transcribed_text)
        
        user_message = {
            "role": "user", "content": transcribed_text,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.chat_history.append(user_message)
        self.after(0, self.add_message, "Groq", "Thinking...")
        
        llm_data = self.groq_handler.get_chat_completion(self.chat_history)
        
        if llm_data.get("error"):
            error_message = llm_data["error"]
            print(f"An error occurred: {error_message}")
            self.after(0, self.update_last_message, "An error occurred.")
            self.chat_history.append({"role": "system", "content": f"[ERROR] {error_message}"})
            self.save_chat_history()
            self.after(0, self.setup_idle_ui)
            return

        raw_llm_response = llm_data["response"]
        usage_info = llm_data["usage"]

        if not raw_llm_response or not raw_llm_response.strip():
            error_message = "Could not generate a response. Please try again."
            self.after(0, self.update_last_message, error_message)
            self.chat_history.append({"role": "assistant", "content": f"[{error_message}]"})
            self.save_chat_history()
            self.after(0, self.setup_idle_ui)
            return

        processed_text = parse_and_clean_llm_response(raw_llm_response)
        
        assistant_message = {
            "role": "assistant",
            "content_raw": raw_llm_response,
            "content_ui": processed_text["for_ui"],
            "content_tts": processed_text["for_tts"]
        }
        
        if usage_info:
            self.chat_history[-1]["prompt_tokens"] = usage_info["prompt_tokens"]
            assistant_message["completion_tokens"] = usage_info["completion_tokens"]
            assistant_message["completion_time"] = usage_info["completion_time"]

        self.chat_history.append(assistant_message)
        self.save_chat_history()
        
        audio_content = self.tts_handler.synthesize_speech(processed_text["for_tts"])
        if audio_content:
            assistant_audio_path = os.path.join(self.conversation_path, f"assistant_{self.turn_counter}.mp3")
            with open(assistant_audio_path, "wb") as f:
                f.write(audio_content)
        
        self.after(0, self.handle_response_playback, processed_text["for_ui"], audio_content)

    # Creates and lays out the main UI widgets.
    def create_widgets(self):
        self.control_frame = tk.Frame(self, height=60)
        self.control_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.control_frame.pack_propagate(False)
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 12))
        self.text_area.pack(pady=(10, 0), padx=10, expand=True, fill="both")
        
        self.setup_text_styles()

        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=2)
        self.control_frame.grid_columnconfigure(2, weight=1)
        self.add_message("System", "Welcome! Press 'Record' to speak with the assistant.")

    # Adds a new message to the chat display.
    def add_message(self, sender, text):
        self._insert_styled_text(text, prefix=f"{sender}: ")

    # Replaces the "Thinking..." message with the final response.
    def update_last_message(self, new_text):
        self.text_area.config(state=tk.NORMAL)
        start_index = self.text_area.search("Groq: Thinking...", "1.0", stopindex="end", backwards=True)
        if start_index:
            end_index = f"{start_index} + {len('Groq: Thinking...')} chars"
            self.text_area.delete(start_index, end_index)
            self.text_area.mark_set("insert", start_index)
            self._insert_styled_text(new_text, prefix="Groq: ")
        else:
            self.add_message("Groq", new_text)
            
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)
    
    # Updates the UI with the final response and plays the synthesized audio.
    def handle_response_playback(self, llm_response, audio_content):
        self.update_last_message(llm_response)
        self.setup_idle_ui()
        self.audio_player.play(audio_content)
        self.turn_counter += 1

    # Changes the UI to a "thinking" or processing state.
    def setup_processing_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        loading_font = font.Font(family='Helvetica', size=14)
        self.loading_label = tk.Label(self.control_frame, text="Thinking...", font=loading_font)
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")

    # Sets the UI to its default state with the "Record" button.
    def setup_idle_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        self.record_button = tk.Button(self.control_frame, text="Record", font=("Arial", 12), command=self.start_recording_flow)
        self.record_button.place(relx=0.5, rely=0.5, anchor="center")
    
    # Starts the audio recording process and updates the UI.
    def start_recording_flow(self):
        self.audio_player.stop()
        self.setup_recording_ui()
        self.recorder.start()
        self.add_message("System", "Listening... Press 'Send' when you're done.")

    # Stops recording and starts the processing thread.
    def send_recording_flow(self):
        self.setup_processing_ui()
        self.add_message("System", "Processing audio...")
        threading.Thread(target=self._process_audio_thread).start()

    # Runs in a background thread to save and process the recorded audio.
    def _process_audio_thread(self):
        self.recorder.stop()
        user_audio_path = os.path.join(self.conversation_path, f"user_{self.turn_counter}.wav")
        saved_path = self.recorder.save(user_audio_path)
        
        if saved_path:
            self.process_and_respond(saved_path)
        else:
            self.after(0, self.add_message, "System", "No audio was recorded.")
            self.after(0, self.setup_idle_ui)
            
    # Changes the UI to the recording state (waveform, cancel, send buttons).
    def setup_recording_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        self.cancel_button = tk.Button(self.control_frame, text="Cancel", command=self.cancel_recording_flow)
        self.cancel_button.grid(row=0, column=0, sticky="w")
        self.waveform_canvas = tk.Canvas(self.control_frame, height=40, bg="black")
        self.waveform_canvas.grid(row=0, column=1, sticky="ew", padx=10)
        self.send_button = tk.Button(self.control_frame, text="Send", command=self.send_recording_flow)
        self.send_button.grid(row=0, column=2, sticky="e")

    # Stops the recording and reverts the UI to the idle state.
    def cancel_recording_flow(self):
        self.recorder.stop()
        self.setup_idle_ui()
        self.add_message("System", "Recording canceled.")

    # Callback from the recorder to trigger a waveform redraw on the main thread.
    def update_waveform(self, data):
        self.after(0, self._draw_waveform, data)

    # Draws the audio waveform data on the canvas.
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