"""
HTTP utilities for the Pepper Robot and Flask Server integration system.
This module provides functions for making HTTP requests and handling responses.
"""

import requests
from typing import Dict, Any, Optional, Union, Tuple
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_audio_to_server(server_url: str, endpoint: str, audio_data: bytes) -> Tuple[bool, Optional[str]]:
    """
    Send audio data to the Flask server.
    
    Args:
        server_url: Base URL of the Flask server
        endpoint: API endpoint to send the audio to
        audio_data: Audio data in WAV format
        
    Returns:
        Tuple of (success, response_text)
        - success: Boolean indicating if the request was successful
        - response_text: Response text from the server if successful, None otherwise
    """
    url = f"{server_url}{endpoint}"
    
    try:
        files = {'audio': ('audio.wav', audio_data, 'audio/wav')}
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            return True, response.text
        else:
            logger.error(f"Server returned error: {response.status_code} - {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return False, None

def get_server_health(server_url: str) -> bool:
    """
    Check if the Flask server is running and healthy.
    
    Args:
        server_url: Base URL of the Flask server
        
    Returns:
        Boolean indicating if the server is healthy
    """
    try:
        response = requests.get(f"{server_url}/health")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def build_server_url(host: str, port: int) -> str:
    """
    Build the server URL from host and port.
    
    Args:
        host: Server hostname or IP address
        port: Server port number
        
    Returns:
        Complete server URL
    """
    return f"http://{host}:{port}"