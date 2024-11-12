from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os
import sys
import json

def main():
    # Load environment variables
    load_dotenv()
    
    try:
        # Check if name argument is provided
        if len(sys.argv) < 2:
            raise ValueError("Name argument is required")
        
        name = sys.argv[1]
        print(f"Generating greeting for name: {name}")
        
        # Get static text and replace {name} placeholder
        static_text = os.getenv('STATIC_TEXT')
        if not static_text:
            raise ValueError("STATIC_TEXT environment variable is not set")
            
        # Ensure static_text is properly decoded as UTF-8
        if isinstance(static_text, bytes):
            static_text = static_text.decode('utf-8')
            
        personalized_text = static_text.replace('{name}', name)
        
        # Print using UTF-8 encoding
        print("Personalized text:", personalized_text.encode('utf-8').decode('utf-8'))
        
        # Get API key
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
            
        # Initialize client
        client = ElevenLabs(api_key=api_key)
        
        # Get voice name and model
        voice_name = os.getenv('ELEVENLABS_VOICE_NAME')
        model = os.getenv('ELEVENLABS_MODEL')
        if not voice_name or not model:
            raise ValueError("ELEVENLABS_VOICE_NAME or ELEVENLABS_MODEL environment variable is not set")
        
        print("Generating audio...")
        
        # Generate audio
        audio_generator = client.generate(
            text=personalized_text,
            voice=voice_name,
            model=model
        )
        
        # Convert generator to bytes
        audio_bytes = b"".join(chunk for chunk in audio_generator)
        
        # Ensure assets directory exists
        os.makedirs('assets', exist_ok=True)
        
        # Write audio bytes to file using os.path.join for cross-platform compatibility
        temp_filename = os.path.join('assets', 'audio.mp3')
        with open(temp_filename, 'wb') as f:
            f.write(audio_bytes)
        
        print("Audio generated successfully and saved to", temp_filename)
        return True
        
    except Exception as e:
        error_msg = {
            "error": str(e),
            "type": type(e).__name__
        }
        # Ensure error message is JSON serializable and UTF-8 encoded
        print(json.dumps(error_msg, ensure_ascii=False).encode('utf-8').decode('utf-8'), file=sys.stderr)
        return False

if __name__ == "__main__":
    # Set UTF-8 encoding for stdout and stderr
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
    
    success = main()
    sys.exit(0 if success else 1)
