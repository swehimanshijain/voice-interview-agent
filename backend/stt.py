from faster_whisper import WhisperModel
import os
import numpy as np
import wave
import io

# Initialize Whisper model
model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using Faster Whisper with better error handling"""
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        return ""
    
    print(f"Transcribing: {audio_path}")
    
    try:
        # Check file size
        file_size = os.path.getsize(audio_path)
        if file_size < 1000:  # Less than 1KB
            print("Audio file too small")
            return ""
        
        segments, info = model.transcribe(
            audio_path,
            language="en",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                threshold=0.5
            )
        )
        
        transcript_parts = []
        for segment in segments:
            if segment.text and segment.text.strip():
                transcript_parts.append(segment.text.strip())
        
        transcript = " ".join(transcript_parts)
        transcript = transcript.strip()
        
        print(f"Transcript: {transcript}")
        
        if not transcript:
            print("No speech detected in audio")
            return ""
        
        return transcript
    
    except Exception as e:
        print(f"Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return ""

def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """Transcribe audio from bytes"""
    try:
        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        result = transcribe_audio(tmp_path)
        
        # Clean up
        try:
            os.remove(tmp_path)
        except:
            pass
        
        return result
        
    except Exception as e:
        print(f"Transcription from bytes error: {e}")
        return ""