"""
Video transcription using NVIDIA Riva ASR client
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple


class VideoTranscriber:
    """Handles video-to-text transcription using NVIDIA Riva ASR"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the video transcriber
        
        Args:
            api_key: NVIDIA API key. If not provided, will look for NVIDIA_API_KEY env variable
        """
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set NVIDIA_API_KEY environment variable or pass api_key parameter")
        
        self.asr_function_id = "d8dd4e9b-fbf5-4fb0-9dba-8cf436c8d965"
        self.server = "grpc.nvcf.nvidia.com:443"
        self.riva_script = os.path.join(os.path.dirname(__file__), "python-clients/scripts/asr/transcribe_file.py")
    
    def extract_audio_from_video(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract audio from video file using ffmpeg
        
        Args:
            video_path: Path to the video file
            output_path: Optional path for output audio file
            
        Returns:
            Path to the extracted audio file
        """
        if output_path is None:
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"audio_{os.path.basename(video_path)}.wav")
        
        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("ffmpeg is not installed. Please install ffmpeg to extract audio from videos.")
        
        # Extract audio using ffmpeg
        # Convert to 16kHz mono WAV (optimal for speech recognition)
        command = [
            "ffmpeg", "-i", video_path,
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # PCM 16-bit little-endian
            "-ar", "16000",  # 16kHz sample rate
            "-ac", "1",  # Mono
            "-y",  # Overwrite output file
            output_path
        ]
        
        try:
            result = subprocess.run(command, capture_output=True, check=True, text=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract audio: {e.stderr}")
    
    def transcribe_audio(self, audio_path: str, language_code: str = "en-US") -> str:
        """
        Transcribe audio file using NVIDIA Riva ASR client
        
        Args:
            audio_path: Path to the audio file
            language_code: Language code (default: en-US)
            
        Returns:
            Transcribed text
        """
        if not os.path.isfile(audio_path):
            raise ValueError(f"Invalid audio file path: {audio_path}")
        
        # Build command to run Riva transcription script
        command = [
            "python", self.riva_script,
            "--server", self.server,
            "--use-ssl",
            "--metadata", "function-id", self.asr_function_id,
            "--metadata", "authorization", f"Bearer {self.api_key}",
            "--language-code", language_code,
            "--input-file", audio_path
        ]
        
        try:
            # Run the Riva client script and capture output
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=300
            )
            
            # Parse the output to extract transcript
            # The Riva script prints transcripts to stdout
            output = result.stdout.strip()
            
            # Extract only the final transcript (last line usually)
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            if lines:
                # Return the last non-empty line which should be the final transcript
                return lines[-1]
            else:
                raise ValueError("No transcript generated")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Transcription timed out after 5 minutes")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Riva ASR failed: {e.stderr}")
    
    def transcribe_video(self, video_path: str, language_code: str = "en-US", cleanup: bool = True) -> Tuple[str, str]:
        """
        Complete video-to-text pipeline
        
        Args:
            video_path: Path to the video file
            language_code: Language code for transcription
            cleanup: Whether to delete temporary audio file
            
        Returns:
            Tuple of (transcript_text, audio_file_path)
        """
        print(f"Extracting audio from video: {video_path}")
        audio_path = self.extract_audio_from_video(video_path)
        
        print(f"Transcribing audio: {audio_path}")
        transcript = self.transcribe_audio(audio_path, language_code)
        
        if cleanup and audio_path.startswith(tempfile.gettempdir()):
            try:
                os.remove(audio_path)
                print(f"Cleaned up temporary file: {audio_path}")
            except Exception as e:
                print(f"Warning: Could not remove temporary file: {e}")
        
        return transcript, audio_path
    
    def transcribe_with_fallback(self, file_path: str, language_code: str = "en-US") -> str:
        """
        Transcribe with automatic audio/video detection and fallback
        
        Args:
            file_path: Path to audio or video file
            language_code: Language code for transcription
            
        Returns:
            Transcribed text
        """
        file_ext = Path(file_path).suffix.lower()
        
        # Audio formats - transcribe directly
        audio_formats = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
        # Video formats - extract audio first
        video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        
        if file_ext in audio_formats:
            print("Detected audio file, transcribing directly...")
            return self.transcribe_audio(file_path, language_code)
        elif file_ext in video_formats:
            print("Detected video file, extracting audio first...")
            transcript, _ = self.transcribe_video(file_path, language_code)
            return transcript
        else:
            # Try as video first, then audio
            try:
                print("Unknown format, attempting video extraction...")
                transcript, _ = self.transcribe_video(file_path, language_code)
                return transcript
            except Exception as e:
                print(f"Video extraction failed, trying direct transcription: {e}")
                return self.transcribe_audio(file_path, language_code)

