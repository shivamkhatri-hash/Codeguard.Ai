from typing import Optional
from fastapi import APIRouter

from app.schemas.analysis import Finding
from app.schemas.summary import PRSummaryRequest, PRSummaryResponse
from app.services.agents.pr_summary_agent import pr_summary_agent
from app.services.storage_service import storage_service

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post("", response_model=PRSummaryResponse)
@router.post("/generate", response_model=PRSummaryResponse)
def generate_pr_summary_from_payload(payload: PRSummaryRequest):
    """
    Generates a structured Pull Request review summary directly from payload findings.
    """
    analysis_id = payload.analysis_id or "direct"
    findings = payload.findings or []
    code = payload.code or ""
    language = payload.language or "python"

    if not findings and analysis_id != "direct":
        analysis_data = storage_service.get_analysis(analysis_id)
        if analysis_data:
            findings_raw = analysis_data.get("findings") or []
            findings = [Finding.model_validate(f) for f in findings_raw]
            code = analysis_data.get("code", "")
            language = analysis_data.get("language", "python")

    summary = pr_summary_agent.generate_summary(
        analysis_id=analysis_id,
        findings=findings,
        code=code,
        language=language,
    )
    return summary


@router.get("/{analysis_id}", response_model=PRSummaryResponse)
@router.post("/{analysis_id}", response_model=PRSummaryResponse)
def get_pr_summary(analysis_id: str, payload: Optional[PRSummaryRequest] = None):
    """
    Generates or retrieves a structured Pull Request style review summary
    for the specified code analysis submission ID.
    """
    analysis_data = storage_service.get_analysis(analysis_id)
    if analysis_data:
        findings_raw = analysis_data.get("findings") or []
        findings = [Finding.model_validate(f) for f in findings_raw]
        code = analysis_data.get("code", "")
        language = analysis_data.get("language", "python")
    elif payload and payload.findings:
        findings = payload.findings
        code = payload.code or ""
        language = payload.language or "python"
    else:
        findings = []
        code = ""
        language = "python"

    summary = pr_summary_agent.generate_summary(
        analysis_id=analysis_id,
        findings=findings,
        code=code,
        language=language,
    )
    return summary
