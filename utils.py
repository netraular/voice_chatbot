# utils.py
import re
from config import EXPRESSIONS_LIST

# Parses and cleans the LLM response for UI display and Text-to-Speech.
def parse_and_clean_llm_response(text: str) -> dict:
    if not isinstance(text, str):
        return {"for_ui": "", "for_tts": "", "expression": None}

    raw_text = text.strip()
    expression_found = None

    # Check if the text ends with one of the expressions
    for expression in EXPRESSIONS_LIST:
        # Check if it ends with the expression (case insensitive or exact? User said exact list, but let's be safe with strip)
        # Using regex to ensure it's the last word/line
        if raw_text.endswith(expression):
            expression_found = expression
            # Remove the expression from the end
            raw_text = raw_text[:-len(expression)].strip()
            break

    # --- 1. Generate text for the UI ---
    # Remove unsupported markdown but keep simple styling.
    ui_text = re.sub(r'```.*?```', '', raw_text, flags=re.DOTALL)
    ui_text = re.sub(r'`[^`]*`', '', ui_text)
    ui_text = re.sub(r'!\[.*?\]\(.*?\)', '', ui_text)
    ui_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', ui_text)
    ui_text = ui_text.strip()

    # --- 2. Generate text for TTS (aggressive cleaning) ---
    tts_text = raw_text
    
    # Remove code snippets.
    tts_text = re.sub(r'`[^`]*`', '', tts_text)
    # Remove links, keeping the text.
    tts_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', tts_text)
    # Remove phrases in asterisks (like actions) and any trailing period.
    tts_text = re.sub(r'\s?\*.*?\*\.?\s?', ' ', tts_text)
    # Remove double asterisks (bold).
    tts_text = re.sub(r'\*\*(.*?)\*\*', r'\1', tts_text)
    # Remove list markers and headers.
    tts_text = re.sub(r'^\s*[-*#]+\s*', '', tts_text, flags=re.MULTILINE)
    # Remove any character that isn't a word, space, or common punctuation in Spanish.
    tts_text = re.sub(r'[^\w\s.,¡!¿?áéíóúÁÉÍÓÚñÑ]', '', tts_text)
    # Collapse multiple spaces into one.
    tts_text = re.sub(r'\s+', ' ', tts_text).strip()

    return {
        "for_ui": ui_text,
        "for_tts": tts_text,
        "expression": expression_found
    }