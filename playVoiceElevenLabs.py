from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os
import pygame
import time

# Load environment variables
load_dotenv()

try:
    # Initialize pygame mixer
    pygame.mixer.init()
    
    client = ElevenLabs(
        api_key=os.getenv('ELEVENLABS_API_KEY'),        
    )

    # Generate audio and collect all chunks into bytes
    print("Generating audio...")
    audio_generator = client.generate(
        text= os.getenv('STATIC_TEXT'),
        voice=os.getenv('ELEVENLABS_VOICE_NAME'),
        model=os.getenv('ELEVENLABS_MODEL'),
    )
    
    # Convert generator to bytes
    audio_bytes = b"".join(chunk for chunk in audio_generator)
    
    # Write audio bytes to file in assets directory using os.path.join for cross-platform compatibility
    temp_filename = os.path.join('assets', 'audio.mp3')
    with open(temp_filename, 'wb') as f:
        f.write(audio_bytes)
    
    print("Audio generated successfully, playing now...")
    
    # Load and play the audio
    pygame.mixer.music.load(temp_filename)
    pygame.mixer.music.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Add a small delay to ensure audio finishes
    time.sleep(1)
    
    # Cleanup
    pygame.mixer.quit()
    # os.remove(temp_filename)
    
    print("Audio played successfully!")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")
    # Cleanup in case of error
    if 'temp_filename' in locals() and os.path.exists(temp_filename):
        try:
            os.remove(temp_filename)
        except:
            pass
