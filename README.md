# Groq Voice Assistant

A modular desktop application that records audio, transcribes it, gets a response from an LLM, and speaks the response back to you.

## Features

- **Full Voice Interaction Loop**: Speak, get a transcribed text, receive an LLM response, and hear it spoken aloud.
- **Modular Architecture**: Code is separated into UI, Audio Recording, Audio Playback, Groq API, and Google Cloud API modules.
- **Powered by Best-in-Class APIs**:
  - **Groq**: For ultra-fast Speech-to-Text (`whisper-large-v3`) and LLM inference.
  - **Google Cloud**: For high-quality, natural-sounding Text-to-Speech.
- **Real-time Audio Visualization**: Confirms microphone input during recording.

## Setup

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

- Python 3.7+
- A microphone and speakers.
- A Groq Account and API Key.
- A Google Cloud Account.

### 2. Groq Setup

1.  **Get a Groq API Key** from the [Groq Console](https://console.groq.com/keys).
2.  **Configure your API Key**: Create a file named `.env` in the project root and add your key:
    ```
    GROQ_API_KEY="gsk_your_api_key_here"
    ```

### 3. Google Cloud Setup (for Text-to-Speech)

1.  **Create/Select a Google Cloud Project** in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Enable the Text-to-Speech API** for your project. You can use [this direct link](https://console.cloud.google.com/flows/enableapi?apiid=texttospeech.googleapis.com). You may need to enable billing.
3.  **Install the `gcloud` CLI**: Follow the [official installation guide](https://cloud.google.com/sdk/docs/install) for your OS.
4.  **Authenticate your Environment**: Run the following command in your terminal. This allows the application to use your credentials securely without needing extra API keys.
    ```bash
    gcloud auth application-default login
    ```

### 4. Application Installation

1.  **Clone or download the project.**
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the main `app.py` script from your terminal:

```bash
python app.py