from fastapi import APIRouter

from app.schemas.assistant import ChatRequest, ChatResponse
from app.services.agents.assistant_agent import assistant_agent

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
def assistant_chat(payload: ChatRequest):
    """
    Conversational Code Assistant endpoint for answering developer questions,
    explaining vulnerabilities, and providing secure coding advice.
    """
    response = assistant_agent.ask(
        query=payload.query,
        analysis_id=payload.analysis_id,
        language=payload.language or "python",
        history=payload.history or [],
    )
    return response
