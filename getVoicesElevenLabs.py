import requests
import json
from dotenv import load_dotenv
import os

def get_voices():
    """
    Fetch all available voices from ElevenLabs API
    Returns a list of voice objects
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # API endpoint for voices
    url = "https://api.elevenlabs.io/v1/voices"
    
    # Get API key from environment variable
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found in .env file")
        print("Please create a .env file with your API key like this:")
        print("ELEVENLABS_API_KEY=your-api-key-here")
        return None
    
    # Headers for authentication
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        # Make the GET request
        print("Making request to ElevenLabs API...")
        response = requests.get(url, headers=headers)
        
        # Print status code for debugging
        print(f"Response status code: {response.status_code}")
        
        # Check if the request was successful
        if response.status_code == 200:
            voices = response.json()
            return voices
        else:
            print(f"Error: API request failed with status code {response.status_code}")
            print("Response content:", response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {str(e)}")
        print("Raw response:", response.text)
        return None

if __name__ == "__main__":
    print("Starting voice fetch...")
    voices = get_voices()
    
    if voices:
        print("\nSuccessfully retrieved voices:")
        print(json.dumps(voices, indent=2))
        print(f"\nTotal voices found: {len(voices.get('voices', []))}")
    else:
        print("\nFailed to retrieve voices. Please check the errors above.")
