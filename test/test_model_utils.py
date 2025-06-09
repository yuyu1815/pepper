"""
Unit tests for the model utilities.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.flask_server.model_utils import ModelManager

class TestModelUtils(unittest.TestCase):
    """Test cases for the model utilities."""
    
    @patch('src.flask_server.model_utils.AutoTokenizer')
    @patch('src.flask_server.model_utils.AutoModelForCausalLM')
    @patch('src.flask_server.model_utils.pipeline')
    def setUp(self, mock_pipeline, mock_auto_model, mock_auto_tokenizer):
        """Set up test environment before each test."""
        # Mock the tokenizer
        self.mock_tokenizer = MagicMock()
        mock_auto_tokenizer.from_pretrained.return_value = self.mock_tokenizer
        
        # Mock the model
        self.mock_model = MagicMock()
        self.mock_model.device = 'cpu'
        mock_auto_model.from_pretrained.return_value = self.mock_model
        
        # Mock the pipeline
        self.mock_speech_to_text = MagicMock()
        mock_pipeline.return_value = self.mock_speech_to_text
        
        # Create the model manager
        self.model_manager = ModelManager()
    
    def test_initialization(self):
        """Test model manager initialization."""
        # Verify the models were initialized
        self.assertIsNotNone(self.model_manager.text_model)
        self.assertIsNotNone(self.model_manager.text_tokenizer)
        self.assertIsNotNone(self.model_manager.speech_to_text)
    
    def test_transcribe_audio(self):
        """Test audio transcription."""
        # Configure the mock
        self.mock_speech_to_text.return_value = {"text": "こんにちは、Pepper"}
        
        # Test with dummy audio data
        result = self.model_manager.transcribe_audio(b'DUMMY_AUDIO_DATA')
        
        # Verify the result
        self.assertEqual(result, "こんにちは、Pepper")
        
        # Verify the speech-to-text model was called
        self.mock_speech_to_text.assert_called_once_with(b'DUMMY_AUDIO_DATA')
    
    def test_transcribe_audio_error(self):
        """Test audio transcription when an error occurs."""
        # Configure the mock to raise an exception
        self.mock_speech_to_text.side_effect = Exception("Transcription error")
        
        # Test with dummy audio data
        result = self.model_manager.transcribe_audio(b'DUMMY_AUDIO_DATA')
        
        # Verify the result is an error message
        self.assertEqual(result, "Error transcribing audio.")
    
    def test_generate_response(self):
        """Test response generation."""
        # Configure the mocks
        self.mock_tokenizer.return_value = {"input_ids": MagicMock(), "attention_mask": MagicMock()}
        self.mock_tokenizer.__call__ = MagicMock(return_value=MagicMock())
        self.mock_model.generate.return_value = [MagicMock()]
        self.mock_tokenizer.decode.return_value = "User: こんにちは\nAssistant: こんにちは、ご用件は何でしょうか？"
        
        # Test with input text
        result = self.model_manager.generate_response("こんにちは")
        
        # Verify the result
        self.assertEqual(result, "こんにちは、ご用件は何でしょうか？")
        
        # Verify the model was called
        self.mock_model.generate.assert_called_once()
        self.mock_tokenizer.decode.assert_called_once()
    
    def test_generate_response_error(self):
        """Test response generation when an error occurs."""
        # Configure the mock to raise an exception
        self.mock_tokenizer.__call__ = MagicMock(side_effect=Exception("Generation error"))
        
        # Test with input text
        result = self.model_manager.generate_response("こんにちは")
        
        # Verify the result is an error message
        self.assertEqual(result, "Error generating response.")
    
    @patch('src.flask_server.model_utils.AutoTokenizer')
    @patch('src.flask_server.model_utils.AutoModelForCausalLM')
    @patch('src.flask_server.model_utils.pipeline')
    def test_initialization_fallback(self, mock_pipeline, mock_auto_model, mock_auto_tokenizer):
        """Test model manager initialization with fallback."""
        # First attempt fails, second succeeds
        mock_auto_tokenizer.from_pretrained.side_effect = [Exception("Model not found"), MagicMock()]
        mock_auto_model.from_pretrained.side_effect = [Exception("Model not found"), MagicMock()]
        
        # Create the model manager
        model_manager = ModelManager()
        
        # Verify the fallback model was loaded
        self.assertEqual(mock_auto_tokenizer.from_pretrained.call_count, 2)
        self.assertEqual(mock_auto_model.from_pretrained.call_count, 2)
        
        # Verify the second call was with the fallback model
        args, _ = mock_auto_tokenizer.from_pretrained.call_args_list[1]
        self.assertEqual(args[0], "google/gemma-2b")

if __name__ == '__main__':
    unittest.main()