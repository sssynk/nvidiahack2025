#!/usr/bin/env python3
"""
Quick test of video transcription using sample audio
"""
import os
from video_transcriber import VideoTranscriber

# Test with sample audio file
sample_audio = "python-clients/data/examples/en-US_sample.wav"

if not os.path.exists(sample_audio):
    print(f"Sample audio not found: {sample_audio}")
    exit(1)

print(f"Testing transcription with: {sample_audio}")
print("-" * 60)

try:
    transcriber = VideoTranscriber()
    print("Transcribing...")
    transcript = transcriber.transcribe_audio(sample_audio, language_code="en-US")
    print("\nTranscript:")
    print(transcript)
    print("\n" + "-" * 60)
    print("✅ Test successful!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

