from fastapi import APIRouter, HTTPException, status
from app.schemas.analysis import AnalysisStatusResponse
from app.services.storage_service import storage_service

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/{analysis_id}", response_model=AnalysisStatusResponse)
def get_analysis_status(analysis_id: str):
    """
    Retrieves the status, syntax correctness report, and structural/security findings of a code submission.
    """
    analysis_data = storage_service.get_analysis(analysis_id)
    if not analysis_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis submission with ID '{analysis_id}' not found"
        )
        
    return AnalysisStatusResponse(
        analysis_id=analysis_data["analysis_id"],
        status=analysis_data["status"],
        language=analysis_data["language"],
        syntax_valid=analysis_data["syntax_valid"],
        errors=analysis_data["errors"],
        findings=analysis_data.get("findings")
    )


@router.get("", response_model=list[AnalysisStatusResponse])
def list_analysis_history():
    """Returns the most recent saved analyses."""
    return [
        AnalysisStatusResponse(
            analysis_id=item["analysis_id"],
            status=item["status"],
            language=item["language"],
            syntax_valid=item["syntax_valid"],
            errors=item.get("errors"),
            findings=item.get("findings"),
        )
        for item in storage_service.list_analyses()
    ]


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: str):
    """Deletes one saved analysis from history."""
    if not storage_service.delete_analysis(analysis_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis submission with ID '{analysis_id}' not found",
        )
