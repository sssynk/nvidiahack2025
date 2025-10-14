"""
Class AI Agent for transcript summarization and Q&A across sessions per class
"""
from ai_agent import NvidiaAIAgent
from classes_manager import ClassesManager
from typing import Optional, List, Dict


class ClassAIAgent:
    """AI Agent specialized for class transcript processing with multiple sessions per class"""

    def __init__(self, api_key: Optional[str] = None, storage_path: str = "transcripts"):
        """
        Initialize the Class AI Agent

        Args:
            api_key: NVIDIA API key
            storage_path: Path to store transcripts
        """
        self.agent = NvidiaAIAgent(api_key)
        self.classes_manager = ClassesManager(storage_path)
    
    def add_class_session(
        self,
        class_id: str,
        transcript: str,
        session_title: Optional[str] = None,
        auto_summarize: bool = True,
    ) -> Dict:
        """
        Add a session (lecture) to an existing class and optionally generate a summary for that session.

        Args:
            class_id: Unique identifier for the class
            transcript: The transcript content
            session_title: Optional title for the session
            auto_summarize: Whether to automatically generate a session summary

        Returns:
            The session object
        """
        session = self.classes_manager.add_session(
            class_id=class_id,
            title=session_title or "Lecture",
            content=transcript,
            metadata=None,
        )

        if auto_summarize:
            summary = self.summarize_session(class_id, session["session_id"])
            session["summary"] = summary

        return session
    
    def summarize_session(self, class_id: str, session_id: str) -> str:
        """
        Generate a summary for a class session

        Args:
            class_id: The class identifier
            session_id: The session identifier

        Returns:
            The generated summary
        """
        session = self.classes_manager.get_session(class_id, session_id)
        if not session:
            raise ValueError(f"Session not found for class_id={class_id}, session_id={session_id}")

        messages = [
            {
                "role": "system",
                "content": "You are an expert at summarizing educational content. Create clear, concise, and comprehensive summaries of lecture sessions. Include key topics, main concepts, important points."
            },
            {
                "role": "user",
                "content": f"Please summarize the following lecture:\n\n{session['content']}"
            }
        ]

        summary = self.agent.chat_non_stream(messages, temperature=0.5)
        self.classes_manager.update_session_summary(class_id, session_id, summary)
        return summary
    
    def ask_question(self, class_id: str, question: str, stream: bool = True):
        """
        Ask a question about a specific class by synthesizing across its sessions

        Args:
            class_id: The class identifier
            question: The question to ask
            stream: Whether to stream the response

        Returns:
            Generator yielding response chunks if stream=True, otherwise complete response
        """
        cinfo = self.classes_manager.get_class(class_id)
        if not cinfo:
            raise ValueError(f"Class not found: {class_id}")

        # Build context from sessions
        sessions = cinfo.get("sessions", [])
        if not sessions:
            raise ValueError("No sessions found for this class")

        context = f"Class: {cinfo.get('name') or class_id}\n\n"
        for s in sessions:
            context += f"--- {s.get('title')} (ID: {s.get('session_id')}) ---\n"
            if s.get('summary'):
                context += f"Summary: {s['summary']}\n"
            context += f"Transcript: {s.get('content','')}\n\n"

        messages = [
            {
                "role": "system",
                "content": "You are a helpful teaching assistant. Answer questions about class content based on multiple lecture sessions. Cite which session(s) you used. Keep your responses less than 4 sentences."
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
        classes_to_search: List[Dict] = []

        if class_ids:
            for class_id in class_ids:
                cinfo = self.classes_manager.get_class(class_id)
                if cinfo:
                    classes_to_search.append(cinfo)
        else:
            classes_to_search = [self.classes_manager.get_class(c["class_id"]) for c in self.classes_manager.list_classes()]
            classes_to_search = [c for c in classes_to_search if c]

        if not classes_to_search:
            raise ValueError("No classes found to search")

        # Build context from all relevant classes and their sessions
        context = "Available Class Information:\n\n"
        for c in classes_to_search:
            context += f"### Class: {c.get('name')} (ID: {c.get('class_id')})\n"
            for s in c.get("sessions", []):
                context += f"- Session: {s.get('title')} (ID: {s.get('session_id')})\n"
                if s.get('summary'):
                    context += f"  Summary: {s['summary']}\n"
                context += f"  Transcript: {s.get('content','')}\n"
            context += "\n"
        
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
        List all available classes (metadata only)

        Returns:
            List of class objects (without session content)
        """
        return self.classes_manager.list_classes()
    
    def get_class_info(self, class_id: str) -> Optional[Dict]:
        """
        Get information about a specific class, including its sessions

        Args:
            class_id: The class identifier

        Returns:
            The class object with sessions or None
        """
        return self.classes_manager.get_class(class_id)

    # Convenience helpers for class creation used by API/UI
    def create_class(self, name: str, code: Optional[str] = None, color: Optional[str] = None) -> Dict:
        return self.classes_manager.create_class(name=name, code=code, color=color)

