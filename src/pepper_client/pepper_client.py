"""
Pepper client for the Flask Server integration system.
This module handles the client-side operations on the Pepper robot,
including audio recording, keyword detection, sending audio to the server,
and text-to-speech functionality for responses.
"""

import sys
import time
import logging
import argparse
from typing import Optional

# Import Pepper-related libraries (using a try-except block since these might not be available in all environments)
try:
    import qi
except ImportError:
    print("Warning: qi module not found. This is expected if not running on Pepper.")
    # Create a mock qi module for development/testing
    class MockQi:
        class Session:
            def __init__(self):
                self.services = {}
            
            def connect(self, url):
                print(f"Mock connecting to {url}")
                return True
            
            def service(self, name):
                print(f"Mock getting service {name}")
                if name not in self.services:
                    self.services[name] = type(name, (), {
                        "say": lambda self, text: print(f"Pepper says: {text}"),
                        "setLanguage": lambda self, lang: print(f"Setting language to {lang}"),
                        "startRecording": lambda self, path: print(f"Started recording to {path}"),
                        "stopRecording": lambda self: print("Stopped recording"),
                        "getOutputVolume": lambda self: 50,
                        "setOutputVolume": lambda self, vol: print(f"Setting volume to {vol}")
                    })()
                return self.services[name]
    
    qi = MockQi()

