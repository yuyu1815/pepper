"""
Configuration settings for the Pepper Robot and Flask Server integration system.
This file contains all the necessary configuration parameters for both the
Pepper client and Flask server components.
"""

# Flask Server Configuration
FLASK_HOST = '0.0.0.0'  # Listen on all available interfaces
FLASK_PORT = 5000
DEBUG_MODE = True

# API Endpoints
AUDIO_ENDPOINT = '/api/audio'
RESPONSE_ENDPOINT = '/api/response'

# Pepper Robot Configuration
DEFAULT_PEPPER_IP = '127.0.0.1'  # Default to localhost, should be overridden when running
PEPPER_PORT = 9559  # Default port for NAOqi

# Audio Recording Configuration
AUDIO_FORMAT = 'wav'
RECORDING_SECONDS = 5  # Duration of each recording in seconds
SAMPLE_RATE = 16000  # Sample rate for audio recording
CHANNELS = 1  # Mono audio

# Keyword Detection
KEYWORD = 'pepper'
KEYWORD_THRESHOLD = 0.5  # Confidence threshold for keyword detection

# Hugging Face Model Configuration
GEMMA_MODEL_ID = "google/gemma-3n"  # Model ID for Gemma 3n
SPEECH_TO_TEXT_MODEL = "openai/whisper-base"  # Example model for speech-to-text
MAX_NEW_TOKENS = 100  # Maximum number of tokens to generate in response