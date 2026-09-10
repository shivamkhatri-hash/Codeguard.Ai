from typing import List

from pydantic import BaseModel, Field


class RemediationResponse(BaseModel):

    recommendation: str = Field(
        ...,
        description="Recommended secure fix for the identified finding",
    )

    explanation: str = Field(
        ...,
        description="Clear explanation of the vulnerability and proposed fix",
    )

    original_code: str = Field(
        ...,
        description="Original vulnerable code",
    )

    corrected_code: str = Field(
        ...,
        description="Corrected secure version of the code",
    )

    why_it_works: str = Field(
        ...,
        description="Explanation of why the corrected code fixes the issue",
    )

    benefits: List[str] = Field(
        default_factory=list,
        description="Benefits of applying the remediation",
    )

    refactoring_suggestions: List[str] = Field(
        default_factory=list,
        description="Additional code quality or refactoring suggestions",
    )

    secure_guidance: str = Field(
        ...,
        description="Secure coding guidance relevant to the finding",
    )

    references: List[str] = Field(
        default_factory=list,
        description="Relevant secure coding references",
    )


class RemediationBatchResponse(BaseModel):
    remediations: List[RemediationResponse] = Field(
        ...,
        description="Remediation results for all supplied findings",
    )