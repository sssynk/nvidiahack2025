"""
Base AI Agent using NVIDIA API for class transcript processing
"""
from openai import OpenAI
import os
from typing import List, Dict, Optional, Generator, Any


class NvidiaAIAgent:
    """AI agent that can use NVIDIA or Groq (OpenAI-compatible) based on configuration."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI Agent.

        Provider selection order:
        - LLM_PROVIDER env ("groq" or "nvidia")
        - Default: nvidia
        """
        self._init_api_key = api_key
        self.client: OpenAI | None = None
        self.model: str = ""
        self.provider: str = ""
        self._configure_client()

    def _configure_client(self) -> None:
        provider = (os.getenv("LLM_PROVIDER") or "nvidia").strip().lower()
        
        # OpenAI provider
        if provider == "openai":
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
            self.client = OpenAI(api_key=openai_key)  # No custom base_url needed for OpenAI
            self.model = os.getenv("OPENAI_MODEL") or "gpt-4o"  # Default to gpt-4o
            self.provider = "openai"
            return
        
        # Groq provider
        if provider == "groq":
            groq_key = os.getenv("GROQ_API_KEY")
            if not groq_key:
                # Fallback to NVIDIA if GROQ_API_KEY missing
                provider = "nvidia"
            else:
                self.client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_key)
                self.model = "openai/gpt-oss-20b"
                self.provider = "groq"
                return

        # Default to NVIDIA
        nvidia_key = self._init_api_key or os.getenv("NVIDIA_API_KEY")
        if not nvidia_key:
            raise ValueError("API key is required. Set NVIDIA_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY environment variable")
        self.client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=nvidia_key)
        self.model = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
        self.provider = "nvidia"

    def _ensure_client(self) -> None:
        # Reconfigure if provider changed at runtime
        current = (os.getenv("LLM_PROVIDER") or "nvidia").strip().lower()
        if current != self.provider:
            self._configure_client()
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.6,
        max_tokens: int = 2048,
        stream: bool = True,
        use_thinking: bool = False
    ) -> Generator[str, None, None]:
        """
        Send a chat request to the NVIDIA API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            use_thinking: Whether to enable thinking mode
            
        Yields:
            Response chunks from the API
        """
        self._ensure_client()
        extra_body = {}
        # Avoid provider-specific fields for Groq and OpenAI
        if self.provider not in ("groq", "openai"):
            if use_thinking:
                extra_body = {
                    "min_thinking_tokens": 1024,
                    "max_thinking_tokens": 2048
                }
            else:
                extra_body = {
                    "use_thinking": False
                }
        
        assert self.client is not None
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=0.95,
            max_tokens=max_tokens,
            frequency_penalty=0,
            presence_penalty=0,
            stream=stream,
            extra_body=extra_body
        )
        
        if stream:
            for chunk in completion:
                reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
                if reasoning:
                    yield reasoning
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        else:
            yield completion.choices[0].message.content
    
    def chat_non_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.6,
        max_tokens: int = 2048,
        use_thinking: bool = True,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send a non-streaming chat request to the NVIDIA API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_thinking: Whether to enable thinking mode
            
        Returns:
            Complete response from the API
        """
        self._ensure_client()
        extra_body = {}
        if self.provider not in ("groq", "openai"):
            if use_thinking:
                extra_body = {
                    "min_thinking_tokens": 1024,
                    "max_thinking_tokens": 2048
                }
            else:
                extra_body = {
                    "use_thinking": False
                }

        assert self.client is not None
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.95,
            "max_tokens": max_tokens,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stream": False,
            "extra_body": extra_body,
        }
        if response_format is not None:
            kwargs["response_format"] = response_format

        completion = self.client.chat.completions.create(**kwargs)
        
        return completion.choices[0].message.content

