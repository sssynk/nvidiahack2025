# Class AI Agent

AI agent for transcribing class videos and answering questions using NVIDIA APIs.

## Setup

1. Install ffmpeg: `brew install ffmpeg` (macOS) or `sudo apt-get install ffmpeg` (Linux)
2. Install Python packages: `pip install -r requirements.txt`
3. Set API key: `export NVIDIA_API_KEY='your_api_key_here'`

Get your API key at https://build.nvidia.com/

## Usage

### Web UI (Recommended)
```bash
python app.py
```
Open http://localhost:7860

### CLI
```bash
python cli.py
```

## Features

- Upload videos → auto-transcribe with NVIDIA ASR
- Auto-generate summaries with NVIDIA Nemotron  
- Ask questions about classes
- Search across multiple classes
