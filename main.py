# main.py
"""FastAPI 服务：/ask 接口 + 静态前端页面。"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from rag_engine import RAGEngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

engine: Optional[RAGEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时加载一次模型，之后常驻内存。"""
    global engine
    engine = RAGEngine(
        data_path=os.getenv("DATA_PATH", r"D:\demo1\data\产品1.txt"),
        persist_dir=os.getenv("PERSIST_DIR", os.path.join(BASE_DIR, "chroma_db1")),
        rebuild=os.getenv("REBUILD_DB", "0") == "1",  # 想重建库时: set REBUILD_DB=1
    )
    yield
    engine = None


app = FastAPI(title="RAG 问答服务", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- 数据模型 ----------------
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="返回的来源块数")


class Source(BaseModel):
    index: int
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source] = Field(default_factory=list)


# ---------------- 接口 ----------------
@app.get("/health")
async def health():
    return {"status": "ok", "engine_ready": engine is not None}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if engine is None:
        raise HTTPException(status_code=503, detail="RAG 引擎尚未初始化完成，请稍后重试")

    try:
        # 同步的 CPU/IO 重活丢到线程池，避免阻塞事件循环
        result = await run_in_threadpool(engine.ask, req.question, req.top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"处理失败: {exc}") from exc

    return AskResponse(question=req.question, **result)


# ---------------- 静态前端 ----------------
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    async def index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))