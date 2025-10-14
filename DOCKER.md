# Docker Setup Guide

This guide explains how to run the ClassNotes AI application using Docker.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- NVIDIA API Key

## Quick Start

### 1. Set up environment variables

Copy the example environment file and add your NVIDIA API key:

```bash
cp env.example .env
```

Edit `.env` and replace `your_nvidia_api_key_here` with your actual NVIDIA API key:

```
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxx
```

### 2. Build and run with Docker Compose

```bash
docker-compose up --build
```

This will:
- Build the backend (FastAPI) container
- Build the frontend (Next.js) container
- Start both services
- Backend will be available at http://localhost:8000
- Frontend will be available at http://localhost:3000

### 3. Access the application

Open your browser and go to:
- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs (FastAPI Swagger docs)

## Docker Commands

### Start services (detached mode)
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Rebuild after code changes
```bash
docker-compose up --build
```

### Remove all containers and volumes
```bash
docker-compose down -v
```

## Data Persistence

The following directories are mounted as volumes to persist data:
- `./transcripts` - Stores class and session data
- `./uploads` - Stores uploaded video files

These directories will persist even if you stop or remove the containers.

## Troubleshooting

### Port already in use
If ports 3000 or 8000 are already in use, you can change them in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change 8001 to any available port
  
  frontend:
    ports:
      - "3001:3000"  # Change 3001 to any available port
```

### Backend can't connect to NVIDIA API
Make sure your `.env` file has the correct `NVIDIA_API_KEY` set.

### Frontend can't reach backend
If running on a different machine or network, update the `NEXT_PUBLIC_API_BASE` in `docker-compose.yml`:

```yaml
frontend:
  environment:
    - NEXT_PUBLIC_API_BASE=http://your-backend-host:8000
```

## Production Deployment

For production, consider:
1. Using a reverse proxy (nginx) in front of both services
2. Setting up SSL/TLS certificates
3. Using environment-specific `.env` files
4. Implementing proper logging and monitoring
5. Setting resource limits in docker-compose.yml

## Individual Container Build

### Backend only
```bash
docker build -f Dockerfile.backend -t classnotes-backend .
docker run -p 8000:8000 --env-file .env classnotes-backend
```

### Frontend only
```bash
cd ui
docker build -t classnotes-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_BASE=http://localhost:8000 classnotes-frontend
```

