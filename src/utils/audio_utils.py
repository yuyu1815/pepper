"""
Audio processing utilities for the Pepper Robot and Flask Server integration system.
This module provides functions for audio recording, format conversion, and keyword detection.
"""

import io
import wave
import numpy as np
from typing import Tuple, Optional, BinaryIO
import speech_recognition as sr

from src.config.config import (
    SAMPLE_RATE,
    CHANNELS,
    KEYWORD,
    KEYWORD_THRESHOLD
)

def convert_audio_to_wav(audio_data: bytes, sample_rate: int = SAMPLE_RATE, 
                         channels: int = CHANNELS) -> bytes:
    """
    Convert raw audio data to WAV format.
    
    Args:
        audio_data: Raw audio data bytes
        sample_rate: Sample rate of the audio
        channels: Number of audio channels
        
    Returns:
        WAV formatted audio data as bytes
    """
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 16-bit audio
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)
    
    return wav_buffer.getvalue()

def detect_keyword(audio_data: bytes, keyword: str = KEYWORD, 
                  threshold: float = KEYWORD_THRESHOLD) -> bool:
    """
    Detect if the specified keyword is present in the audio data.
    
    Args:
        audio_data: Audio data in WAV format
        keyword: Keyword to detect (default: 'pepper')
        threshold: Confidence threshold for detection
        
    Returns:
        True if keyword is detected, False otherwise
    """
    recognizer = sr.Recognizer()
    
    # Convert bytes to AudioData
    audio_file = io.BytesIO(audio_data)
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    
    try:
        # Use Google's speech recognition (can be replaced with a local model)
        text = recognizer.recognize_google(audio, show_all=True)
        
        # Check if any result contains the keyword
        if isinstance(text, dict) and 'alternative' in text:
            for alt in text['alternative']:
                if keyword.lower() in alt['transcript'].lower():
                    if 'confidence' in alt and alt['confidence'] >= threshold:
                        return True
                    elif 'confidence' not in alt:
                        # If no confidence score, assume it's good enough
                        return True
        
        # If text is a string (older API versions)
        elif isinstance(text, str) and keyword.lower() in text.lower():
            return True
            
    except (sr.UnknownValueError, sr.RequestError):
        # Speech not understood or API error
        pass
    
    return False

def save_audio_to_file(audio_data: bytes, filename: str) -> None:
    """
    Save audio data to a file.
    
    Args:
        audio_data: Audio data in WAV format
        filename: Path to save the audio file
    """
    with open(filename, 'wb') as f:
        f.write(audio_data)

def load_audio_from_file(filename: str) -> bytes:
    """
    Load audio data from a file.
    
    Args:
        filename: Path to the audio file
        
    Returns:
        Audio data as bytes
    """
    with open(filename, 'rb') as f:
        return f.read()