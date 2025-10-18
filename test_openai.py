"""
Quick test script to verify OpenAI integration
"""
import os
from ai_agent import NvidiaAIAgent

def test_openai_provider():
    """Test that OpenAI provider works correctly"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Please set it to test OpenAI integration.")
        print("   export OPENAI_API_KEY='your_key_here'")
        return
    
    # Set provider to OpenAI
    os.environ["LLM_PROVIDER"] = "openai"
    
    print("🔧 Initializing AI Agent with OpenAI provider...")
    agent = NvidiaAIAgent()
    
    print(f"✅ Provider: {agent.provider}")
    print(f"✅ Model: {agent.model}")
    print(f"✅ Client initialized: {agent.client is not None}")
    
    # Test a simple chat
    print("\n💬 Testing chat completion...")
    messages = [
        {"role": "user", "content": "Say 'Hello from OpenAI!' in exactly those words."}
    ]
    
    response = agent.chat_non_stream(messages, max_tokens=50)
    print(f"📝 Response: {response}")
    
    print("\n✅ OpenAI integration working successfully!")

if __name__ == "__main__":
    test_openai_provider()

