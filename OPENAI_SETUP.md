# OpenAI Integration Guide

## Overview

ClassNotes AI now supports **OpenAI** as an alternative LLM provider alongside NVIDIA and Groq. You can switch between providers using environment variables with minimal code changes.

## What Was Changed

Only **3 files** were modified to add OpenAI support:

1. **`ai_agent.py`** - Added OpenAI provider configuration
2. **`env.example`** - Added OpenAI environment variables documentation
3. **`README.md`** - Added configuration section for users

Total lines changed: **~50 lines**

## Quick Start with OpenAI

### 1. Get an OpenAI API Key

Get your API key from: https://platform.openai.com/api-keys

### 2. Set Environment Variables

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_openai_api_key_here
export OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o
```

Or create a `.env` file:

```bash
cp env.example .env
# Edit .env and set:
LLM_PROVIDER=openai
OPENAI_API_KEY=your_actual_key_here
OPENAI_MODEL=gpt-4o
```

### 3. Start the Application

**Option A: Run the Backend API**
```bash
uvicorn api:app --reload
```

**Option B: Run the Gradio UI**
```bash
python app.py
```

That's it! The application will now use OpenAI instead of NVIDIA.

## Available OpenAI Models

You can choose from any OpenAI model by setting the `OPENAI_MODEL` environment variable:

| Model | Description | Cost | Best For |
|-------|-------------|------|----------|
| `gpt-4o` | Latest GPT-4 Optimized (default) | $$$ | Best quality, most capable |
| `gpt-4o-mini` | Faster, cheaper GPT-4 | $$ | Good balance of speed/quality |
| `gpt-4-turbo` | Previous generation | $$$ | Strong general purpose |
| `gpt-3.5-turbo` | Fast and economical | $ | Budget-friendly option |

Example:
```bash
export OPENAI_MODEL=gpt-4o-mini  # Use the mini variant
```

## Testing the Integration

Run the test script to verify OpenAI is working:

```bash
python test_openai.py
```

Expected output:
```
🔧 Initializing AI Agent with OpenAI provider...
✅ Provider: openai
✅ Model: gpt-4o
✅ Client initialized: True

💬 Testing chat completion...
📝 Response: Hello from OpenAI!

✅ OpenAI integration working successfully!
```

## Switching Between Providers

You can easily switch between providers at any time:

### Use NVIDIA (default):
```bash
unset LLM_PROVIDER  # Or set to "nvidia"
export NVIDIA_API_KEY=your_nvidia_key
```

### Use OpenAI:
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_openai_key
```

### Use Groq:
```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=your_groq_key
```

## Technical Details

### How It Works

The `NvidiaAIAgent` class (in `ai_agent.py`) uses the OpenAI Python SDK's unified interface. All three providers (NVIDIA, OpenAI, Groq) support the OpenAI-compatible API format:

- **NVIDIA**: Uses custom `base_url` pointing to NVIDIA's API
- **Groq**: Uses custom `base_url` pointing to Groq's API
- **OpenAI**: Uses the default OpenAI API endpoint

### Code Changes Summary

**Added OpenAI provider detection:**
```python
if provider == "openai":
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    self.client = OpenAI(api_key=openai_key)
    self.model = os.getenv("OPENAI_MODEL") or "gpt-4o"
    self.provider = "openai"
```

**Skipped NVIDIA-specific parameters for OpenAI:**
```python
if self.provider not in ("groq", "openai"):
    # Only add thinking tokens for NVIDIA
    extra_body = {"use_thinking": False}
```

### Features That Work with OpenAI

✅ **All core features work:**
- Video transcription (using NVIDIA Riva - separate service)
- AI-powered summaries
- Q&A chat interface
- Multi-session queries
- Streaming responses
- Non-streaming responses

❌ **NVIDIA-specific features disabled:**
- Thinking mode (`use_thinking`, `min_thinking_tokens`, `max_thinking_tokens`)

## Transcription Note

**Important:** Audio transcription still uses **NVIDIA Riva ASR** or **Groq Whisper**, regardless of the LLM provider. Only the text generation (summaries, Q&A) uses the selected LLM provider.

To use Groq's Whisper for faster transcription:
```bash
export ASR_MODE=fast
export GROQ_API_KEY=your_groq_key
```

## Cost Considerations

OpenAI pricing is different from NVIDIA:

- **OpenAI GPT-4o**: ~$5/1M input tokens, ~$15/1M output tokens
- **OpenAI GPT-4o-mini**: ~$0.15/1M input tokens, ~$0.60/1M output tokens
- **NVIDIA**: Usage depends on your NVIDIA API credits

For educational use, consider using `gpt-4o-mini` for cost savings.

## Troubleshooting

### Error: "OPENAI_API_KEY environment variable is required"
**Solution:** Make sure you've set the API key:
```bash
export OPENAI_API_KEY=your_actual_key_here
```

### Error: "Invalid API key"
**Solution:** Verify your key at https://platform.openai.com/api-keys

### Wrong provider being used
**Solution:** Explicitly set the provider:
```bash
export LLM_PROVIDER=openai
```

### Model not found error
**Solution:** Use a valid OpenAI model name. Check available models at:
https://platform.openai.com/docs/models

## Support

For issues or questions:
1. Check this documentation
2. Verify environment variables are set correctly
3. Test with `python test_openai.py`
4. Check the console logs for detailed error messages

