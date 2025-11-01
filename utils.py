# utils.py
import re

def parse_and_clean_llm_response(text: str) -> dict:
    """
    Parses and cleans the LLM response for UI display and Text-to-Speech.
    """
    if not isinstance(text, str):
        return {"for_ui": "", "for_tts": ""}

    raw_text = text

    # --- 1. Generate text for the UI ---
    # Remove unsupported markdown: code blocks, images. Keep link text.
    ui_text = re.sub(r'```.*?```', '', raw_text, flags=re.DOTALL)
    ui_text = re.sub(r'`[^`]*`', '', ui_text) # <-- Removes inline code like `this`
    ui_text = re.sub(r'!\[.*?\]\(.*?\)', '', ui_text)
    ui_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', ui_text)
    # This regex was too aggressive for UI, removed: ui_text = re.sub(r'(\*\*|__|\*|_)\s*\1', '', ui_text)
    ui_text = ui_text.strip()

    # --- 2. Generate text for TTS (aggressive cleaning) ---
    tts_text = raw_text
    
    # Remove code snippets first
    tts_text = re.sub(r'`[^`]*`', '', tts_text)
    # Remove links, keeping the text
    tts_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', tts_text)
    # Remove phrases enclosed in single asterisks (like actions)
    tts_text = re.sub(r'\s?\*.*?\*\s?', ' ', tts_text)
    # Remove double asterisks (bold)
    tts_text = re.sub(r'\*\*(.*?)\*\*', r'\1', tts_text)
    # Remove list markers and headers
    tts_text = re.sub(r'^\s*[-*#]+\s*', '', tts_text, flags=re.MULTILINE)
    # Remove any character that isn't a word, space, or common punctuation in Spanish
    tts_text = re.sub(r'[^\w\s.,¡!¿?áéíóúÁÉÍÓÚñÑ]', '', tts_text)
    # Collapse multiple spaces into one
    tts_text = re.sub(r'\s+', ' ', tts_text).strip()

    return {
        "for_ui": ui_text,
        "for_tts": tts_text
    }