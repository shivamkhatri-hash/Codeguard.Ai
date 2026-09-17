from fastapi import APIRouter, HTTPException, status

from app.schemas.analysis import Finding
from app.services.storage_service import storage_service
from app.services.agents.remediation_agent import remediation_agent


router = APIRouter(
    prefix="/remediation",
    tags=["remediation"],
)


def _finding_key(finding: Finding) -> str:
    """
    Create a unique key for a finding.

    Title + line is used because multiple findings can have
    the same title but occur on different lines.
    """
    return f"{finding.title}|{finding.line}"


@router.post("/{analysis_id}")
def generate_remediation(analysis_id: str):
    """
    Generate or retrieve AI-powered remediation for all findings.
    """

    # ---------------------------------------------------------
    # STEP 1: Retrieve existing analysis
    # ---------------------------------------------------------

    analysis_data = storage_service.get_analysis(analysis_id)

    if not analysis_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Analysis submission with ID "
                f"'{analysis_id}' not found"
            ),
        )

    # ---------------------------------------------------------
    # STEP 2: Check syntax
    # ---------------------------------------------------------

    if not analysis_data["syntax_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Remediation cannot be generated because "
                "the submitted code contains syntax errors."
            ),
        )

    # ---------------------------------------------------------
    # STEP 3: Get findings
    # ---------------------------------------------------------

    findings_data = analysis_data.get("findings")

    if not findings_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No findings were found for this analysis.",
        )

    # ---------------------------------------------------------
    # STEP 4: Convert findings to Finding schemas
    # ---------------------------------------------------------

    try:
        findings = [
            Finding.model_validate(finding_data)
            for finding_data in findings_data
            if finding_data.get("title") != "Software Architecture Metrics"
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to validate analysis findings: {exc}",
        )

    # ---------------------------------------------------------
    # STEP 5: Check SQLite cache
    # ---------------------------------------------------------

    cached_items = storage_service.get_remediations(
        analysis_id
    )

    cached_by_key = {
        item["finding_key"]: item["remediation"]
        for item in cached_items
    }

    remediation_results = []

    findings_needing_llm = []

    for finding in findings:

        key = _finding_key(finding)

        if key in cached_by_key:
            remediation_results.append(
                cached_by_key[key]
            )
        else:
            findings_needing_llm.append(finding)

    # ---------------------------------------------------------
    # STEP 6: Generate remediation only for uncached findings
    # ---------------------------------------------------------

    if findings_needing_llm:

        try:
            new_remediations = (
                remediation_agent.remediate_batch(
                    findings=findings_needing_llm,
                    code=analysis_data["code"],
                    language=analysis_data["language"],
                )
            )

        except Exception as exc:
            error_message = str(exc)

            if "429" in error_message:
                user_message = (
                    "AI remediation is temporarily unavailable "
                    "because the AI service quota has been reached. "
                    "Please use an existing cached remediation or "
                    "try again after the quota resets."
                )

            elif "503" in error_message:
                user_message = (
                    "AI remediation service is temporarily "
                    "unavailable. Please try again shortly."
                )

            elif "timeout" in error_message.lower():
                user_message = (
                    "AI remediation request timed out. "
                    "Please try again."
                )

            else:
                user_message = (
                    f"Remediation generation failed: {error_message}"
                )

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=user_message,
            )

        # -----------------------------------------------------
        # STEP 7: Save newly generated remediations
        # -----------------------------------------------------

        for finding, remediation in zip(
            findings_needing_llm,
            new_remediations,
        ):

            key = _finding_key(finding)

            storage_service.save_remediation(
                analysis_id=analysis_id,
                finding_key=key,
                remediation=remediation,
            )

            cached_by_key[key] = remediation

    # ---------------------------------------------------------
    # STEP 8: Build results in original finding order
    # ---------------------------------------------------------

    remediation_results = []

    for finding in findings:

        key = _finding_key(finding)

        if key in cached_by_key:
            remediation_results.append(
                cached_by_key[key]
            )

    # ---------------------------------------------------------
    # STEP 9: Calculate status
    # ---------------------------------------------------------

    failed_count = sum(
        1
        for result in remediation_results
        if result.get("status") == "failed"
    )

    if failed_count == 0:
        overall_status = "completed"
    elif failed_count < len(remediation_results):
        overall_status = "completed_with_errors"
    else:
        overall_status = "failed"

    # ---------------------------------------------------------
    # STEP 10: Return response
    # ---------------------------------------------------------

    return {
        "analysis_id": analysis_id,
        "status": overall_status,
        "language": analysis_data["language"],
        "remediation_count": len(remediation_results),
        "successful_count": len(remediation_results) - failed_count,
        "failed_count": failed_count,
        "remediations": remediation_results,
    }