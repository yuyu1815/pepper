"""
Unit tests for the Flask server component.
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

from src.flask_server.flask_server import app
from src.flask_server.model_utils import ModelManager

class TestFlaskServer(unittest.TestCase):
    """Test cases for the Flask server."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create a temporary test audio file
        self.test_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        with open(self.test_audio_file.name, 'wb') as f:
            # Write some dummy audio data
            f.write(b'DUMMY_AUDIO_DATA')
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary test file
        if os.path.exists(self.test_audio_file.name):
            os.unlink(self.test_audio_file.name)
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    @patch('src.flask_server.model_utils.model_manager.transcribe_audio')
    @patch('src.flask_server.model_utils.model_manager.generate_response')
    def test_process_audio(self, mock_generate_response, mock_transcribe_audio):
        """Test the audio processing endpoint."""
        # Mock the model responses
        mock_transcribe_audio.return_value = "こんにちは、Pepper"
        mock_generate_response.return_value = "こんにちは、ご用件は何でしょうか？"
        
        # Open the test audio file
        with open(self.test_audio_file.name, 'rb') as audio_file:
            # Send a POST request with the audio file
            response = self.app.post(
                '/api/audio',
                data={'audio': (audio_file, 'test_audio.wav')}
            )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['transcribed_text'], "こんにちは、Pepper")
        self.assertEqual(data['response_text'], "こんにちは、ご用件は何でしょうか？")
        
        # Verify the mocks were called
        mock_transcribe_audio.assert_called_once()
        mock_generate_response.assert_called_once_with("こんにちは、Pepper")
    
    def test_process_audio_no_file(self):
        """Test the audio processing endpoint with no file."""
        response = self.app.post('/api/audio')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()