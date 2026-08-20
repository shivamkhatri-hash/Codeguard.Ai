from typing import Any, Dict, List
import asyncio
import re

from app.schemas.analysis import Finding
from app.services.agents.code_analysis_agent import CodeAnalysisAgent
from app.services.agents.security_vulnerability_agent import SecurityVulnerabilityAgent


class AgentOrchestrator:
    """
    Coordinates the Code Analysis and Security Vulnerability agents.

    Both agents are executed concurrently and their findings are
    combined into a single analysis result.
    """

    def __init__(self):
        self.quality_agent = CodeAnalysisAgent()
        self.security_agent = SecurityVulnerabilityAgent()

    async def _run_quality_agent(
        self,
        code: str,
        language: str,
    ) -> List[Finding]:
        return await asyncio.to_thread(
            self.quality_agent.analyze_code,
            code,
            language,
        )

    async def _run_security_agent(
        self,
        code: str,
        language: str,
    ) -> List[Finding]:
        return await asyncio.to_thread(
            self.security_agent.analyze_code,
            code,
            language,
        )

    def _compute_metrics(
        self,
        code: str,
        language: str,
    ) -> Dict[str, Any]:
        """Compute general software architecture metrics."""

        lines = code.splitlines()

        loc = len([
            line
            for line in lines
            if line.strip()
            and not line.strip().startswith("#")
            and not line.strip().startswith("//")
        ])

        func_count = 0
        class_count = 0
        complexity = 1

        lang = language.lower()

        decision_keywords = {
            "python": [
                r"\bif\b",
                r"\bfor\b",
                r"\bwhile\b",
                r"\bexcept\b",
                r"\band\b",
                r"\bor\b",
            ],
            "java": [
                r"\bif\b",
                r"\bfor\b",
                r"\bwhile\b",
                r"\bcatch\b",
                r"&&",
                r"\|\|",
                r"\bcase\b",
            ],
            "javascript": [
                r"\bif\b",
                r"\bfor\b",
                r"\bwhile\b",
                r"\bcatch\b",
                r"&&",
                r"\|\|",
                r"\bcase\b",
            ],
            "typescript": [
                r"\bif\b",
                r"\bfor\b",
                r"\bwhile\b",
                r"\bcatch\b",
                r"&&",
                r"\|\|",
                r"\bcase\b",
            ],
            "cpp": [
                r"\bif\b",
                r"\bfor\b",
                r"\bwhile\b",
                r"\bcatch\b",
                r"&&",
                r"\|\|",
                r"\bcase\b",
            ],
            "go": [
                r"\bif\b",
                r"\bfor\b",
                r"\bselect\b",
                r"\bcase\b",
                r"&&",
                r"\|\|",
            ],
            "html": [
                r"href=",
                r"onclick=",
            ],
        }

        keywords = decision_keywords.get(lang, [r"\bif\b"])

        for line in lines:
            stripped = line.strip()

            if lang == "python":
                if stripped.startswith("def ") or stripped.startswith("async def "):
                    func_count += 1

                if stripped.startswith("class "):
                    class_count += 1
            else:
                if "class " in stripped and "{" in stripped:
                    class_count += 1

                if (
                    "function " in stripped
                    or (
                        ("public" in stripped or "private" in stripped)
                        and "(" in stripped
                        and ")" in stripped
                        and ";" not in stripped
                    )
                ):
                    func_count += 1

            for keyword in keywords:
                complexity += len(re.findall(keyword, stripped))

        return {
            "lines_of_code": loc,
            "number_of_functions": func_count,
            "number_of_classes": class_count,
            "cyclomatic_complexity": complexity,
        }

    def _deduplicate_findings(
        self,
        findings: List[Finding],
    ) -> List[Finding]:
        """Remove duplicate findings from the combined agent results."""

        unique = []
        seen = set()

        for finding in findings:
            key = (
                finding.type,
                finding.title,
                finding.line,
            )

            if key not in seen:
                seen.add(key)
                unique.append(finding)

        return unique

    async def analyze(
        self,
        code: str,
        language: str,
    ) -> List[Finding]:
        """
        Run both analysis agents concurrently and combine their results.
        """

        lang = language.lower()

        quality_findings, security_findings = await asyncio.gather(
            self._run_quality_agent(code, lang),
            self._run_security_agent(code, lang),
        )

        findings = quality_findings + security_findings

        findings = self._deduplicate_findings(findings)

        findings.sort(key=lambda finding: finding.line)

        metrics = self._compute_metrics(code, lang)
        complexity = metrics["cyclomatic_complexity"]

        if complexity < 10:
            complexity_label = "Low Complexity"
        elif complexity < 20:
            complexity_label = "Moderate Complexity"
        else:
            complexity_label = "High Complexity"

        metric_msg = (
            "Software Code Metrics:\n"
            f"- Non-comment Lines of Code (LOC): {metrics['lines_of_code']}\n"
            f"- Number of Functions: {metrics['number_of_functions']}\n"
            f"- Number of Classes: {metrics['number_of_classes']}\n"
            f"- Cyclomatic Complexity Index: "
            f"{complexity} ({complexity_label})"
        )

        first_line = code.splitlines()[0] if code.splitlines() else ""

        findings.insert(
            0,
            Finding(
                type="code_smell",
                title="Software Architecture Metrics",
                severity="low",
                line=1,
                description=metric_msg,
                recommendation=(
                    "Maintain clean, small functions and keep "
                    "cyclomatic complexity below 10 where practical "
                    "for better readability and maintainability."
                ),
                code_snippet=first_line,
            ),
        )

        return findings


agent_orchestrator = AgentOrchestrator()