from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.schemas.code import CodeSubmitRequest, CodeSubmitResponse
from app.services.code_validator import code_validator_service
from app.services.file_service import file_service
from app.services.storage_service import storage_service
from app.services.agent_orchestrator import agent_orchestrator


router = APIRouter(prefix="/code", tags=["code"])


@router.post("/submit", response_model=CodeSubmitResponse)
async def submit_code(payload: CodeSubmitRequest):
    """
    Submits source code directly in a JSON body.

    Performs validation on code size, language support,
    syntax correctness, and full security/vulnerability analysis.
    """

    # Validate basic metadata
    is_valid, err_msg = code_validator_service.validate_metadata(
        payload.code,
        payload.language
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

    # Run syntax validation
    syntax_result = code_validator_service.validate_code(
        payload.code,
        payload.language
    )

    # Run full code quality and security analysis if syntax is correct
    analysis_findings = None

    if syntax_result["syntax_valid"]:
        analysis_findings = await agent_orchestrator.analyze(
    payload.code,
    payload.language
)

    # Generate unique analysis ID
    analysis_id = storage_service.generate_id()

    # Save validation state + findings to memory storage
    filename = payload.filename or ("main." + ("py" if payload.language.lower() == "python" else "java"))
    analysis_data = {
        "analysis_id": analysis_id,
        "filename": filename,
        "status": (
            "completed"
            if syntax_result["syntax_valid"]
            else "failed"
        ),
        "language": payload.language.lower(),
        "code": payload.code,
        "syntax_valid": syntax_result["syntax_valid"],
        "errors": syntax_result["errors"],
        "findings": (
            [f.model_dump() for f in analysis_findings]
            if analysis_findings
            else None
        )
    }

    storage_service.save_analysis(
        analysis_id,
        analysis_data
    )

    # Return validation + code analysis results
    return CodeSubmitResponse(
        analysis_id=analysis_id,
        filename=filename,
        status=analysis_data["status"],
        language=analysis_data["language"],
        syntax_valid=analysis_data["syntax_valid"],
        errors=analysis_data["errors"],
        message=(
            "Code analyzed successfully."
            if analysis_data["status"] == "completed"
            else "Code submitted but syntax errors were found."
        ),
        findings=analysis_findings
    )


@router.post("/upload", response_model=CodeSubmitResponse)
async def upload_code(file: UploadFile = File(...)):
    """
    Uploads a code file, runs syntax checking and
    code quality/security vulnerability analysis.
    """

    # Validate extension
    ext_valid, ext_err = file_service.validate_file_metadata(file)

    if not ext_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ext_err
        )

    try:
        # Read content, validate size limits, and extract language
        code, language = await file_service.extract_content_and_validate_size(
            file
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the file: {str(e)}"
        )

    # Run syntax validation
    syntax_result = code_validator_service.validate_code(
        code,
        language
    )

    # Run full code analysis if syntax is valid
    analysis_findings = None

    if syntax_result["syntax_valid"]:
        analysis_findings = await agent_orchestrator.analyze(
            code,
            language
        )

    # Generate unique analysis ID
    analysis_id = storage_service.generate_id()
    filename = file.filename or ("uploaded." + ("py" if language == "python" else "java"))

    # Save validation state to memory
    analysis_data = {
        "analysis_id": analysis_id,
        "filename": filename,
        "status": (
            "completed"
            if syntax_result["syntax_valid"]
            else "failed"
        ),
        "language": language,
        "code": code,
        "syntax_valid": syntax_result["syntax_valid"],
        "errors": syntax_result["errors"],
        "findings": (
            [f.model_dump() for f in analysis_findings]
            if analysis_findings
            else None
        )
    }

    storage_service.save_analysis(
        analysis_id,
        analysis_data
    )

    return CodeSubmitResponse(
        analysis_id=analysis_id,
        filename=filename,
        status=analysis_data["status"],
        language=analysis_data["language"],
        syntax_valid=analysis_data["syntax_valid"],
        errors=analysis_data["errors"],
        code=code,
        message=(
            "Code uploaded and analyzed successfully."
            if analysis_data["status"] == "completed"
            else "Code uploaded but syntax errors were found."
        ),
        findings=analysis_findings
    )