from src.config.config import (
    DEFAULT_PEPPER_IP,
    PEPPER_PORT,
    RECORDING_SECONDS,
    AUDIO_FORMAT,
    FLASK_HOST,
    FLASK_PORT,
    AUDIO_ENDPOINT
)
from src.utils.audio_utils import convert_audio_to_wav, detect_keyword, save_audio_to_file
from src.utils.http_utils import build_server_url, send_audio_to_server, get_server_health

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PepperClient:
    """
    Client for interacting with Pepper robot and Flask server.
    """
    
    def __init__(self, pepper_ip: str = DEFAULT_PEPPER_IP, pepper_port: int = PEPPER_PORT,
                 server_host: str = FLASK_HOST, server_port: int = FLASK_PORT):
        """
        Initialize the Pepper client.
        
        Args:
            pepper_ip: IP address of the Pepper robot
            pepper_port: Port number for the Pepper robot
            server_host: Host of the Flask server
            server_port: Port of the Flask server
        """
        self.pepper_ip = pepper_ip
        self.pepper_port = pepper_port
        self.server_url = build_server_url(server_host, server_port)
        
        # Initialize Pepper connection
        self.session = qi.Session()
        self.connected = False
        self.audio_service = None
        self.tts_service = None
        
        # Connect to Pepper
        self._connect_to_pepper()
    
    def _connect_to_pepper(self) -> bool:
        """
        Connect to the Pepper robot.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            pepper_url = f"tcp://{self.pepper_ip}:{self.pepper_port}"
            logger.info(f"Connecting to Pepper at {pepper_url}")
            
            self.session.connect(pepper_url)
            self.connected = True
            
            # Get required services
            self.audio_service = self.session.service("ALAudioRecorder")
            self.tts_service = self.session.service("ALTextToSpeech")
            
            # Set language to Japanese
            self.tts_service.setLanguage("Japanese")
            
            logger.info("Successfully connected to Pepper")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Pepper: {str(e)}")
            self.connected = False
            return False
    
    def record_audio(self, duration: int = RECORDING_SECONDS) -> Optional[bytes]:
        """
        Record audio from Pepper's microphone.
        
        Args:
            duration: Duration of recording in seconds
            
        Returns:
            Recorded audio data as bytes, or None if recording failed
        """
        if not self.connected or not self.audio_service:
            logger.error("Cannot record audio: Not connected to Pepper")
            return None
        
        try:
            # Define the path where Pepper will save the recording
            recording_path = f"/home/nao/recordings/audio_{int(time.time())}.{AUDIO_FORMAT}"
            
            # Start recording
            logger.info(f"Starting audio recording for {duration} seconds")
            self.audio_service.startRecording(recording_path)
            
            # Wait for the specified duration
            time.sleep(duration)
            
            # Stop recording
            self.audio_service.stopRecording()
            logger.info("Audio recording completed")
            
            # Read the recorded file from Pepper
            # Note: In a real implementation, you would need to transfer the file from Pepper
            # For this example, we'll simulate it with a local file
            try:
                with open(recording_path, 'rb') as f:
                    audio_data = f.read()
                return audio_data
            except FileNotFoundError:
                # For development/testing when not on actual Pepper
                logger.warning("Simulating audio recording (not on actual Pepper)")
                # Return some dummy audio data
                return b'DUMMY_AUDIO_DATA'
                
        except Exception as e:
            logger.error(f"Error recording audio: {str(e)}")
            return None
    
    def speak(self, text: str) -> bool:
        """
        Make Pepper speak the given text.
        
        Args:
            text: Text for Pepper to speak
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.tts_service:
            logger.error("Cannot speak: Not connected to Pepper")
            return False
        
        try:
            logger.info(f"Pepper speaking: {text}")
            self.tts_service.say(text)
            return True
        except Exception as e:
            logger.error(f"Error making Pepper speak: {str(e)}")
            return False
    
    def process_audio_and_respond(self) -> bool:
        """
        Record audio, check for keyword, send to server if keyword detected,
        and speak the response.
        
        Returns:
            True if the full process was successful, False otherwise
        """
        # Record audio
        audio_data = self.record_audio()
        if not audio_data:
            logger.error("Failed to record audio")
            return False
        
        # Convert audio to WAV format
        wav_audio = convert_audio_to_wav(audio_data)
        
        # Check if the keyword is detected
        if not detect_keyword(wav_audio):
            logger.info("Keyword 'pepper' not detected in audio")
            return False
        
        logger.info("Keyword 'pepper' detected, sending audio to server")
        
        # Check if server is healthy
        if not get_server_health(self.server_url):
            logger.error("Server is not healthy")
            self.speak("サーバーに接続できません。")
            return False
        
        # Send audio to server
        success, response = send_audio_to_server(self.server_url, AUDIO_ENDPOINT, wav_audio)
        
        if not success or not response:
            logger.error("Failed to get response from server")
            self.speak("サーバーからの応答がありません。")
            return False
        
        try:
            # Parse the response
            import json
            response_data = json.loads(response)
            response_text = response_data.get("response_text", "応答がありません。")
            
            # Speak the response
            self.speak(response_text)
            return True
            
        except Exception as e:
            logger.error(f"Error processing server response: {str(e)}")
            self.speak("応答の処理中にエラーが発生しました。")
            return False
    
    def run(self, continuous: bool = True, interval: float = 1.0):
        """
        Run the Pepper client in a loop, continuously processing audio and responding.
        
        Args:
            continuous: Whether to run continuously or just once
            interval: Time interval between processing cycles in seconds
        """
        if not self.connected:
            logger.error("Cannot run: Not connected to Pepper")
            return
        
        try:
            if continuous:
                logger.info(f"Running continuously with interval {interval} seconds")
                self.speak("準備ができました。「pepper」と呼びかけてください。")
                
                while True:
                    self.process_audio_and_respond()
                    time.sleep(interval)
            else:
                logger.info("Running once")
                self.speak("準備ができました。「pepper」と呼びかけてください。")
                self.process_audio_and_respond()
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping")
            self.speak("終了します。")
        except Exception as e:
            logger.error(f"Error in run loop: {str(e)}")
            self.speak("エラーが発生しました。")

def main():
    """
    Main entry point for the Pepper client.
    """
    parser = argparse.ArgumentParser(description="Pepper client for Flask server integration")
    parser.add_argument("pepper_ip", nargs="?", default=DEFAULT_PEPPER_IP,
                        help=f"IP address of the Pepper robot (default: {DEFAULT_PEPPER_IP})")
    parser.add_argument("--port", type=int, default=PEPPER_PORT,
                        help=f"Port number for the Pepper robot (default: {PEPPER_PORT})")
    parser.add_argument("--server-host", default=FLASK_HOST,
                        help=f"Host of the Flask server (default: {FLASK_HOST})")
    parser.add_argument("--server-port", type=int, default=FLASK_PORT,
                        help=f"Port of the Flask server (default: {FLASK_PORT})")
    parser.add_argument("--once", action="store_true",
                        help="Run only once instead of continuously")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Time interval between processing cycles in seconds (default: 1.0)")
    
    args = parser.parse_args()
    
    client = PepperClient(
        pepper_ip=args.pepper_ip,
        pepper_port=args.port,
        server_host=args.server_host,
        server_port=args.server_port
    )
    
    client.run(continuous=not args.once, interval=args.interval)

if __name__ == "__main__":
    main()