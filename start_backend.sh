#!/bin/bash

# Start the backend with OpenAI configuration
export LLM_PROVIDER=openai
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_MODEL=gpt-4o-mini
export ASR_MODE=free

echo "🚀 Starting backend with OpenAI configuration..."
echo "   Provider: $LLM_PROVIDER"
echo "   Model: $OPENAI_MODEL"
echo ""
echo "📄 PDF uploads: ENABLED"
echo "🎥 Video uploads: Require NVIDIA_API_KEY for transcription"
echo ""
echo "Backend will be available at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend UI: http://localhost:3000"
echo ""

python3 -m uvicorn api:app --reload --host 0.0.0.0 --port 8000

