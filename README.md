# Groq Voice Assistant w/Google Cloud TTS

A modular desktop application that records audio, transcribes it, gets a response from a Large Language Model (LLM), and speaks the response back to you. All conversations are automatically saved for later review and analysis.

## Features

-   **Full Voice Interaction Loop**: Speak, get a transcribed text, receive an LLM response, and hear it spoken aloud in a natural voice.
-   **Automatic Conversation Logging**: Each time the app starts, a new unique folder is created in the `conversations/` directory. This folder stores:
    -   User's input audio as `user_X.wav`.
    -   The assistant's spoken response as `assistant_X.mp3`.
    -   The full conversation history with the LLM as `chat_history.json`.
-   **Modular Architecture**: The code is cleanly separated into modules for the User Interface (`ui.py`), Audio Recording (`audio.py`), Audio Playback (`audio_player.py`), Groq API interactions (`groq_api.py`), and Google Cloud API interactions (`google_cloud_api.py`).
-   **Powered by Best-in-Class APIs**:
    -   **Groq**: For ultra-fast Speech-to-Text (`whisper-large-v3`) and LLM inference.
    -   **Google Cloud**: For high-quality, natural-sounding Text-to-Speech.
-   **Real-time Audio Visualization**: A simple waveform display confirms that the microphone is capturing audio during recording.

## Setup

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

-   Python 3.7+
-   A working microphone and speakers/headphones.
-   A Groq Cloud account and API Key.
-   A Google Cloud account.

### 2. Installation

1.  **Clone or download the project:**
    Unzip or clone this repository into a local directory.

2.  **Create a virtual environment (recommended):**
    Open a terminal in the project's root directory and run:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

You must configure access for both Groq and Google Cloud APIs.

#### Groq API Setup

1.  **Get a Groq API Key** from the [Groq Console](https://console.groq.com/keys).
2.  **Create a `.env` file** in the root directory of the project.
3.  Add your API key to the `.env` file in the following format:
    ```
    GROQ_API_KEY="gsk_your_api_key_here"
    ```

#### Google Cloud Text-to-Speech Setup

This application uses **Application Default Credentials (ADC)** to securely authenticate with Google Cloud, which is the recommended method for local development.

1.  **Create or Select a Google Cloud Project**: Go to the [Google Cloud Console](https://console.cloud.google.com/) and ensure you have a project ready. For this example, we'll assume your Project ID is `voice-chatbot-1234`.

2.  **Enable the Text-to-Speech API**: You must enable the API for your project. You can use [this direct link to enable it](https://console.cloud.google.com/marketplace/product/google/texttospeech.googleapis.com). You may need to enable billing for your project if you haven't already.

3.  **Install the `gcloud` CLI**: If you don't have it, follow the [official installation guide](https://cloud.google.com/sdk/docs/install) for your operating system.

4.  **Authenticate Your Local Environment**: This is the most important step. Run the following two commands in your terminal:

    *   First, log in with your Google account. This will open a browser window for you to authorize access. This command creates a local credential file that the application will automatically find.
        ```bash
        gcloud auth application-default login
        ```

    *   Next, set your project as the default for the `gcloud` CLI. This tells Google Cloud which project should be billed and used for API calls. **Replace `voice-chatbot-476822` with your actual Project ID.**
        ```bash
        gcloud config set project voice-chatbot-476822
        ```

After completing these steps, your application is fully configured to use the Google Cloud TTS API without needing any extra key files.

## Usage

To run the application, execute the main `app.py` script from your terminal:

```bash
python app.py
```

### How it Works

1.  Click the **Record** button to start capturing audio.
2.  The UI will show **Cancel** and **Send** buttons, along with a live audio visualizer.
3.  Speak your query or message in Spanish.
4.  Click **Send**.
5.  The application will:
    a. Save your recorded audio to the current session folder.
    b. Send the audio to Groq's Whisper API for transcription.
    c. Display your transcribed message in the chat.
    d. Send the full conversation history to the Groq LLM API.
    e. Display a "Thinking..." placeholder.
    f. Send the LLM's text response to Google Cloud's Text-to-Speech API.
    g. Save the generated audio response to the session folder.
    h. Replace the "Thinking..." message with the final text response.
    i. Play the audio response through your speakers.
6.  The UI resets, ready for your next interaction.

## Project Structure

The project is organized into several modules to separate concerns:

```
groq-voice-assistant/
├── conversations/          # Stores all conversation logs and audio files
├── app.py                  # Main entry point to run the application
├── ui.py                   # Manages the Tkinter GUI and application flow
├── audio.py                # Handles audio recording via sounddevice
├── audio_player.py         # Handles audio playback via pygame
├── groq_api.py             # Manages all API calls to Groq (STT and LLM)
├── google_cloud_api.py     # Manages all API calls to Google Cloud (TTS)
├── requirements.txt        # Project dependencies
├── README.md               # This file
└── .env                    # Stores your Groq API key (not version controlled)
```