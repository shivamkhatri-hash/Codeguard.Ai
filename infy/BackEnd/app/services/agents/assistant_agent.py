from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.assistant import ChatMessage, ChatResponse, RAGSource
from app.services.rag_service import rag_service
from app.services.storage_service import storage_service


class ConversationalAssistantAgent:
    """
    RAG-powered conversational assistant for developer Q&A, follow-up queries
    on flagged vulnerabilities, and secure coding guidance grounded in the knowledge base.
    """

    def __init__(self):
        self.rag_service = rag_service
        self.client = None
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                self.client = genai.Client(
                    api_key=settings.GEMINI_API_KEY,
                    http_options=types.HttpOptions(
                        timeout=30000,
                        retry_options=types.HttpRetryOptions(attempts=1),
                    ),
                )
            except Exception:
                self.client = None

    def ask(
        self,
        query: str,
        analysis_id: Optional[str] = None,
        language: str = "python",
        history: Optional[List[ChatMessage]] = None,
    ) -> ChatResponse:
        """
        Answers developer follow-up queries using RAG context and optional LLM.
        """
        # Step 1: Fetch RAG context
        rag_results = self.rag_service.query(
            query_text=query,
            language=language,
            top_k=3,
        )

        rag_sources = [
            RAGSource(
                title=doc.get("title", "Secure Coding Guideline"),
                category=doc.get("category", "General"),
                score=round(float(doc.get("score", 0.0)), 3),
                snippet=doc.get("content", "")[:250] + "...",
            )
            for doc in rag_results
        ]

        # Step 2: Fetch analysis context if ID is provided
        analysis_context = ""
        if analysis_id:
            analysis_data = storage_service.get_analysis(analysis_id)
            if analysis_data:
                code_snippet = analysis_data.get("code", "")[:1000]
                findings_list = analysis_data.get("findings", []) or []
                findings_str = "\n".join([
                    f"- Line {f.get('line')}: [{f.get('severity')}] {f.get('title')} - {f.get('description')}"
                    for f in findings_list[:5]
                ])
                analysis_context = f"\nAnalyzed Code:\n```\n{code_snippet}\n```\nDetected Findings:\n{findings_str}\n"

        rag_context_text = "\n\n".join([
            f"### {doc['title']} ({doc['category']})\n{doc['content']}"
            for doc in rag_results
        ])

        # Step 3: LLM Generation if available
        if self.client:
            try:
                system_prompt = (
                    f"You are an expert secure coding mentor and AI code review assistant. "
                    f"You help developers understand vulnerabilities, explain code smells, and provide secure code examples.\n"
                    f"Programming Language: {language}\n\n"
                    f"Relevant Knowledge Base Guidelines:\n{rag_context_text}\n"
                    f"{analysis_context}\n"
                    f"Provide clear, actionable, friendly, and well-explained answers with code snippets where helpful."
                )

                history_turns = []
                if history:
                    for msg in history[-4:]:
                        role_label = "User" if msg.role == "user" else "Assistant"
                        history_turns.append(f"{role_label}: {msg.content}")

                history_prompt = "\n".join(history_turns)
                full_prompt = f"{system_prompt}\n\n{history_prompt}\nUser: {query}\nAssistant:"

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                )
                if response.text and response.text.strip():
                    return ChatResponse(
                        response=response.text.strip(),
                        sources=rag_sources,
                    )
            except Exception:
                pass

        # Step 4: Fallback deterministic guidance grounded in RAG KB
        if rag_results:
            top_doc = rag_results[0]
            fallback_text = (
                f"### 🛡️ Knowledge Base Guidance: **{top_doc['title']}**\n\n"
                f"{top_doc['content']}\n\n"
                f"**Recommendation**: When developing in {language.capitalize()}, ensure all inputs are strictly validated, "
                f"secrets are separated from source files, and database queries use prepared statements."
            )
        else:
            fallback_text = (
                f"Based on secure coding best practices for **{language.capitalize()}**:\n\n"
                f"- **Input Validation**: Never trust raw user inputs; sanitize and validate against strict whitelists.\n"
                f"- **Parameterized Queries**: Always use prepared statements or parameterized bindings for SQL/database operations.\n"
                f"- **Secrets Management**: Store API keys, tokens, and credentials in environment variables or a secrets vault.\n"
                f"- **Output Encoding**: Contextually escape dynamic data before rendering in web templates."
            )

        return ChatResponse(
            response=fallback_text,
            sources=rag_sources,
        )


assistant_agent = ConversationalAssistantAgent()
