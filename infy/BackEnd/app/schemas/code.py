from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from app.schemas.analysis import Finding


class CodeSubmitRequest(BaseModel):
    language: str = Field(
        ...,
        description="Programming language of the code, e.g. 'python' or 'java'"
    )
    code: str = Field(
        ...,
        description="Raw source code content"
    )
    filename: Optional[str] = Field(
        None,
        description="Original source filename (e.g. '0209.py')"
    )


class CodeSubmitResponse(BaseModel):
    analysis_id: str = Field(
        ...,
        description="Unique generated 8-character ID for analysis"
    )
    filename: Optional[str] = Field(
        None,
        description="Filename analyzed"
    )
    status: str = Field(
        ...,
        description="Submission status, e.g. 'submitted', 'completed', or 'failed'"
    )
    language: str = Field(
        ...,
        description="The programming language determined or validated"
    )
    syntax_valid: bool = Field(
        ...,
        description="Flag indicating if the source code contains syntax errors"
    )
    message: str = Field(
        ...,
        description="A status message"
    )
    code: Optional[str] = Field(
        None,
        description="The raw source code context (returned on upload)"
    )
    errors: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of syntax error issues found"
    )
    findings: Optional[List[Finding]] = Field(
        None,
        description="Code quality and security analysis findings"
    )