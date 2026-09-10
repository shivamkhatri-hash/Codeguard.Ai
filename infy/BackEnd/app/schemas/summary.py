from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.analysis import Finding


class PrioritizedFix(BaseModel):
    priority: int = Field(..., description="Priority ranking starting from 1 (highest priority)")
    title: str = Field(..., description="Finding title")
    severity: str = Field(..., description="Severity: high, medium, low")
    line: int = Field(..., description="Line number in source code")
    category: str = Field(..., description="Category: Security or Code Quality")
    action_required: str = Field(..., description="Concise action required to remediate")


class SeverityBreakdown(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0


class PRSummaryRequest(BaseModel):
    analysis_id: Optional[str] = "direct"
    language: Optional[str] = "python"
    code: Optional[str] = ""
    findings: Optional[List[Finding]] = None


class PRSummaryResponse(BaseModel):
    analysis_id: str
    verdict: str = Field(..., description="'Approved', 'Needs Attention', or 'Blocked (High Risk)'")
    health_score: int = Field(..., description="Code Health Score from 0 to 100")
    executive_overview: str = Field(..., description="Executive summary of the code inspection")
    severity_breakdown: SeverityBreakdown
    prioritized_fixes: List[PrioritizedFix]
    markdown_pr_comment: str = Field(..., description="Ready-to-use GitHub PR Markdown comment")
