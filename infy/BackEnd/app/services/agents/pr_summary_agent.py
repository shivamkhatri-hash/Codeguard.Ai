from typing import Any, Dict, List, Optional
import re

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.analysis import Finding
from app.schemas.summary import PRSummaryResponse, PrioritizedFix, SeverityBreakdown


class PRSummaryAgent:
    """
    Compiles findings, quality metrics, and security warnings from all agents
    into a structured pull-request style review summary with an executive overview,
    severity breakdown, health score, and prioritized fix list.
    """

    def __init__(self):
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

    @staticmethod
    def calculate_health_score(findings: List[Finding]) -> int:
        """
        Calculates an overall code health score from 0 to 100 based on severity penalties.
        Base: 100
        Penalties: High: -15, Medium: -8, Low: -3 (excluding software architecture metrics)
        """
        score = 100
        for f in findings:
            if f.title == "Software Architecture Metrics":
                continue
            sev = (f.severity or "low").lower()
            if sev == "high":
                score -= 15
            elif sev == "medium":
                score -= 8
            else:
                score -= 3
        return max(0, min(100, score))

    def _determine_verdict(self, high_count: int, medium_count: int, health_score: int) -> str:
        if high_count > 0:
            return "Blocked (Critical Security Risks Detected)"
        if medium_count > 2 or health_score < 70:
            return "Needs Attention (Medium Severity & Quality Issues)"
        return "Approved (Safe to Merge)"

    def generate_summary(
        self,
        analysis_id: str,
        findings: List[Finding],
        code: str = "",
        language: str = "python",
    ) -> PRSummaryResponse:
        """
        Compiles all findings into a structured Pull Request style summary.
        """
        # Exclude metadata metrics from fix counts
        actionable_findings = [f for f in findings if f.title != "Software Architecture Metrics"]

        high_findings = [f for f in actionable_findings if (f.severity or "").lower() == "high"]
        med_findings = [f for f in actionable_findings if (f.severity or "").lower() == "medium"]
        low_findings = [f for f in actionable_findings if (f.severity or "").lower() == "low"]

        breakdown = SeverityBreakdown(
            high=len(high_findings),
            medium=len(med_findings),
            low=len(low_findings),
            total=len(actionable_findings),
        )

    @staticmethod
    def _extract_action(finding: Finding, language: str = "python") -> str:
        title = (finding.title or "").lower()
        desc = (finding.description or "").lower()

        # Specific concise direct recommendations
        if "sql injection" in title or "sql injection" in desc:
            return "Use parameterized queries with prepared statements instead of dynamic SQL concatenation."
        if "secret" in title or "credential" in title or "key" in title or "hardcoded" in title:
            return "Move hardcoded secret/credentials to environment variables (e.g. os.getenv) or secret vaults."
        if "command injection" in title or "os.system" in desc or "subprocess" in desc:
            return "Avoid shell=True and os.system; use subprocess.run with argument list parameter binding."
        if "xss" in title or "cross-site scripting" in desc:
            return "Contextually escape and sanitize untrusted variables before rendering in HTML output."
        if "hash" in title or "cryptograph" in title:
            return "Replace weak MD5/SHA1 algorithm with bcrypt, argon2, or SHA-256 for secure hashing."
        if "docstring" in title:
            return "Add a descriptive docstring explaining function purpose, parameters, and return value."
        if "complexity" in title or "cyclomatic" in desc:
            return "Refactor large conditional blocks into smaller, modular single-responsibility helper functions."
        if "mutable default" in title or "mutable" in desc:
            return "Replace mutable default argument (list/dict) with None and initialize inside the function body."
        if "wildcard" in title or "import *" in desc:
            return "Replace wildcard 'import *' with explicit imports to prevent namespace pollution."
        if "bare except" in title or "broad exception" in desc or "catch-all" in desc:
            return "Catch specific exception types instead of bare 'except:' to avoid masking critical runtime errors."

        # Fallback: extract the first actual recommendation line (skipping generic headers)
        if finding.recommendation:
            lines = [l.strip() for l in finding.recommendation.splitlines() if l.strip()]
            for line in lines:
                if (
                    line.endswith(":")
                    or line.lower().startswith("prevention")
                    or line.lower().startswith("owasp top 10")
                    or line.lower().startswith("no sufficiently")
                ):
                    continue
                clean = re.sub(r"^\d+[\.\)]\s*", "", line)
                if len(clean) > 15:
                    return clean[:120]

        return f"Refactor {finding.title} on line {finding.line} according to established {language.capitalize()} secure coding guidelines."

    def generate_summary(
        self,
        analysis_id: str,
        findings: List[Finding],
        code: str = "",
        language: str = "python",
    ) -> PRSummaryResponse:
        """
        Compiles all findings into a structured Pull Request style summary.
        """
        # Exclude metadata metrics from fix counts
        actionable_findings = [f for f in findings if f.title != "Software Architecture Metrics"]

        high_findings = [f for f in actionable_findings if (f.severity or "").lower() == "high"]
        med_findings = [f for f in actionable_findings if (f.severity or "").lower() == "medium"]
        low_findings = [f for f in actionable_findings if (f.severity or "").lower() == "low"]

        breakdown = SeverityBreakdown(
            high=len(high_findings),
            medium=len(med_findings),
            low=len(low_findings),
            total=len(actionable_findings),
        )

        health_score = self.calculate_health_score(findings)
        verdict = self._determine_verdict(breakdown.high, breakdown.medium, health_score)

        # Build prioritized fix list
        prioritized_fixes: List[PrioritizedFix] = []
        priority_idx = 1

        for f in high_findings + med_findings + low_findings:
            category = "Security" if (
                f.type == "security_vulnerability"
                or any(k in f.title.lower() for k in ["injection", "xss", "secret", "hash", "exec", "command", "crypto"])
            ) else "Code Quality"

            action = self._extract_action(f, language)

            prioritized_fixes.append(
                PrioritizedFix(
                    priority=priority_idx,
                    title=f.title,
                    severity=f.severity,
                    line=f.line,
                    category=category,
                    action_required=action,
                )
            )
            priority_idx += 1

        # Generate Executive Overview
        if breakdown.total == 0:
            executive_overview = (
                f"Automated multi-agent inspection of {language.capitalize()} code passed with a perfect score "
                f"of {health_score}/100. No security vulnerabilities or severe code smells detected."
            )
        else:
            executive_overview = (
                f"Automated multi-agent review identified {breakdown.total} issue(s) "
                f"({breakdown.high} High, {breakdown.medium} Medium, {breakdown.low} Low). "
                f"Overall Code Health Score: {health_score}/100. Review verdict: {verdict}."
            )

        # Attempt AI enhancement if LLM client available
        if self.client and breakdown.total > 0:
            try:
                prompt = (
                    f"Write a concise 2-sentence executive summary for a GitHub Pull Request review comment.\n"
                    f"Language: {language}\n"
                    f"Health Score: {health_score}/100\n"
                    f"Issues: {breakdown.high} High, {breakdown.medium} Medium, {breakdown.low} Low\n"
                    f"Top Issues: {', '.join(f.title for f in actionable_findings[:3])}\n"
                    f"Verdict: {verdict}\n"
                    f"Keep it professional and actionable."
                )
                res = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                if res.text and len(res.text.strip()) > 20:
                    executive_overview = res.text.strip()
            except Exception:
                pass

        # Generate Markdown PR Comment
        fix_rows = ""
        for fix in prioritized_fixes[:8]:
            badge = "🔴 High" if fix.severity.lower() == "high" else ("🟡 Medium" if fix.severity.lower() == "medium" else "🟢 Low")
            fix_rows += f"| #{fix.priority} | **{fix.title}** | Line {fix.line} | {badge} | {fix.action_required} |\n"

        markdown_pr = f"""## 🛡️ CodeGuard AI - Pull Request Review Summary

### 📊 Code Health Score: **{health_score}/100** • Verdict: **{verdict}**

> {executive_overview}

---

### 🚨 Severity Breakdown
- 🔴 **High Severity (Critical / Security)**: `{breakdown.high}`
- 🟡 **Medium Severity (Quality / Warnings)**: `{breakdown.medium}`
- 🟢 **Low Severity (Style / Minor)**: `{breakdown.low}`
- 📦 **Total Flagged Findings**: `{breakdown.total}`

---

### 🎯 Prioritized Fix Checklist
| Priority | Issue | Location | Severity | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
{fix_rows if fix_rows else "| - | No issues detected | - | 🟢 Clean | All checks passed! |\n"}

*Generated automatically by CodeGuard Multi-Agent Intelligence System grounded in OWASP Top 10 Standards.*
"""

        return PRSummaryResponse(
            analysis_id=analysis_id,
            verdict=verdict,
            health_score=health_score,
            executive_overview=executive_overview,
            severity_breakdown=breakdown,
            prioritized_fixes=prioritized_fixes,
            markdown_pr_comment=markdown_pr.strip(),
        )


pr_summary_agent = PRSummaryAgent()
