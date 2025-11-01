# Modular Voice Chatbot with Multi-LLM Support

A modular desktop application that records audio, transcribes it, gets a response from a configurable Large Language Model (LLM), and speaks the response back to you. All conversations are automatically saved for later review and analysis.

## Features

-   **Full Voice Interaction Loop**: Speak, get a transcribed text, receive an LLM response, and hear it spoken aloud in a natural voice.
-   **Multi-LLM Provider Support**: Easily switch between different LLM providers by changing a single setting.
    -   **Groq**: For blazing-fast inference.
    -   **OpenRouter**: Access a wide variety of models, including free and open-source options.
    -   **Google Gemini**: Leverage Google's powerful family of models.
-   **High-Quality Speech Services**:
    -   **Transcription**: Powered by Groq's API using the `whisper-large-v3` model for fast and accurate speech-to-text.
    -   **Synthesis**: Uses Google Cloud's high-quality, natural-sounding Text-to-Speech voices.
-   **Automatic Conversation Logging**: Each time the app starts, a new unique folder is created in the `conversations/` directory. This folder stores:
    -   User's input audio as `user_X.wav`.
    -   The assistant's spoken response as `assistant_X.mp3`.
    -   A detailed log of the full conversation, including token usage and metadata, as `chat_history.json`.
-   **Clean, Modular Architecture**: The code is cleanly separated into modules for the User Interface (`ui.py`), core assistant logic (`assistant.py`), LLM abstraction (`llm_api.py`), audio handling, and individual API clients.
-   **Real-time Audio Visualization**: A simple waveform display confirms that the microphone is capturing audio during recording.

## Setup

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

-   Python 3.7+
-   A working microphone and speakers/headphones.
-   API keys for the services you intend to use (see Configuration section).

### 2. Installation

1.  **Clone or download the project:**
    Unzip or clone this repository into a local directory.

2.  **Create a virtual environment (recommended):**
    Open a terminal in the project's root directory and run:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Linux, use `source venv/bin/activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

You must configure API access for transcription, text-to-speech, and your chosen LLM.

#### Step 1: Set Your LLM Provider in `config.py`

Open the `config.py` file and choose your desired LLM provider.

```python
# config.py

# --- LLM PROVIDER ---
# Choose your provider: 'gemini', 'openrouter', or 'groq'.
# Groq is set by default.
LLM_PROVIDER = "groq" 
```

#### Step 2: Set API Keys in a `.env` file

1.  **Create a `.env` file** in the root directory of the project.
2.  Add the necessary API keys to the `.env` file. You only need to add keys for the services you are using.

    ```
    # .env file

    # REQUIRED for transcription
    GROQ_API_KEY="gsk_your_groq_api_key"

    # REQUIRED if using OpenRouter as the LLM provider
    OPENROUTER_API_KEY="sk-or-v1-your_openrouter_api_key"

    # REQUIRED if using Gemini as the LLM provider
    GOOGLE_API_KEY="your_google_ai_gemini_api_key"
    ```

-   **Groq API Key**: Get from the [Groq Console](https://console.groq.com/keys). (Required for transcription regardless of LLM choice).
-   **OpenRouter API Key**: Get from the [OpenRouter Keys page](https://openrouter.ai/keys).
-   **Google API Key**: Get from the [Google AI Studio](https://aistudio.google.com/app/apikey). (This is for the Gemini API, *not* Google Cloud).

#### Step 3: Configure Google Cloud Text-to-Speech

This application uses **Application Default Credentials (ADC)** to securely authenticate with Google Cloud for TTS.

1.  **Create or Select a Google Cloud Project**: Go to the [Google Cloud Console](https://console.cloud.google.com/) and ensure you have a project ready.

2.  **Enable the Text-to-Speech API**: You must enable the API for your project. You can use [this direct link to enable it](https://console.cloud.google.com/marketplace/product/google/texttospeech.googleapis.com). You may need to enable billing for your project if you haven't already.

3.  **Install the `gcloud` CLI**: If you don't have it, follow the [official installation guide](https://cloud.google.com/sdk/docs/install) for your operating system.

4.  **Authenticate Your Local Environment**: Run the following command in your terminal. This will open a browser window for you to authorize access and create a local credential file that the application will automatically find.
    ```bash
    gcloud auth application-default login
    ```

## Usage

To run the application, execute the main `app.py` script from your terminal:

```bash
python app.py
```

### How it Works

1.  Click the **Record** button to start capturing audio.
2.  Speak your query or message. The UI will show a live audio visualizer.
3.  Click **Send**.
4.  The application will:
    a. Save your recorded audio.
    b. Send the audio to Groq's Whisper API for transcription.
    c. Display your transcribed message in the chat.
    d. Send the full conversation history to your configured LLM API (Groq, OpenRouter, or Gemini).
    e. Display a "Thinking..." placeholder.
    f. Receive the LLM's text response and send it to Google Cloud's Text-to-Speech API.
    g. Save the generated MP3 audio response.
    h. Replace the "Thinking..." message with the final formatted text response.
    i. Play the audio response through your speakers.
5.  The UI resets, ready for your next interaction.

## Project Structure

The project is organized into several modules to separate concerns:

```
voice-assistant/
├── conversations/          # Stores all conversation logs and audio files
├── app.py                  # Main entry point to run the application
├── ui.py                   # Manages the Tkinter GUI and user interaction flow
├── assistant.py            # Core application logic, orchestrating calls to other modules
├── llm_api.py              # Abstraction layer for multiple LLM providers (Groq, OpenRouter, Gemini)
├── audio.py                # Handles audio recording via sounddevice
├── audio_player.py         # Handles audio playback via pygame
├── groq_api.py             # Manages API calls to Groq for transcription (Whisper)
├── google_cloud_api.py     # Manages API calls to Google Cloud for Text-to-Speech
├── utils.py                # Helper functions for text parsing and cleaning
├── config.py               # Application configuration (models, provider choices, etc.)
├── requirements.txt        # Project dependencies
├── README.md               # This file
└── .env                    # Stores your API keys (not version controlled)
```