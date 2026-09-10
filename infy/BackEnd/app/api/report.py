from typing import Optional
from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.analysis import Finding
from app.schemas.summary import PRSummaryRequest
from app.services.pdf_report_service import pdf_report_service
from app.services.storage_service import storage_service
from app.services.agents.remediation_agent import remediation_agent

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/pdf/{analysis_id}")
def export_pdf_report_by_id(analysis_id: str):
    """
    Generates and streams a PDF code inspection report for the specified analysis ID.
    """
    analysis_data = storage_service.get_analysis(analysis_id)
    if not analysis_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis submission with ID '{analysis_id}' not found",
        )

    findings_raw = analysis_data.get("findings") or []
    findings = [Finding.model_validate(f) for f in findings_raw]
    filename = analysis_data.get("filename") or ("main." + ("py" if analysis_data.get("language") == "python" else "java"))
    code = analysis_data.get("code", "")
    language = analysis_data.get("language", "python")

    # Fetch cached or generated remediations
    remediations_raw = storage_service.get_remediations(analysis_id)
    if not remediations_raw and findings:
        remediations_raw = remediation_agent.remediate_batch(findings, code, language)

    pdf_bytes = pdf_report_service.generate_pdf(
        analysis_id=analysis_id,
        filename=filename,
        language=language,
        code=code,
        findings=findings,
        remediations=remediations_raw,
    )

    headers = {
        "Content-Disposition": f'attachment; filename="CodeGuard_Report_{analysis_id}.pdf"'
    }

    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@router.post("/pdf/generate")
def generate_pdf_report_from_payload(payload: PRSummaryRequest):
    """
    Generates and streams a PDF code inspection report directly from payload findings.
    """
    analysis_id = payload.analysis_id or "direct"
    findings = payload.findings or []
    code = payload.code or ""
    language = payload.language or "python"
    filename = f"snippet.{'py' if language == 'python' else 'java'}"

    if not findings and analysis_id != "direct":
        analysis_data = storage_service.get_analysis(analysis_id)
        if analysis_data:
            findings_raw = analysis_data.get("findings") or []
            findings = [Finding.model_validate(f) for f in findings_raw]
            code = analysis_data.get("code", "")
            language = analysis_data.get("language", "python")
            filename = analysis_data.get("filename", filename)

    remediations_raw = storage_service.get_remediations(analysis_id) if analysis_id != "direct" else []
    if not remediations_raw and findings:
        remediations_raw = remediation_agent.remediate_batch(findings, code, language)

    pdf_bytes = pdf_report_service.generate_pdf(
        analysis_id=analysis_id,
        filename=filename,
        language=language,
        code=code,
        findings=findings,
        remediations=remediations_raw,
    )

    headers = {
        "Content-Disposition": f'attachment; filename="CodeGuard_Report_{analysis_id}.pdf"'
    }

    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
