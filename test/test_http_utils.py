"""
Unit tests for the HTTP utilities.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.utils.http_utils import (
    send_audio_to_server,
    get_server_health,
    build_server_url
)

class TestHttpUtils(unittest.TestCase):
    """Test cases for the HTTP utilities."""
    
    def test_build_server_url(self):
        """Test building server URL from host and port."""
        # Test with localhost
        url = build_server_url('localhost', 5000)
        self.assertEqual(url, 'http://localhost:5000')
        
        # Test with IP address
        url = build_server_url('192.168.1.100', 8080)
        self.assertEqual(url, 'http://192.168.1.100:8080')
        
        # Test with domain name
        url = build_server_url('example.com', 443)
        self.assertEqual(url, 'http://example.com:443')
    
    @patch('requests.get')
    def test_get_server_health_success(self, mock_get):
        """Test server health check when server is healthy."""
        # Configure the mock to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test the health check
        result = get_server_health('http://test-server:5000')
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with('http://test-server:5000/health')
    
    @patch('requests.get')
    def test_get_server_health_failure(self, mock_get):
        """Test server health check when server is not healthy."""
        # Configure the mock to return a failed response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        # Test the health check
        result = get_server_health('http://test-server:5000')
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with('http://test-server:5000/health')
    
    @patch('requests.get')
    def test_get_server_health_exception(self, mock_get):
        """Test server health check when request throws an exception."""
        # Configure the mock to raise an exception
        mock_get.side_effect = Exception('Connection error')
        
        # Test the health check
        result = get_server_health('http://test-server:5000')
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify the request was attempted
        mock_get.assert_called_once_with('http://test-server:5000/health')
    
    @patch('requests.post')
    def test_send_audio_to_server_success(self, mock_post):
        """Test sending audio to server when successful."""
        # Configure the mock to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"response_text": "テスト応答です。"}'
        mock_post.return_value = mock_response
        
        # Test data
        server_url = 'http://test-server:5000'
        endpoint = '/api/audio'
        audio_data = b'DUMMY_AUDIO_DATA'
        
        # Send the audio
        success, response = send_audio_to_server(server_url, endpoint, audio_data)
        
        # Verify the result
        self.assertTrue(success)
        self.assertEqual(response, '{"response_text": "テスト応答です。"}')
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], 'http://test-server:5000/api/audio')
        self.assertIn('files', kwargs)
        self.assertIn('audio', kwargs['files'])
    
    @patch('requests.post')
    def test_send_audio_to_server_failure(self, mock_post):
        """Test sending audio to server when server returns an error."""
        # Configure the mock to return a failed response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response
        
        # Test data
        server_url = 'http://test-server:5000'
        endpoint = '/api/audio'
        audio_data = b'DUMMY_AUDIO_DATA'
        
        # Send the audio
        success, response = send_audio_to_server(server_url, endpoint, audio_data)
        
        # Verify the result
        self.assertFalse(success)
        self.assertIsNone(response)
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_audio_to_server_exception(self, mock_post):
        """Test sending audio to server when request throws an exception."""
        # Configure the mock to raise an exception
        mock_post.side_effect = Exception('Connection error')
        
        # Test data
        server_url = 'http://test-server:5000'
        endpoint = '/api/audio'
        audio_data = b'DUMMY_AUDIO_DATA'
        
        # Send the audio
        success, response = send_audio_to_server(server_url, endpoint, audio_data)
        
        # Verify the result
        self.assertFalse(success)
        self.assertIsNone(response)
        
        # Verify the request was attempted
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()