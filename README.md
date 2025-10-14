# ClassNotes AI

AI-powered lecture transcription and analysis tool using NVIDIA APIs. Organize classes, upload lecture videos, get AI-generated summaries, and chat with your notes.

## Features

- 📚 **Class Organization** - Create and manage multiple classes
- 🎥 **Video Transcription** - Auto-transcribe lectures with NVIDIA Riva ASR
- ✨ **AI Summaries** - Generate summaries with NVIDIA Nemotron
- 💬 **Chat Interface** - Ask questions about your lectures
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

## Usage

1. **Create Classes** - On first launch, add your classes (e.g., "CS 229 - Machine Learning")
2. **Upload Lectures** - Select a class and upload a video file
3. **View Summaries** - AI automatically generates summaries for each lecture
4. **Chat** - Ask questions about the lecture content
5. **Browse Sessions** - View all lectures for each class

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
