"""
Integrated Class AI Agent with video transcription
"""
from class_agent import ClassAIAgent
from video_transcriber import VideoTranscriber
from typing import Optional, Dict
import os
from pathlib import Path


class IntegratedClassAgent:
    """
    Integrated agent that combines video transcription with class Q&A
    """
    
    def __init__(self, api_key: Optional[str] = None, storage_path: str = "transcripts"):
        """
        Initialize the integrated agent
        
        Args:
            api_key: NVIDIA API key
            storage_path: Path to store transcripts
        """
        self.class_agent = ClassAIAgent(api_key=api_key, storage_path=storage_path)
        self.transcriber = VideoTranscriber(api_key=api_key)
    
    def process_video(
        self,
        video_path: str,
        class_id: str,
        title: Optional[str] = None,
        language_code: str = "en-US",
        auto_summarize: bool = True
    ) -> Dict:
        """
        Process a video: transcribe, store, and optionally summarize
        
        Args:
            video_path: Path to the video file
            class_id: Unique identifier for the class
            title: Optional title for the class
            language_code: Language code for transcription
            auto_summarize: Whether to automatically generate a summary
            
        Returns:
            Dictionary with transcript and summary information
        """
        # Get video filename if no title provided
        if not title:
            title = Path(video_path).stem.replace('_', ' ').replace('-', ' ').title()
        
        # Transcribe the video
        print(f"Processing video: {video_path}")
        transcript = self.transcriber.transcribe_with_fallback(video_path, language_code)
        
        if not transcript or not transcript.strip():
            raise ValueError("Transcription failed or produced empty result")
        
        # Add to class agent
        print(f"Adding transcript to class agent...")
        result = self.class_agent.add_class_transcript(
            class_id=class_id,
            transcript=transcript,
            title=title,
            auto_summarize=auto_summarize
        )
        
        return {
            "class_id": class_id,
            "title": title,
            "transcript": transcript,
            "summary": result.get("summary"),
            "video_path": video_path
        }
    
    def ask_question(self, class_id: str, question: str, stream: bool = True):
        """Ask a question about a class"""
        return self.class_agent.ask_question(class_id, question, stream)
    
    def ask_across_classes(self, question: str, class_ids: Optional[list] = None, stream: bool = True):
        """Ask a question across multiple classes"""
        return self.class_agent.ask_across_classes(question, class_ids, stream)
    
    def list_classes(self):
        """List all available classes"""
        return self.class_agent.list_classes()
    
    def get_class_info(self, class_id: str):
        """Get information about a specific class"""
        return self.class_agent.get_class_info(class_id)
    
    def summarize_transcript(self, class_id: str):
        """Generate or regenerate a summary"""
        return self.class_agent.summarize_transcript(class_id)

