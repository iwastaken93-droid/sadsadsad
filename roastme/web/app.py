"""FastAPI application — serves the web UI and API."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from roastme.analyzer.engine import CodeAnalyzer
from roastme.config import RoastConfig
from roastme.personas.base import PERSONAS
from roastme.reviewer.engine import ReviewEngine

app = FastAPI(title="RoastMe", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = Path(__file__).parent.parent / "web" / "dist"

# ── Request/Response Models ──────────────────────────────────

class ConfigRequest(BaseModel):
    api_key: str = ""
    api_base: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    roast_level: str = "savage"
    persona: str = "disappointed_mentor"


class RoastRequest(BaseModel):
    source: str
    file_path: str = "untitled.py"
    config: Optional[ConfigRequest] = None


class AnalyzeRequest(BaseModel):
    source: str
    file_path: str = "untitled.py"


# ── API Endpoints ────────────────────────────────────────────

@app.get("/api/personas")
def list_personas():
    """Return all available roast personas."""
    return {
        pid: {
            "name": p.name,
            "description": p.description,
            "emoji": p.emoji,
        }
        for pid, p in PERSONAS.items()
    }


@app.get("/api/config")
def get_config():
    """Return current configuration (API key redacted)."""
    cfg = RoastConfig.load()
    return {
        "api_key_configured": bool(cfg.api_key),
        "api_base": cfg.api_base,
        "model": cfg.model,
        "roast_level": cfg.roast_level,
        "persona": cfg.persona,
    }


@app.post("/api/config")
def save_config(req: ConfigRequest):
    """Save configuration."""
    cfg = RoastConfig.load()
    cfg.api_key = req.api_key
    cfg.api_base = req.api_base
    cfg.model = req.model
    cfg.roast_level = req.roast_level
    cfg.persona = req.persona
    cfg.save()
    return {"status": "saved"}


@app.post("/api/analyze")
def analyze_code(req: AnalyzeRequest):
    """Run static analysis only."""
    analyzer = CodeAnalyzer()
    result = analyzer.analyze(req.file_path, req.source)
    return {
        "file_path": result.file_path,
        "language": result.language,
        "lines_of_code": result.lines_of_code,
        "function_count": result.function_count,
        "class_count": result.class_count,
        "avg_complexity": result.avg_complexity,
        "shame_score": result.shame_score,
        "summary": result.summary,
        "findings": [
            {
                "line": f.line,
                "end_line": f.end_line,
                "category": f.category.value,
                "severity": f.severity.value,
                "message": f.message,
                "code_snippet": f.code_snippet,
                "roast_hint": f.roast_hint,
            }
            for f in result.findings
        ],
    }


@app.post("/api/roast")
def roast_code(req: RoastRequest):
    """Full roast review with AI."""
    if req.config:
        cfg = RoastConfig(
            api_key=req.config.api_key,
            api_base=req.config.api_base,
            model=req.config.model,
            roast_level=req.config.roast_level,
            persona=req.config.persona,
        )
    else:
        cfg = RoastConfig.load()

    if not cfg.api_key:
        raise HTTPException(400, "No API key configured. Go to Settings to configure.")

    analyzer = CodeAnalyzer()
    analysis = analyzer.analyze(req.file_path, req.source)

    engine = ReviewEngine(cfg)
    result = engine.review(req.file_path, req.source, analysis)

    return {
        "file_path": result.file_path,
        "overall_roast": result.overall_roast,
        "shame_score": result.shame_score,
        "persona_name": result.persona_name,
        "summary": result.summary,
        "line_roasts": [
            {
                "line": lr.line,
                "code_snippet": lr.code_snippet,
                "roast": lr.roast,
                "suggestion": lr.suggestion,
                "category": lr.category,
            }
            for lr in result.line_roasts
        ],
        "refactoring_suggestions": result.refactoring_suggestions,
    }


# ── Serve Frontend ──────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return HTMLResponse("<h1>RoastMe UI not built yet. Run `npm install && npm run build` in web/</h1>")


# Try to mount static files if they exist
if WEB_DIR.exists():
    app.mount("/assets", StaticFiles(directory=WEB_DIR / "assets"), name="assets")
