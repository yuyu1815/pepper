"""
Test script for the chat endpoint of the Flask server.
This script sends a text message to the chat endpoint and prints the response.
"""

import requests
import json
import sys
import argparse

def test_chat_endpoint(server_url, message):
    """
    Test the chat endpoint by sending a message and printing the response.
    
    Args:
        server_url: URL of the Flask server
        message: Message to send to the chat endpoint
    """
    # Build the endpoint URL
    endpoint = f"{server_url}/api/response"
    
    # Prepare the request data
    data = {"text": message}
    headers = {"Content-Type": "application/json"}
    
    try:
        # Send the request
        print(f"Sending message to {endpoint}: {message}")
        response = requests.post(endpoint, data=json.dumps(data), headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            response_data = response.json()
            
            # Print the response
            print("\nResponse:")
            print(f"Input text: {response_data.get('input_text', 'N/A')}")
            print(f"Response text: {response_data.get('response_text', 'N/A')}")
            return True
        else:
            # Print the error
            print(f"\nError: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        # Print any exceptions
        print(f"\nException: {str(e)}")
        return False

def main():
    """
    Main entry point for the script.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the chat endpoint of the Flask server")
    parser.add_argument("--server", default="http://localhost:5000",
                        help="URL of the Flask server (default: http://localhost:5000)")
    parser.add_argument("--message", default="こんにちは、Pepper",
                        help="Message to send to the chat endpoint (default: こんにちは、Pepper)")
    
    args = parser.parse_args()
    
    # Test the chat endpoint
    success = test_chat_endpoint(args.server, args.message)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()