from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Text content of the message")


class ChatRequest(BaseModel):
    query: str = Field(..., description="User's follow-up question or query")
    analysis_id: Optional[str] = Field(None, description="Optional Analysis ID for context")
    language: Optional[str] = Field("python", description="Programming language context")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Previous conversation turns")


class RAGSource(BaseModel):
    title: str
    category: str
    score: float
    snippet: str


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI Assistant's answer grounded in knowledge base")
    sources: List[RAGSource] = Field(default_factory=list, description="Citations from Secure Coding Knowledge Base")
