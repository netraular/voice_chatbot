# ui.py
import tkinter as tk
from tkinter import scrolledtext, font
import threading
import os
import datetime
import numpy as np
import re

# New modular imports
from audio import AudioRecorder
from audio_player import AudioPlayer
from assistant import VoiceAssistant
from config import CONVERSATIONS_DIR

# Main application class inheriting from tkinter.Tk.
class Application(tk.Tk):
    # Initializes the main application window and its components.
    def __init__(self):
        super().__init__()
        self.title("Groq Voice Assistant")
        self.geometry("480x480")
        self.resizable(False, False)

        self.recorder = AudioRecorder(waveform_callback=self.update_waveform)
        self.audio_player = AudioPlayer()
        
        self.conversation_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.assistant = VoiceAssistant(self.conversation_id)
        
        self.turn_counter = 0
        self.conversation_path = os.path.join(CONVERSATIONS_DIR, self.conversation_id)
        
        self.create_widgets()
        self.setup_idle_ui()

    # Configures text styles (tags) for the chat text area.
    def setup_text_styles(self):
        action_font = font.Font(family="Arial", size=12, slant="italic")
        self.text_area.tag_configure("action", foreground="grey", font=action_font)
        bold_font = font.Font(family="Arial", size=12, weight="bold")
        self.text_area.tag_configure("bold", font=bold_font)
        self.text_area.tag_configure("list_item", lmargin1=20, lmargin2=20)

    # Inserts text with markdown-like styling...
    def _insert_styled_text(self, text, prefix=""):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, prefix)
        inline_pattern = re.compile(r'(\*\*.*?\*\*)|(\*.*?\*)')
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_start_index = self.text_area.index(tk.END)
            last_end = 0
            for match in inline_pattern.finditer(line):
                start, end = match.span()
                self.text_area.insert(tk.END, line[last_end:start])
                matched_text = match.group(0)
                if matched_text.startswith('**') and matched_text.endswith('**'):
                    self.text_area.insert(tk.END, matched_text[2:-2], "bold")
                elif matched_text.startswith('*') and matched_text.endswith('*'):
                    self.text_area.insert(tk.END, matched_text[1:-1], "action")
                last_end = end
            self.text_area.insert(tk.END, line[last_end:])
            if line.strip().startswith(('-', '*')) or re.match(r'^\s*\d+\.', line.strip()):
                self.text_area.tag_add("list_item", line_start_index, f"{line_start_index} lineend")
            if i < len(lines) - 1:
                self.text_area.insert(tk.END, '\n')
        self.text_area.insert(tk.END, "\n\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

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
        start_index = self.text_area.search("Bot: Thinking...", "1.0", stopindex="end", backwards=True)
        if start_index:
            end_index = f"{start_index} + {len('Bot: Thinking...')} chars"
            self.text_area.delete(start_index, end_index)
            self.text_area.mark_set("insert", start_index)
            self._insert_styled_text(new_text, prefix="Bot: ")
        else:
            self.add_message("Bot", new_text)
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)
    
    # --- UI FLOW METHODS (MODIFIED) ---

    def start_recording_flow(self):
        self.audio_player.stop()
        self.setup_recording_ui()
        self.recorder.start()
        self.add_message("System", "Listening... Press 'Send' when you're done.")

    def send_recording_flow(self):
        self.setup_processing_ui("Transcribing...") # Step 1: Show "Transcribing"
        threading.Thread(target=self._transcribe_audio_thread).start()

    def cancel_recording_flow(self):
        self.recorder.stop()
        self.setup_idle_ui()
        self.add_message("System", "Recording canceled.")

    # --- BACKGROUND THREADS AND HANDLERS (MODIFIED) ---

    def _transcribe_audio_thread(self):
        """Thread for Step 1: Save audio and transcribe."""
        self.recorder.stop()
        user_audio_path = os.path.join(self.conversation_path, f"user_{self.turn_counter}.wav")
        saved_path = self.recorder.save(user_audio_path)
        
        if saved_path:
            transcription_result = self.assistant.transcribe_and_update_history(saved_path)
            self.after(0, self.handle_transcription_result, transcription_result)
        else:
            self.after(0, self.add_message, "System", "No audio was recorded.")
            self.after(0, self.setup_idle_ui)

    def handle_transcription_result(self, result):
        """UI update after transcription. Kicks off the next step."""
        if result.get("error"):
            self.add_message("System", result["error"])
            self.setup_idle_ui()
            return

        # Show user's transcribed text in the chat
        self.add_message("You", result["user_text"])
        
        # Now, show "Thinking..."
        self.add_message("Bot", "Thinking...")
        self.setup_processing_ui("Thinking...") # Step 2: Show "Thinking" in control frame
        
        # Start the LLM response generation in a new thread
        threading.Thread(target=self._get_assistant_response_thread).start()

    def _get_assistant_response_thread(self):
        """Thread for Step 2: Get LLM response and TTS."""
        response_result = self.assistant.generate_assistant_response(self.turn_counter)
        self.after(0, self.handle_final_response, response_result)

    def handle_final_response(self, result):
        """Final UI update with the assistant's response and audio."""
        if result.get("error"):
            self.update_last_message(result["error"])
            self.setup_idle_ui()
            return
        
        self.update_last_message(result["assistant_ui_text"])
        self.setup_idle_ui()
        self.audio_player.play(result["audio_content"])
        self.turn_counter += 1

    # --- UI SETUP METHODS ---
    
    def setup_processing_ui(self, text="Processing..."):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        loading_font = font.Font(family='Helvetica', size=14)
        self.loading_label = tk.Label(self.control_frame, text=text, font=loading_font)
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")

    def setup_idle_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        self.record_button = tk.Button(self.control_frame, text="Record", font=("Arial", 12), command=self.start_recording_flow)
        self.record_button.place(relx=0.5, rely=0.5, anchor="center")
    
    def setup_recording_ui(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        self.cancel_button = tk.Button(self.control_frame, text="Cancel", command=self.cancel_recording_flow)
        self.cancel_button.grid(row=0, column=0, sticky="w")
        self.waveform_canvas = tk.Canvas(self.control_frame, height=40, bg="black")
        self.waveform_canvas.grid(row=0, column=1, sticky="ew", padx=10)
        self.send_button = tk.Button(self.control_frame, text="Send", command=self.send_recording_flow)
        self.send_button.grid(row=0, column=2, sticky="e")

    # --- WAVEFORM DRAWING ---

    def update_waveform(self, data):
        self.after(0, self._draw_waveform, data)

    def _draw_waveform(self, data):
        if not hasattr(self, 'waveform_canvas') or not self.waveform_canvas.winfo_exists(): return
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
        if len(coords) > 1: canvas.create_line(coords, fill="lime", width=1)