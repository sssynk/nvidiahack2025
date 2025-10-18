"""
Integrated Class AI Agent with video transcription and PDF processing
"""
from class_agent import ClassAIAgent
from video_transcriber import VideoTranscriber
from pdf_reader import PDFReader
from typing import Optional, Dict
import os
from pathlib import Path
from settings_manager import SettingsManager


class IntegratedClassAgent:
    """
    Integrated agent that combines video transcription, PDF processing, and class Q&A
    """
    
    def __init__(self, api_key: Optional[str] = None, storage_path: str = "transcripts"):
        """
        Initialize the integrated agent
        
        Args:
            api_key: API key (OpenAI, NVIDIA, or Groq)
            storage_path: Path to store transcripts
        """
        self.class_agent = ClassAIAgent(api_key=api_key, storage_path=storage_path)
        self.transcriber = VideoTranscriber(api_key=api_key)
        self.pdf_reader = PDFReader()
        self.settings = SettingsManager(storage_path)
    
    def process_video(
        self,
        video_path: str,
        class_id: str,
        session_title: Optional[str] = None,
        language_code: str = "en-US",
        auto_summarize: bool = True
    ) -> Dict:
        """
        Process a video: transcribe, store, and optionally summarize
        
        Args:
            video_path: Path to the video file
            class_id: Unique identifier for the class
            session_title: Optional title for the session/lecture
            language_code: Language code for transcription
            auto_summarize: Whether to automatically generate a summary
            
        Returns:
            Dictionary with transcript and summary information
        """
        # Get session title from filename if not provided
        if not session_title:
            session_title = Path(video_path).stem.replace('_', ' ').replace('-', ' ').title()
        
        # Transcribe the video using selected ASR mode (env or settings.json)
        print(f"Processing video: {video_path}")
        asr_mode = (os.getenv("ASR_MODE") or self.settings.get("asr_mode", "free")).lower()
        # Allow runtime override by setting ASR_MODE env; otherwise use stored setting
        if asr_mode not in ("free", "fast"):
            asr_mode = "free"
        # Pass through via environment so VideoTranscriber can switch
        os.environ["ASR_MODE"] = asr_mode
        print(f"ASR mode: {asr_mode}")
        transcript = self.transcriber.transcribe_with_fallback(video_path, language_code)
        
        if not transcript or not transcript.strip():
            raise ValueError("Transcription failed or produced empty result")
        
        # Add session to class agent
        print(f"Adding session to class agent...")
        session = self.class_agent.add_class_session(
            class_id=class_id,
            transcript=transcript,
            session_title=session_title,
            auto_summarize=auto_summarize,
        )
        
        return {
            "class_id": class_id,
            "session_id": session.get("session_id"),
            "title": session_title,
            "transcript": transcript,
            "summary": session.get("summary"),
            "video_path": video_path
        }
    
    def process_pdf(
        self,
        pdf_path: str,
        class_id: str,
        session_title: Optional[str] = None,
        auto_summarize: bool = True
    ) -> Dict:
        """
        Process a PDF: extract text, store, and optionally summarize
        
        Args:
            pdf_path: Path to the PDF file
            class_id: Unique identifier for the class
            session_title: Optional title for the session/document
            auto_summarize: Whether to automatically generate a summary
            
        Returns:
            Dictionary with text content and summary information
        """
        # Get session title from filename if not provided
        if not session_title:
            session_title = Path(pdf_path).stem.replace('_', ' ').replace('-', ' ').title()
        
        # Extract text from PDF
        print(f"Processing PDF: {pdf_path}")
        text_content = self.pdf_reader.extract_text_from_pdf(pdf_path)
        
        if not text_content or not text_content.strip():
            raise ValueError("PDF extraction failed or produced empty result")
        
        # Get PDF info for metadata
        pdf_info = self.pdf_reader.get_pdf_info(pdf_path)
        print(f"PDF has {pdf_info.get('num_pages', 'unknown')} pages")
        
        # Add session to class agent (using text_content as "transcript")
        print(f"Adding PDF content to class agent...")
        session = self.class_agent.add_class_session(
            class_id=class_id,
            transcript=text_content,
            session_title=session_title,
            auto_summarize=auto_summarize,
        )
        
        return {
            "class_id": class_id,
            "session_id": session.get("session_id"),
            "title": session_title,
            "transcript": text_content,
            "summary": session.get("summary"),
            "pdf_path": pdf_path,
            "num_pages": pdf_info.get("num_pages", 0)
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
    
    def summarize_session(self, class_id: str, session_id: str):
        """Generate or regenerate a session summary"""
        return self.class_agent.summarize_session(class_id, session_id)

    def create_class(self, name: str, code: Optional[str] = None, color: Optional[str] = None):
        return self.class_agent.create_class(name=name, code=code, color=color)

