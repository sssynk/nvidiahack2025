"""
Transcript Manager for storing and managing class transcripts
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class TranscriptManager:
    """Manages class transcripts storage and retrieval"""
    
    def __init__(self, storage_path: str = "transcripts"):
        """
        Initialize the transcript manager
        
        Args:
            storage_path: Directory to store transcript files
        """
        self.storage_path = storage_path
        self._ensure_storage_exists()
        self.transcripts: Dict[str, Dict] = {}
        self.load_all_transcripts()
    
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def add_transcript(
        self, 
        class_id: str, 
        content: str, 
        title: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Add a new class transcript
        
        Args:
            class_id: Unique identifier for the class
            content: The transcript content
            title: Optional title for the class
            metadata: Optional metadata dict
            
        Returns:
            The created transcript object
        """
        transcript = {
            "class_id": class_id,
            "title": title or f"Class {class_id}",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "summary": None
        }
        
        self.transcripts[class_id] = transcript
        self._save_transcript(class_id, transcript)
        return transcript
    
    def get_transcript(self, class_id: str) -> Optional[Dict]:
        """
        Get a transcript by class ID
        
        Args:
            class_id: The class identifier
            
        Returns:
            The transcript dict or None if not found
        """
        return self.transcripts.get(class_id)
    
    def list_transcripts(self) -> List[Dict]:
        """
        List all transcripts
        
        Returns:
            List of all transcript objects
        """
        return list(self.transcripts.values())
    
    def update_summary(self, class_id: str, summary: str):
        """
        Update the summary for a transcript
        
        Args:
            class_id: The class identifier
            summary: The summary text
        """
        if class_id in self.transcripts:
            self.transcripts[class_id]["summary"] = summary
            self._save_transcript(class_id, self.transcripts[class_id])
    
    def _save_transcript(self, class_id: str, transcript: Dict):
        """Save a transcript to file"""
        file_path = os.path.join(self.storage_path, f"{class_id}.json")
        with open(file_path, 'w') as f:
            json.dump(transcript, f, indent=2)
    
    def load_all_transcripts(self):
        """Load all transcripts from storage"""
        if not os.path.exists(self.storage_path):
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_path, filename)
                with open(file_path, 'r') as f:
                    transcript = json.load(f)
                    self.transcripts[transcript['class_id']] = transcript
    
    def delete_transcript(self, class_id: str) -> bool:
        """
        Delete a transcript
        
        Args:
            class_id: The class identifier
            
        Returns:
            True if deleted, False if not found
        """
        if class_id in self.transcripts:
            del self.transcripts[class_id]
            file_path = os.path.join(self.storage_path, f"{class_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        return False

