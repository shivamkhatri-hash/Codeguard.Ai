from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Finding(BaseModel):
    type: str = Field(..., description="Type of finding: 'security_vulnerability' or 'code_smell'")
    title: str = Field(..., description="Name/title of the detected issue")
    severity: str = Field(..., description="Severity level: 'high', 'medium', or 'low'")
    line: int = Field(..., description="Line number of the issue")
    description: str = Field(..., description="Detailed description of what the issue is")
    recommendation: str = Field(..., description="Remediation recommendation retrieved from RAG")
    code_snippet: Optional[str] = Field(None, description="Code snippet containing the issue")

class AnalysisStatusResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique generated 8-character ID for analysis")
    status: str = Field(..., description="Current status: 'submitted', 'completed', or 'failed'")
    language: str = Field(..., description="Programming language of the code")
    syntax_valid: bool = Field(..., description="Flag indicating if the source code contains syntax errors")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of syntax error issues found")
    findings: Optional[List[Finding]] = Field(None, description="List of vulnerability and code quality findings")
