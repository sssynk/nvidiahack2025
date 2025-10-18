# 🚀 Quick Start with OpenAI

Your nvidiahack2025 project is now configured to use **OpenAI GPT-4o-mini**!

## ✅ Configuration Complete

- **Provider**: OpenAI
- **Model**: gpt-4o-mini (fast and cost-effective)
- **API Key**: Configured ✓

## 🎯 How to Start the Application

### Option 1: Start Backend API (Recommended)

```bash
cd /Users/josuediaz/nvidiahack2025
./start_backend.sh
```

This will start the FastAPI backend on **http://localhost:8000**

### Option 2: Manual Start with Environment Variables

```bash
cd /Users/josuediaz/nvidiahack2025

# Set environment variables
export LLM_PROVIDER=openai
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_MODEL=gpt-4o-mini

# Start backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Run Gradio UI

```bash
cd /Users/josuediaz/nvidiahack2025

# Set environment variables
export LLM_PROVIDER=openai
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_MODEL=gpt-4o-mini

# Run app
python3 app.py
```

## 🌐 Access the Application

### Next.js UI (Already Running!)
- **URL**: http://localhost:3000
- **Status**: ✅ Running in background
- Modern, beautiful interface

### FastAPI Backend
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- Powers the Next.js frontend

### Gradio UI (Legacy)
- **URL**: http://localhost:7860 (when running app.py)
- Original interface

## 🧪 Test the Setup

Verify OpenAI is working:

```bash
cd /Users/josuediaz/nvidiahack2025

# Set environment variables
export LLM_PROVIDER=openai
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_MODEL=gpt-4o-mini

# Run test
python3 test_openai.py
```

Expected output:
```
🔧 Initializing AI Agent with OpenAI provider...
✅ Provider: openai
✅ Model: gpt-4o-mini
✅ Client initialized: True

💬 Testing chat completion...
📝 Response: Hello from OpenAI!

✅ OpenAI integration working successfully!
```

## 📝 What You Can Do Now

1. **Create Classes** - Organize your lecture notes by class
2. **Upload Videos** - Upload lecture videos for transcription
3. **Get AI Summaries** - Automatic summaries powered by GPT-4o-mini
4. **Ask Questions** - Chat with your lecture notes
5. **Search Across Sessions** - Query multiple lectures at once

## 💡 About GPT-4o-mini

- **Speed**: Very fast responses
- **Cost**: Most economical OpenAI model (~$0.15/1M input tokens)
- **Quality**: Great for educational use cases
- **Capabilities**: Excellent for summaries and Q&A

### Other Available Models

If you want to try different models, change the `OPENAI_MODEL` variable:

```bash
export OPENAI_MODEL=gpt-4o        # More powerful (higher cost)
export OPENAI_MODEL=gpt-4o-mini   # Current setting (cost-effective)
export OPENAI_MODEL=gpt-3.5-turbo # Budget option
```

## 🔧 Troubleshooting

### Backend won't start?
Make sure you're in the correct directory:
```bash
cd /Users/josuediaz/nvidiahack2025
```

### Environment variables not working?
Use the `start_backend.sh` script which sets everything automatically:
```bash
./start_backend.sh
```

### Test script fails?
Make sure the environment variables are set before running:
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY="your_key_here"
python3 test_openai.py
```

### Frontend can't connect to backend?
1. Verify backend is running on port 8000
2. Check http://localhost:8000/docs to confirm
3. Frontend automatically connects to http://localhost:8000

## 🎨 UI Already Running

The Next.js frontend is **already running** at http://localhost:3000!
- Just start the backend and you're ready to go
- No need to restart the frontend

## 📚 More Information

- Full setup guide: See `OPENAI_SETUP.md`
- Configuration options: See `env.example`
- General usage: See `README.md`

## 🎉 You're All Set!

Your application is configured and ready to use with OpenAI GPT-4o-mini.
Start the backend and open http://localhost:3000 to begin!

