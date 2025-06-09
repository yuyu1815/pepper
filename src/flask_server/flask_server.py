"""
Flask server for the Pepper Robot integration system.
This module sets up a Flask server that receives audio from Pepper,
converts it to text, generates a response, and sends it back.
"""

from flask import Flask, request, jsonify
import logging
import os
import tempfile

from src.config.config import (
    FLASK_HOST,
    FLASK_PORT,
    DEBUG_MODE,
    AUDIO_ENDPOINT,
    RESPONSE_ENDPOINT
)
from src.utils.audio_utils import save_audio_to_file
from src.flask_server.model_utils import model_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the server is running.

    Returns:
        JSON response indicating the server is healthy
    """
    return jsonify({"status": "healthy"})

@app.route(AUDIO_ENDPOINT, methods=['POST'])
def process_audio():
    """
    Process audio data from Pepper.

    Expects:
        - A POST request with audio data in the 'audio' field

    Returns:
        - JSON response with the generated text response
    """
    if 'audio' not in request.files:
        logger.error("No audio file in request")
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']

    # Save the audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        audio_file.save(temp_file.name)
        temp_filename = temp_file.name

    try:
        # Read the audio data
        with open(temp_filename, 'rb') as f:
            audio_data = f.read()

        # Transcribe the audio to text
        transcribed_text = model_manager.transcribe_audio(audio_data)
        logger.info(f"Transcribed text: {transcribed_text}")

        # Generate a response
        response_text = model_manager.generate_response(transcribed_text)
        logger.info(f"Generated response: {response_text}")

        # Return the response
        return jsonify({
            "transcribed_text": transcribed_text,
            "response_text": response_text
        })

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.route(RESPONSE_ENDPOINT, methods=['POST'])
def process_chat():
    """
    Process text chat input and generate a response.

    Expects:
        - A POST request with JSON data containing a 'text' field

    Returns:
        - JSON response with the generated text response
    """
    # Check if the request contains JSON data
    if not request.is_json:
        logger.error("Request does not contain JSON data")
        return jsonify({"error": "Request must be JSON"}), 400

    # Get the text from the request
    data = request.get_json()
    if 'text' not in data:
        logger.error("No text field in request JSON")
        return jsonify({"error": "No text provided"}), 400

    input_text = data['text']
    logger.info(f"Received chat input: {input_text}")

    try:
        # Generate a response
        response_text = model_manager.generate_response(input_text)
        logger.info(f"Generated response: {response_text}")

        # Return the response
        return jsonify({
            "input_text": input_text,
            "response_text": response_text
        })

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

def run_server():
    """
    Run the Flask server.
    """
    logger.info(f"Starting Flask server on {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG_MODE)

if __name__ == '__main__':
    run_server()
