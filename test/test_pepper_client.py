"""
Unit tests for the Pepper client component.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import time

from src.pepper_client.pepper_client import PepperClient

class TestPepperClient(unittest.TestCase):
    """Test cases for the Pepper client."""
    
    @patch('src.pepper_client.pepper_client.qi.Session')
    @patch('src.pepper_client.pepper_client.build_server_url')
    def setUp(self, mock_build_server_url, mock_session):
        """Set up test environment before each test."""
        # Mock the qi Session
        self.mock_session_instance = MagicMock()
        mock_session.return_value = self.mock_session_instance
        
        # Mock the services
        self.mock_audio_service = MagicMock()
        self.mock_tts_service = MagicMock()
        
        # Configure the session mock to return our service mocks
        self.mock_session_instance.service.side_effect = lambda name: {
            'ALAudioRecorder': self.mock_audio_service,
            'ALTextToSpeech': self.mock_tts_service
        }.get(name, MagicMock())
        
        # Mock the server URL
        mock_build_server_url.return_value = "http://test-server:5000"
        
        # Create the client
        self.client = PepperClient(
            pepper_ip="test-pepper-ip",
            pepper_port=9559,
            server_host="test-server",
            server_port=5000
        )
    
    def test_connect_to_pepper(self):
        """Test connection to Pepper robot."""
        # Verify the session was connected with the correct URL
        self.mock_session_instance.connect.assert_called_once_with("tcp://test-pepper-ip:9559")
        
        # Verify the services were requested
        self.mock_session_instance.service.assert_any_call("ALAudioRecorder")
        self.mock_session_instance.service.assert_any_call("ALTextToSpeech")
        
        # Verify language was set
        self.mock_tts_service.setLanguage.assert_called_once_with("Japanese")
        
        # Verify the client is connected
        self.assertTrue(self.client.connected)
    
    def test_record_audio(self):
        """Test audio recording functionality."""
        # Mock the time.sleep to avoid waiting
        with patch('time.sleep'):
            # Call the record_audio method
            self.client.record_audio(duration=3)
            
            # Verify the recording was started and stopped
            self.mock_audio_service.startRecording.assert_called_once()
            self.mock_audio_service.stopRecording.assert_called_once()
    
    def test_speak(self):
        """Test text-to-speech functionality."""
        test_text = "こんにちは、テストです。"
        
        # Call the speak method
        result = self.client.speak(test_text)
        
        # Verify the TTS service was called with the correct text
        self.mock_tts_service.say.assert_called_once_with(test_text)
        
        # Verify the method returned success
        self.assertTrue(result)
    
    @patch('src.pepper_client.pepper_client.detect_keyword')
    @patch('src.pepper_client.pepper_client.convert_audio_to_wav')
    @patch('src.pepper_client.pepper_client.get_server_health')
    @patch('src.pepper_client.pepper_client.send_audio_to_server')
    def test_process_audio_and_respond(self, mock_send_audio, mock_get_health, 
                                      mock_convert_audio, mock_detect_keyword):
        """Test the full audio processing and response cycle."""
        # Mock the record_audio method to return dummy data
        self.client.record_audio = MagicMock(return_value=b'DUMMY_AUDIO_DATA')
        
        # Configure the mocks
        mock_convert_audio.return_value = b'CONVERTED_WAV_DATA'
        mock_detect_keyword.return_value = True  # Keyword detected
        mock_get_health.return_value = True  # Server is healthy
        mock_send_audio.return_value = (True, '{"response_text": "テスト応答です。"}')
        
        # Call the method
        result = self.client.process_audio_and_respond()
        
        # Verify the expected methods were called
        self.client.record_audio.assert_called_once()
        mock_convert_audio.assert_called_once_with(b'DUMMY_AUDIO_DATA')
        mock_detect_keyword.assert_called_once_with(b'CONVERTED_WAV_DATA')
        mock_get_health.assert_called_once_with("http://test-server:5000")
        mock_send_audio.assert_called_once()
        
        # Verify the client spoke the response
        self.mock_tts_service.say.assert_called_once_with("テスト応答です。")
        
        # Verify the method returned success
        self.assertTrue(result)
    
    @patch('src.pepper_client.pepper_client.detect_keyword')
    @patch('src.pepper_client.pepper_client.convert_audio_to_wav')
    def test_process_audio_no_keyword(self, mock_convert_audio, mock_detect_keyword):
        """Test processing when no keyword is detected."""
        # Mock the record_audio method to return dummy data
        self.client.record_audio = MagicMock(return_value=b'DUMMY_AUDIO_DATA')
        
        # Configure the mocks
        mock_convert_audio.return_value = b'CONVERTED_WAV_DATA'
        mock_detect_keyword.return_value = False  # No keyword detected
        
        # Call the method
        result = self.client.process_audio_and_respond()
        
        # Verify the expected methods were called
        self.client.record_audio.assert_called_once()
        mock_convert_audio.assert_called_once_with(b'DUMMY_AUDIO_DATA')
        mock_detect_keyword.assert_called_once_with(b'CONVERTED_WAV_DATA')
        
        # Verify the method returned failure
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()