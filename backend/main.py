from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.knowledge_base import KnowledgeBase
from backend.app.schemas import (
    AnswerRequest,
    AnswerResponse,
    CompleteResponse,
    InterviewTypeInfo,
    SessionCreateRequest,
    SessionResponse,
)
from backend.app.services.gemini_service import AIResponseError, GeminiService
from backend.app.services.session_manager import InterviewSessionManager, SessionNotFoundError

settings = get_settings()
knowledge_base = KnowledgeBase(settings.knowledge_base_path)
gemini = GeminiService(settings.gemini_api_key, settings.gemini_model)
session_manager = InterviewSessionManager(
    kb=knowledge_base,
    ai=gemini,
    max_questions=settings.max_questions,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/api/interview-types", response_model=list[InterviewTypeInfo])
def get_interview_types() -> list[InterviewTypeInfo]:
    return knowledge_base.interview_types()


@app.post("/api/sessions", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest) -> SessionResponse:
    try:
        return session_manager.create(payload.interview_type)
    except AIResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str) -> SessionResponse:
    try:
        return session_manager.get(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Interview session not found.") from exc


@app.post("/api/sessions/{session_id}/answers", response_model=AnswerResponse)
def submit_answer(session_id: str, payload: AnswerRequest) -> AnswerResponse:
    try:
        return session_manager.answer(session_id=session_id, transcript=payload.transcript)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Interview session not found.") from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/sessions/{session_id}/complete", response_model=CompleteResponse)
def complete_session(session_id: str) -> CompleteResponse:
    try:
        return session_manager.complete(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Interview session not found.") from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
