from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional, AsyncGenerator
import os
import shutil
import uuid
from datetime import datetime

from integrated_agent import IntegratedClassAgent
from settings_manager import SettingsManager

app = FastAPI(title="Class AI Agent API")

# CORS - allow local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
    ,
    allow_headers=["*"]
)

# Initialize agent
api_key = os.getenv("NVIDIA_API_KEY")
agent = IntegratedClassAgent(api_key=api_key)
settings_mgr = SettingsManager()

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def generate_class_id(base: str) -> str:
    slug = "".join(ch if ch.isalnum() else "-" for ch in base).strip("-").lower() or "class"
    return f"{slug}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"


@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    class_id: str = Form(...),
    session_title: str = Form("") ,
    language_code: str = Form("en-US")
):
    """
    Upload and process a file (video or PDF)
    Automatically detects file type and processes accordingly
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    # Save to disk
    dest_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    base = os.path.splitext(file.filename)[0]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if not session_title:
        session_title = base.replace("_", " ").replace("-", " ").title()

    try:
        # Check if it's a PDF
        if file_ext == ".pdf":
            result = agent.process_pdf(
                pdf_path=dest_path,
                class_id=class_id,
                session_title=session_title,
                auto_summarize=True,
            )
            return {"ok": True, "file_type": "pdf", **result}
        else:
            # Process as video/audio
            result = agent.process_video(
                video_path=dest_path,
                class_id=class_id,
                session_title=session_title,
                language_code=language_code,
                auto_summarize=True,
            )
            return {"ok": True, "file_type": "video", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/classes")
def list_classes():
    return {"ok": True, "classes": agent.list_classes()}


@app.post("/api/classes")
def create_class(name: str = Form(...), code: str = Form(""), color: str = Form("")):
    try:
        obj = agent.create_class(name=name, code=code or None, color=color or None)
        return {"ok": True, "class": obj}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/class/{class_id}")
def get_class(class_id: str):
    info = agent.get_class_info(class_id)
    if not info:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"ok": True, "class": info}


@app.get("/api/settings")
def get_settings():
    return {"ok": True, "settings": settings_mgr.get_settings()}


@app.post("/api/settings")
def update_settings(asr_mode: str = Form(""), llm_provider: str = Form("")):
    try:
        updates = {}
        if asr_mode:
            mode = asr_mode.lower()
            if mode not in ("free", "fast"):
                raise HTTPException(status_code=400, detail="Invalid asr_mode; use 'free' or 'fast'")
            updates["asr_mode"] = mode
        if llm_provider:
            prov = llm_provider.lower()
            if prov not in ("nvidia", "groq", "openai"):
                raise HTTPException(status_code=400, detail="Invalid llm_provider; use 'nvidia', 'openai', or 'groq'")
            updates["llm_provider"] = prov
        if not updates:
            return {"ok": True, "settings": settings_mgr.get_settings()}
        out = settings_mgr.update_settings(updates)
        # Also reflect provider to env so current process switches without restart
        if "llm_provider" in updates:
            os.environ["LLM_PROVIDER"] = updates["llm_provider"]
        return {"ok": True, "settings": out}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/summary/{class_id}/{session_id}")
def regenerate_summary(class_id: str, session_id: str):
    try:
        summary = agent.summarize_session(class_id, session_id)
        return {"ok": True, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/chat/{class_id}")
async def chat_class(class_id: str, question: str = Form(...)):
    try:
        stream = agent.ask_question(class_id, question, stream=True)

        async def generator() -> AsyncGenerator[bytes, None]:
            yield b"{"
            first = True
            yield b'"ok": true, "answer": "'
            for chunk in stream:
                # escape quotes for JSON string
                safe = chunk.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
                yield safe.encode("utf-8")
            yield b'"}'

        return StreamingResponse(generator(), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/chat-all")
async def chat_all(question: str = Form(...)):
    try:
        stream = agent.ask_across_classes(question, stream=True)

        async def generator() -> AsyncGenerator[bytes, None]:
            yield b"{"
            yield b'"ok": true, "answer": "'
            for chunk in stream:
                safe = chunk.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
                yield safe.encode("utf-8")
            yield b'"}'

        return StreamingResponse(generator(), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
