"""
Model utilities for the Flask server component.
This module provides functions for working with Hugging Face models,
including speech-to-text conversion and text generation.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from typing import Dict, Any, Optional, List

from src.config.config import (
    GEMMA_MODEL_ID,
    SPEECH_TO_TEXT_MODEL,
    MAX_NEW_TOKENS
)

class ModelManager:
    """
    Manager class for handling Hugging Face models.
    """
    
    def __init__(self):
        """Initialize the model manager."""
        self.text_model = None
        self.text_tokenizer = None
        self.speech_to_text = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all required models."""
        # Initialize text generation model (Gemma 3n)
        try:
            self.text_tokenizer = AutoTokenizer.from_pretrained(GEMMA_MODEL_ID)
            self.text_model = AutoModelForCausalLM.from_pretrained(
                GEMMA_MODEL_ID,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        except Exception as e:
            print(f"Error loading text model: {str(e)}")
            # Fallback to a simpler model if Gemma fails to load
            try:
                self.text_tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b")
                self.text_model = AutoModelForCausalLM.from_pretrained(
                    "google/gemma-2b",
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
            except Exception as e:
                print(f"Error loading fallback text model: {str(e)}")
                # Set to None if both fail
                self.text_model = None
                self.text_tokenizer = None
        
        # Initialize speech-to-text model
        try:
            self.speech_to_text = pipeline(
                "automatic-speech-recognition",
                model=SPEECH_TO_TEXT_MODEL
            )
        except Exception as e:
            print(f"Error loading speech-to-text model: {str(e)}")
            self.speech_to_text = None
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Audio data in bytes
            
        Returns:
            Transcribed text
        """
        if self.speech_to_text is None:
            return "Speech-to-text model not available."
        
        try:
            result = self.speech_to_text(audio_data)
            return result["text"]
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return "Error transcribing audio."
    
    def generate_response(self, text: str) -> str:
        """
        Generate a response to the given text.
        
        Args:
            text: Input text to respond to
            
        Returns:
            Generated response text
        """
        if self.text_model is None or self.text_tokenizer is None:
            return "Text generation model not available."
        
        try:
            # Format the input for the model
            prompt = f"User: {text}\nAssistant:"
            
            # Tokenize the input
            inputs = self.text_tokenizer(prompt, return_tensors="pt").to(self.text_model.device)
            
            # Generate a response
            with torch.no_grad():
                outputs = self.text_model.generate(
                    **inputs,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
            
            # Decode the response
            response = self.text_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the assistant's response
            assistant_response = response.split("Assistant:")[-1].strip()
            
            return assistant_response
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "Error generating response."

# Create a singleton instance
model_manager = ModelManager()