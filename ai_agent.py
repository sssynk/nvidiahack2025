"""
Base AI Agent using NVIDIA API for class transcript processing
"""
from openai import OpenAI
import os
from typing import List, Dict, Optional, Generator


class NvidiaAIAgent:
    """Base AI agent using NVIDIA's API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the NVIDIA AI Agent
        
        Args:
            api_key: NVIDIA API key. If not provided, will look for NVIDIA_API_KEY env variable
        """
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set NVIDIA_API_KEY environment variable or pass api_key parameter")
        
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key
        )
        self.model = "nvidia/nvidia-nemotron-nano-9b-v2"
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.6,
        max_tokens: int = 2048,
        stream: bool = True,
        use_thinking: bool = True
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
        extra_body = {}
        if use_thinking:
            extra_body = {
                "min_thinking_tokens": 1024,
                "max_thinking_tokens": 2048
            }
        
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
        use_thinking: bool = True
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
        extra_body = {}
        if use_thinking:
            extra_body = {
                "min_thinking_tokens": 1024,
                "max_thinking_tokens": 2048
            }
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=0.95,
            max_tokens=max_tokens,
            frequency_penalty=0,
            presence_penalty=0,
            stream=False,
            extra_body=extra_body
        )
        
        return completion.choices[0].message.content

