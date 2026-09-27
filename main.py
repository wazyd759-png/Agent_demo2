"""FastAPI 服务：SQL Agent 问答。"""
from __future__ import annotations

import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()  # 读 .env

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from Agent_transfer import ask_agent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="SQL Agent 问答助手", version="1.0.0")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask")
async def ask(req: AskRequest):
    try:
        result = await run_in_threadpool(ask_agent, req.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"处理失败: {exc}") from exc
    return result


if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    async def index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))