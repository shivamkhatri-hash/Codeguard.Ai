import unittest

from app.schemas.analysis import Finding
from app.services.agents.pr_summary_agent import pr_summary_agent
from app.services.agents.assistant_agent import assistant_agent
from app.services.agents.remediation_agent import remediation_agent


class TestMilestone3Agents(unittest.TestCase):
    def setUp(self):
        self.findings = [
            Finding(
                type="security_vulnerability",
                title="SQL Injection Risk",
                severity="high",
                line=10,
                description="Raw string formatting in SQL query allows injection.",
                recommendation="Use parameterized queries with prepared statements.",
                code_snippet='cursor.execute(f"SELECT * FROM users WHERE name = \'{user}\'")',
            ),
            Finding(
                type="security_vulnerability",
                title="Hardcoded Secret",
                severity="high",
                line=4,
                description="Hardcoded API token detected.",
                recommendation="Store credentials in environment variables.",
                code_snippet='API_KEY = "sk-1234567890"',
            ),
            Finding(
                type="code_smell",
                title="Missing Docstring",
                severity="low",
                line=8,
                description="Function lacks documentation docstring.",
                recommendation="Add descriptive docstring conforming to PEP 257.",
                code_snippet="def get_user(user):",
            ),
        ]

    def test_pr_summary_agent_generation(self):
        summary = pr_summary_agent.generate_summary(
            analysis_id="test1234",
            findings=self.findings,
            code="...",
            language="python",
        )

        self.assertEqual(summary.analysis_id, "test1234")
        self.assertEqual(summary.severity_breakdown.high, 2)
        self.assertEqual(summary.severity_breakdown.low, 1)
        self.assertEqual(summary.severity_breakdown.total, 3)
        self.assertTrue(summary.health_score < 100)
        self.assertIn("Blocked", summary.verdict)
        self.assertTrue(len(summary.prioritized_fixes) >= 3)
        self.assertTrue("#1" in summary.markdown_pr_comment)
        print("[OK] PR Summary Agent Generated PR Review & Health Score:", summary.health_score)

    def test_conversational_code_assistant(self):
        chat_resp = assistant_agent.ask(
            query="How can I prevent SQL injection in Python?",
            language="python",
        )

        self.assertTrue(len(chat_resp.response) > 50)
        self.assertTrue(len(chat_resp.sources) > 0)
        print("[OK] Conversational Assistant Response length:", len(chat_resp.response))
        print("[OK] RAG Citations retrieved:", [s.title for s in chat_resp.sources])

    def test_remediation_agent(self):
        rem_res = remediation_agent.remediate(
            finding=self.findings[0],
            code="...",
            language="python",
        )

        self.assertTrue(bool(rem_res.get("corrected_code")))
        self.assertTrue(bool(rem_res.get("explanation")))
        self.assertTrue(bool(rem_res.get("why_it_works")))
        print("[OK] Remediation Agent generated corrected code:", rem_res.get("corrected_code")[:40], "...")


if __name__ == "__main__":
    unittest.main()
