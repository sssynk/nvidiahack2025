# ClassNotes AI

AI-powered lecture transcription and analysis tool using NVIDIA APIs. Organize classes, upload lecture videos, get AI-generated summaries, and chat with your notes.

## Features

- 📚 **Class Organization** - Create and manage multiple classes
- 🎥 **Video Transcription** - Auto-transcribe lectures with NVIDIA Riva ASR
- 📄 **Document Support** - Upload and analyze PDFs and Word documents (slides, readings, notes)
- ✨ **AI Summaries** - Generate summaries with GPT, NVIDIA Nemotron, or Groq
- 💬 **Chat Interface** - Ask questions about your lectures and PDFs
- 🔍 **Multi-Session Search** - Query across all sessions in a class
- 🎨 **Modern UI** - Beautiful Next.js + shadcn/ui interface

## Quick Start (Docker - Recommended)

The easiest way to run the application:

```bash
# 1. Copy environment file and add your NVIDIA API key
cp env.example .env
# Edit .env and add your NVIDIA_API_KEY

# 2. Start with Docker Compose
docker-compose up --build

# 3. Open http://localhost:3000
```

See [DOCKER.md](DOCKER.md) for detailed Docker instructions.

## Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- ffmpeg
- NVIDIA API Key ([Get one here](https://build.nvidia.com/))

### Backend Setup

1. Install ffmpeg:
   ```bash
   # macOS
   brew install ffmpeg
   
   # Linux
   sudo apt-get install ffmpeg
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your API key:
   ```bash
   export NVIDIA_API_KEY='your_api_key_here'
   ```

4. Start the FastAPI backend:
   ```bash
   uvicorn api:app --reload
   ```
   Backend runs on http://localhost:8000

### Frontend Setup

1. Install Node dependencies:
   ```bash
   cd ui
   npm install
   ```

2. Set environment variable (optional):
   ```bash
   export NEXT_PUBLIC_API_BASE=http://localhost:8000
   ```

3. Start the Next.js dev server:
   ```bash
   npm run dev
   ```
   Frontend runs on http://localhost:3000

## Configuration

### LLM Provider Options

ClassNotes AI supports multiple LLM providers. Configure via environment variables:

```bash
# Choose your provider (default: nvidia)
LLM_PROVIDER=openai  # Options: nvidia, openai, groq

# OpenAI (if using openai provider)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o

# NVIDIA (if using nvidia provider)
NVIDIA_API_KEY=your_nvidia_api_key_here

# Groq (if using groq provider)
GROQ_API_KEY=your_groq_api_key_here
```

**OpenAI Models:**
- `gpt-4o` - Latest GPT-4 Optimized (default, recommended)
- `gpt-4o-mini` - Faster and cheaper variant
- `gpt-4-turbo` - Previous generation
- `gpt-3.5-turbo` - Budget option

**ASR Options:**
For audio transcription, you can also configure:
```bash
ASR_MODE=free  # Options: free (NVIDIA Riva), fast (Groq Whisper - requires GROQ_API_KEY)
```

### Using OpenAI

To use OpenAI instead of NVIDIA:

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Set environment variables:
   ```bash
   export LLM_PROVIDER=openai
   export OPENAI_API_KEY=your_openai_key_here
   ```
3. Start the backend as normal

## Usage

1. **Create Classes** - On first launch, add your classes (e.g., "CS 229 - Machine Learning")
2. **Upload Content** - Select a class and upload video files or PDFs (slides, readings)
3. **View Summaries** - AI automatically generates summaries for each session
4. **Chat** - Ask questions about your lectures and documents
5. **Browse Sessions** - View all sessions (videos and PDFs) for each class

### Supported File Types
- **Videos**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`
- **Audio**: `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`
- **Documents**: `.pdf`, `.docx` (lecture slides, readings, textbooks, Word documents)

See [PDF_SUPPORT.md](PDF_SUPPORT.md) for details on document upload features.

## Tech Stack

- **Backend**: FastAPI, NVIDIA Riva ASR, NVIDIA Nemotron LLM
- **Frontend**: Next.js 15, React, TypeScript, shadcn/ui, Tailwind CSS
- **Storage**: JSON file-based (classes and sessions)
- **Deployment**: Docker + Docker Compose

## API Documentation

When running, visit http://localhost:8000/docs for interactive API documentation.

## Legacy Gradio UI

The original Gradio interface is still available:
```bash
python app.py
```
Open http://localhost:7860
