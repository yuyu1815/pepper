"""
Unit tests for the audio utilities.
"""

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock

from src.utils.audio_utils import (
    convert_audio_to_wav,
    detect_keyword,
    save_audio_to_file,
    load_audio_from_file
)

class TestAudioUtils(unittest.TestCase):
    """Test cases for the audio utilities."""
    
    def setUp(self):
        """Set up test environment before each test."""
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
    
    def test_convert_audio_to_wav(self):
        """Test conversion of raw audio data to WAV format."""
        # Test with dummy audio data
        raw_audio = b'DUMMY_AUDIO_DATA'
        
        # Convert to WAV
        wav_audio = convert_audio_to_wav(raw_audio)
        
        # Verify the result is bytes and not empty
        self.assertIsInstance(wav_audio, bytes)
        self.assertTrue(len(wav_audio) > 0)
        
        # Verify the WAV header
        self.assertTrue(wav_audio.startswith(b'RIFF'))
        self.assertIn(b'WAVE', wav_audio[:12])
    
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.AudioFile')
    def test_detect_keyword_found(self, mock_audio_file, mock_recognizer_class):
        """Test keyword detection when keyword is found."""
        # Set up mocks
        mock_recognizer = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer
        
        # Configure the recognizer to return a result with the keyword
        mock_recognizer.recognize_google.return_value = {
            'alternative': [
                {'transcript': 'hey pepper how are you', 'confidence': 0.9}
            ]
        }
        
        # Test with dummy audio data
        result = detect_keyword(b'DUMMY_AUDIO_DATA', keyword='pepper')
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the recognizer was called
        mock_recognizer.recognize_google.assert_called_once()
    
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.AudioFile')
    def test_detect_keyword_not_found(self, mock_audio_file, mock_recognizer_class):
        """Test keyword detection when keyword is not found."""
        # Set up mocks
        mock_recognizer = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer
        
        # Configure the recognizer to return a result without the keyword
        mock_recognizer.recognize_google.return_value = {
            'alternative': [
                {'transcript': 'hello how are you', 'confidence': 0.9}
            ]
        }
        
        # Test with dummy audio data
        result = detect_keyword(b'DUMMY_AUDIO_DATA', keyword='pepper')
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify the recognizer was called
        mock_recognizer.recognize_google.assert_called_once()
    
    def test_save_and_load_audio_file(self):
        """Test saving and loading audio files."""
        # Test data
        test_data = b'TEST_AUDIO_DATA'
        test_filename = os.path.join(tempfile.gettempdir(), 'test_audio.wav')
        
        try:
            # Save the audio data
            save_audio_to_file(test_data, test_filename)
            
            # Verify the file exists
            self.assertTrue(os.path.exists(test_filename))
            
            # Load the audio data
            loaded_data = load_audio_from_file(test_filename)
            
            # Verify the loaded data matches the original
            self.assertEqual(loaded_data, test_data)
            
        finally:
            # Clean up
            if os.path.exists(test_filename):
                os.unlink(test_filename)

if __name__ == '__main__':
    unittest.main()