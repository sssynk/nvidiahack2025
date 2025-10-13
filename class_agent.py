"""
Class AI Agent for transcript summarization and Q&A
"""
from ai_agent import NvidiaAIAgent
from transcript_manager import TranscriptManager
from typing import Optional, List, Dict


class ClassAIAgent:
    """AI Agent specialized for class transcript processing"""
    
    def __init__(self, api_key: Optional[str] = None, storage_path: str = "transcripts"):
        """
        Initialize the Class AI Agent
        
        Args:
            api_key: NVIDIA API key
            storage_path: Path to store transcripts
        """
        self.agent = NvidiaAIAgent(api_key)
        self.transcript_manager = TranscriptManager(storage_path)
    
    def add_class_transcript(
        self, 
        class_id: str, 
        transcript: str, 
        title: Optional[str] = None,
        auto_summarize: bool = True
    ) -> Dict:
        """
        Add a class transcript and optionally generate summary
        
        Args:
            class_id: Unique identifier for the class
            transcript: The transcript content
            title: Optional title for the class
            auto_summarize: Whether to automatically generate a summary
            
        Returns:
            The transcript object
        """
        transcript_obj = self.transcript_manager.add_transcript(
            class_id=class_id,
            content=transcript,
            title=title
        )
        
        if auto_summarize:
            summary = self.summarize_transcript(class_id)
            transcript_obj["summary"] = summary
        
        return transcript_obj
    
    def summarize_transcript(self, class_id: str) -> str:
        """
        Generate a summary for a class transcript
        
        Args:
            class_id: The class identifier
            
        Returns:
            The generated summary
        """
        transcript_obj = self.transcript_manager.get_transcript(class_id)
        if not transcript_obj:
            raise ValueError(f"Transcript not found for class_id: {class_id}")
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at summarizing educational content. Create clear, concise, and comprehensive summaries of class transcripts. Include key topics, main concepts, important points, and any actionable items."
            },
            {
                "role": "user",
                "content": f"Please summarize the following class transcript:\n\n{transcript_obj['content']}"
            }
        ]
        
        summary = self.agent.chat_non_stream(messages, temperature=0.5)
        self.transcript_manager.update_summary(class_id, summary)
        return summary
    
    def ask_question(self, class_id: str, question: str, stream: bool = True):
        """
        Ask a question about a specific class transcript
        
        Args:
            class_id: The class identifier
            question: The question to ask
            stream: Whether to stream the response
            
        Returns:
            Generator yielding response chunks if stream=True, otherwise complete response
        """
        transcript_obj = self.transcript_manager.get_transcript(class_id)
        if not transcript_obj:
            raise ValueError(f"Transcript not found for class_id: {class_id}")
        
        # Include summary if available for context
        context = f"Class Title: {transcript_obj['title']}\n\n"
        if transcript_obj.get('summary'):
            context += f"Summary: {transcript_obj['summary']}\n\n"
        context += f"Full Transcript:\n{transcript_obj['content']}"
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful teaching assistant. Answer questions about class content based on the provided transcript. Be accurate, cite specific parts of the class when relevant, and admit when information isn't in the transcript."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
        
        if stream:
            return self.agent.chat(messages, temperature=0.6)
        else:
            return self.agent.chat_non_stream(messages, temperature=0.6)
    
    def ask_across_classes(self, question: str, class_ids: Optional[List[str]] = None, stream: bool = True):
        """
        Ask a question across multiple class transcripts
        
        Args:
            question: The question to ask
            class_ids: List of class IDs to search. If None, searches all classes
            stream: Whether to stream the response
            
        Returns:
            Generator yielding response chunks if stream=True, otherwise complete response
        """
        transcripts_to_search = []
        
        if class_ids:
            for class_id in class_ids:
                transcript = self.transcript_manager.get_transcript(class_id)
                if transcript:
                    transcripts_to_search.append(transcript)
        else:
            transcripts_to_search = self.transcript_manager.list_transcripts()
        
        if not transcripts_to_search:
            raise ValueError("No transcripts found to search")
        
        # Build context from all relevant transcripts
        context = "Available Class Information:\n\n"
        for t in transcripts_to_search:
            context += f"--- {t['title']} (ID: {t['class_id']}) ---\n"
            if t.get('summary'):
                context += f"Summary: {t['summary']}\n"
            context += f"Transcript: {t['content']}\n\n"
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful teaching assistant. Answer questions by synthesizing information from multiple class transcripts. Cite which specific class(es) you're drawing information from."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
        
        if stream:
            return self.agent.chat(messages, temperature=0.6)
        else:
            return self.agent.chat_non_stream(messages, temperature=0.6)
    
    def list_classes(self) -> List[Dict]:
        """
        List all available classes
        
        Returns:
            List of transcript objects
        """
        return self.transcript_manager.list_transcripts()
    
    def get_class_info(self, class_id: str) -> Optional[Dict]:
        """
        Get information about a specific class
        
        Args:
            class_id: The class identifier
            
        Returns:
            The transcript object or None
        """
        return self.transcript_manager.get_transcript(class_id)

