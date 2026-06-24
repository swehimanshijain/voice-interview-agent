import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from pathlib import Path
import tempfile

load_dotenv()

# Initialize ElevenLabs client
api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key) if api_key else None

def generate_speech(text: str) -> str:
    """Convert text to speech with fallback"""
    Path("recordings").mkdir(exist_ok=True)
    output_path = "recordings/response.mp3"
    
    if not client:
        print("ElevenLabs client not initialized - using fallback")
        return create_fallback_audio(text)
    
    try:
        # Truncate text if too long
        if len(text) > 1500:
            text = text[:1497] + "..."
        
        print(f"Generating TTS for: {text[:50]}...")
        
        audio = client.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        )
        
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        print(f"TTS generated successfully: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"TTS error: {e}")
        return create_fallback_audio(text)

def create_fallback_audio(text: str) -> str:
    """Create a silent audio file as fallback"""
    import wave
    import struct
    
    output_path = "recordings/response.mp3"
    
    try:
        # Create a simple silent WAV file (converted to MP3-like)
        with wave.open("recordings/temp.wav", 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            
            # Generate 0.5 seconds of silence
            samples = [0] * 8000
            data = struct.pack('h' * len(samples), *samples)
            wf.writeframes(data)
        
        # Rename to .mp3 for compatibility
        import shutil
        shutil.move("recordings/temp.wav", output_path)
        
        print(f"Fallback audio created: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Fallback audio error: {e}")
        return output_path