from typing import Any, Dict, List
import re

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.analysis import Finding
from app.schemas.remediation import RemediationBatchResponse
from app.services.rag_service import rag_service


class RemediationAgent:
    """
    Generates finding-specific security/code-quality remediation.

    Pipeline:
        Finding -> RAG context -> Gemini -> validation
        Gemini failure/invalid result -> deterministic fallback

    The fallback never invents an unrelated vulnerability and uses
    language-specific remediation patterns for supported findings.
    """

    SUPPORTED_LANGUAGES = {
        "python",
        "java",
        "javascript",
        "typescript",
    }

    def __init__(self):
        self.rag_service = rag_service

        self.client = None
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                self.client = genai.Client(
                    api_key=settings.GEMINI_API_KEY,
                    http_options=types.HttpOptions(
                        timeout=30000,
                        retry_options=types.HttpRetryOptions(
                            attempts=1,
                        ),
                    ),
                )
            except Exception:
                self.client = None

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def _normalize_language(language: str) -> str:
        lang = (language or "").strip().lower()

        aliases = {
            "py": "python",
            "python3": "python",
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
        }

        return aliases.get(lang, lang)

    @staticmethod
    def _contains_placeholder(code: str) -> bool:
        if not code:
            return True

        normalized = code.strip().lower()

        forbidden_exact = {
            "...",
            "todo",
            "pass",
            "your code here",
            "insert code here",
            "add code here",
        }

        if normalized in forbidden_exact:
            return True

        forbidden_patterns = [
            r"\.\.\.",
            r"\btodo\b",
            r"\byour[_ ]code\b",
            r"\binsert[_ ]code\b",
            r"\badd[_ ]code\b",
        ]

        return any(
            re.search(pattern, normalized)
            for pattern in forbidden_patterns
        )

    @staticmethod
    def _has_real_change(original: str, corrected: str) -> bool:
        if not corrected or not corrected.strip():
            return False

        if not original or not original.strip():
            return True

        return corrected.strip() != original.strip()

    @staticmethod
    def _language_guidance(language: str) -> str:
        lang = language.lower()

        if lang == "python":
            return (
                "Python: use parameterized database APIs, "
                "markupsafe/Jinja escaping for HTML output, "
                "os.environ/os.getenv or a secret manager for secrets, "
                "and debug=False in production."
            )

        if lang == "java":
            return (
                "Java: use PreparedStatement/JPA parameter binding for SQL, "
                "contextual HTML escaping, environment variables or a "
                "secret manager for secrets, and disable production debug mode."
            )

        if lang in ("javascript", "typescript"):
            return (
                "JavaScript/TypeScript: use parameterized database APIs, "
                "render untrusted values as text instead of raw HTML, "
                "use process.env or a secret manager for secrets, "
                "and disable development/debug configuration in production."
            )

        return (
            f"Use secure coding practices appropriate for {language}, "
            "and do not introduce unsupported code."
        )

    # ============================================================
    # DETERMINISTIC FALLBACK
    # ============================================================

    def _fallback_remediation(
        self,
        finding: Finding,
        code: str,
        language: str,
    ) -> Dict[str, Any]:

        lang = self._normalize_language(language)

        title = (finding.title or "").lower()
        description = (finding.description or "").lower()
        analysis_recommendation = finding.recommendation or ""

        combined = (
            f"{title} "
            f"{description} "
            f"{analysis_recommendation.lower()}"
        )

        original_code = finding.code_snippet or ""

        recommendation = analysis_recommendation or (
            f"Remediate '{finding.title}' using verified "
            f"{lang} secure-coding practices."
        )

        explanation = finding.description or (
            f"The finding '{finding.title}' requires remediation."
        )

        corrected_code = ""
        why_it_works = ""
        benefits: List[str] = []
        refactoring_suggestions: List[str] = []

        # ========================================================
        # 1. SQL INJECTION
        # ========================================================

        if (
            "sql injection" in combined
            or "sql injection risk" in combined
        ):

            recommendation = (
                "Replace SQL string concatenation or interpolation "
                "with a parameterized query or prepared statement."
            )

            explanation = (
                "The SQL statement incorporates user-controlled data "
                "into the SQL command itself. Parameter binding keeps "
                "data separate from SQL syntax."
            )

            if lang == "python":
                corrected_code = (
                    "cursor.execute(\n"
                    '    "SELECT * FROM users WHERE username = ? '
                    'AND password = ?",\n'
                    "    (username, password)\n"
                    ")"
                )

                why_it_works = (
                    "The database driver receives the SQL structure and "
                    "user values separately, preventing the values from "
                    "being interpreted as SQL syntax."
                )

            elif lang == "java":
                corrected_code = (
                    'String sql = "SELECT * FROM users '
                    'WHERE username = ? AND password = ?";\n'
                    "PreparedStatement stmt = connection.prepareStatement(sql);\n"
                    "stmt.setString(1, username);\n"
                    "stmt.setString(2, password);"
                )

                why_it_works = (
                    "PreparedStatement binds username and password as "
                    "data rather than allowing them to modify SQL syntax."
                )

            elif lang in ("javascript", "typescript"):
                corrected_code = (
                    'const query = "SELECT * FROM users '
                    'WHERE username = $1 AND password = $2";\n'
                    "const result = await db.query(query, [username, password]);"
                )

                why_it_works = (
                    "The PostgreSQL-style parameter placeholders keep "
                    "the user values separate from the SQL command."
                )

            else:
                corrected_code = (
                    "Use the parameterized-query API provided by the "
                    "database driver instead of concatenating user input."
                )

                why_it_works = (
                    "Parameter binding prevents user input from becoming "
                    "part of the SQL syntax."
                )

            benefits = [
                "Prevents SQL injection through user-controlled values.",
                "Separates SQL instructions from application data.",
                "Improves database security.",
            ]

            refactoring_suggestions = [
                "Use prepared statements consistently.",
                "Never concatenate untrusted values into SQL.",
                "Use the parameter syntax supported by the actual database driver.",
                "Add tests containing SQL metacharacters and injection payloads.",
            ]

        # ========================================================
        # 2. XSS
        # ========================================================

        elif (
            "xss" in combined
            or "cross-site scripting" in combined
            or "cross site scripting" in combined
        ):

            recommendation = (
                "Contextually escape untrusted data before rendering it "
                "as HTML. Prefer safe text rendering APIs when HTML is "
                "not required."
            )

            explanation = (
                "User-controlled data is being rendered in an HTML "
                "context without sufficient output encoding. An attacker "
                "could inject executable markup or JavaScript."
            )

            if lang == "python":
                corrected_code = (
                    "from markupsafe import escape\n\n"
                    "safe_value = escape(user_value)"
                )

                why_it_works = (
                    "HTML-sensitive characters are escaped before the "
                    "value is rendered, preventing attacker-controlled "
                    "markup from being interpreted as executable HTML."
                )

            elif lang == "java":
                corrected_code = (
                    "String safeValue = "
                    "org.owasp.encoder.Encode.forHtml(userValue);"
                )

                why_it_works = (
                    "The OWASP encoder converts HTML-sensitive characters "
                    "into safe encoded representations."
                )

            elif lang in ("javascript", "typescript"):
                corrected_code = (
                    "const container = document.createElement('div');\n"
                    "container.textContent = userValue;"
                )

                why_it_works = (
                    "textContent inserts the value as text rather than "
                    "parsing it as HTML."
                )

            else:
                corrected_code = (
                    "Apply context-appropriate HTML output encoding "
                    "before rendering the untrusted value."
                )

                why_it_works = (
                    "Contextual output encoding prevents untrusted input "
                    "from being interpreted as executable markup."
                )

            benefits = [
                "Reduces cross-site scripting risk.",
                "Prevents untrusted HTML from becoming executable markup.",
                "Improves handling of external input.",
            ]

            refactoring_suggestions = [
                "Treat all external input as untrusted.",
                "Prefer text rendering over raw HTML.",
                "Use a trusted framework encoder for HTML contexts.",
                "Avoid disabling framework auto-escaping.",
            ]

        # ========================================================
        # 3. HARDCODED CREDENTIALS
        # ========================================================

        elif (
            "hardcoded" in combined
            or "hard-coded" in combined
            or "hard coded" in combined
            or "hardcoded credential" in combined
            or "hardcoded password" in combined
            or "hardcoded secret" in combined
            or "hardcoded api" in combined
        ):

            recommendation = (
                "Remove credentials and secrets from source code. "
                "Load them from environment configuration or a "
                "dedicated secret-management system."
            )

            explanation = (
                "Secrets embedded in source code can be exposed through "
                "source repositories, logs, builds, backups, or application "
                "packages."
            )

            if lang == "python":
                corrected_code = (
                    "import os\n\n"
                    'username = os.environ["ADMIN_USER"]\n'
                    'password = os.environ["ADMIN_PASS"]'
                )

                why_it_works = (
                    "The credential values are supplied through the "
                    "runtime environment instead of being stored in "
                    "the source code."
                )

            elif lang == "java":
                corrected_code = (
                    'String username = System.getenv("ADMIN_USER");\n'
                    'String password = System.getenv("ADMIN_PASS");'
                )

                why_it_works = (
                    "Java reads the secret values from environment "
                    "configuration rather than embedding them in source."
                )

            elif lang in ("javascript", "typescript"):
                corrected_code = (
                    'const username = process.env.ADMIN_USER;\n'
                    'const password = process.env.ADMIN_PASS;'
                )

                why_it_works = (
                    "The sensitive values are obtained from deployment "
                    "environment variables instead of source code."
                )

            else:
                corrected_code = (
                    "Load credentials from environment configuration "
                    "or a dedicated secret manager."
                )

                why_it_works = (
                    "Secrets are kept outside the application source."
                )

            benefits = [
                "Prevents secrets from being committed to source control.",
                "Makes credential rotation easier.",
                "Reduces accidental secret exposure.",
            ]

            refactoring_suggestions = [
                "Use environment variables for local/demo deployments.",
                "Use a secret manager in production.",
                "Rotate credentials that may already have been exposed.",
                "Add secret scanning to CI/CD.",
            ]

        # ========================================================
        # 4. DEBUG MODE
        # ========================================================

        elif (
            "debug mode" in combined
            or (
                "debug" in combined
                and "production" in combined
            )
        ):

            recommendation = (
                "Disable debug/development mode in production."
            )

            explanation = (
                "Production debug mode can expose stack traces, "
                "configuration information, internal paths, and "
                "other sensitive diagnostic details."
            )

            if lang == "python":
                corrected_code = "app.run(debug=False)"

                why_it_works = (
                    "Flask debug mode is explicitly disabled, preventing "
                    "production users from receiving detailed debugging output."
                )

            elif lang == "java":
                corrected_code = (
                    'String debug = System.getenv("APP_DEBUG");\n'
                    'boolean debugEnabled = "true".equalsIgnoreCase(debug);\n'
                    'if (debugEnabled) {\n'
                    '    throw new IllegalStateException('
                    '"Debug mode must be disabled in production.");\n'
                    '}'
                )

                why_it_works = (
                    "The application refuses to enable the debug behavior "
                    "when the deployment configuration indicates it."
                )

            elif lang in ("javascript", "typescript"):
                corrected_code = (
                    'const isProduction = process.env.NODE_ENV === "production";\n'
                    'const debug = !isProduction;'
                )

                why_it_works = (
                    "Debug behavior is disabled when NODE_ENV identifies "
                    "a production deployment."
                )

            else:
                corrected_code = (
                    "Disable debug/development mode in the production "
                    "deployment configuration."
                )

                why_it_works = (
                    "Production deployments do not expose development "
                    "diagnostic information."
                )

            benefits = [
                "Reduces information disclosure.",
                "Prevents production stack traces from being exposed.",
                "Improves production security.",
            ]

            refactoring_suggestions = [
                "Use separate development and production configuration.",
                "Keep production debug explicitly disabled.",
                "Use controlled application logging.",
            ]

        # ========================================================
        # 5. MISSING DOCSTRING
        # ========================================================

        elif (
            "docstring" in combined
            or "missing documentation" in combined
            or "documentation" in combined
        ):

            recommendation = (
                "Add a meaningful documentation comment or docstring "
                "to the affected function."
            )

            explanation = (
                "The affected function does not contain documentation "
                "describing its purpose and behavior."
            )
            if lang == "python":

                lines = original_code.splitlines()

                if lines and (
                    lines[0].strip().startswith("def ")
                    or lines[0].strip().startswith("async def ")
                ):
                    # Preserve the complete original Python source.
                    corrected_lines = lines[:]

                    # Insert the docstring immediately after the function declaration.
                    corrected_lines.insert(
                        1,
                        '    """'
                    )
                    corrected_lines.insert(
                        2,
                        "    Describe the purpose, parameters, and return value of this function."
                    )
                    corrected_lines.insert(
                        3,
                        '    """'
                    )

                    corrected_code = "\n".join(corrected_lines)

                    why_it_works = (
                        "Python recognizes a string literal immediately "
                        "inside a function as its docstring. The original "
                        "function body and implementation are preserved."
                    )

                else:
                    corrected_code = original_code

                    why_it_works = (
                        "The supplied Python source does not provide a "
                        "safe function declaration location for automatic "
                        "docstring insertion, so the original source is "
                        "preserved rather than inventing code."
                    )

            elif lang == "java":

                # Preserve the supplied Java source and add Javadoc
                # immediately before the affected declaration.
                lines = original_code.splitlines()

                if lines:
                    insertion_index = 0

                    # If the source begins with a public class declaration,
                    # document the class itself.
                    for index, line in enumerate(lines):
                        stripped = line.strip()

                        if (
                            stripped.startswith("public class ")
                            or stripped.startswith("class ")
                        ):
                            insertion_index = index
                            break

                    javadoc = [
                        "/**",
                        " * Describes the purpose and behavior of this declaration.",
                        " */",
                    ]

                    corrected_lines = (
                        lines[:insertion_index]
                        + javadoc
                        + lines[insertion_index:]
                    )

                    corrected_code = "\n".join(corrected_lines)

                    why_it_works = (
                        "Java uses Javadoc comments placed immediately "
                        "before classes and methods for documentation. "
                        "The supplied Java source is preserved."
                    )

                else:
                    corrected_code = original_code

                    why_it_works = (
                        "The supplied Java source is empty, so no "
                        "documentation code is fabricated."
                    )

            elif lang in ("javascript", "typescript"):

                # Preserve the supplied source and add a JSDoc/TypeDoc
                # comment before the affected declaration.
                lines = original_code.splitlines()

                if lines:
                    insertion_index = 0

                    for index, line in enumerate(lines):
                        stripped = line.strip()

                        if (
                            stripped.startswith("function ")
                            or stripped.startswith("async function ")
                            or stripped.startswith("export function ")
                            or stripped.startswith("const ")
                            or stripped.startswith("let ")
                        ):
                            insertion_index = index
                            break

                    jsdoc = [
                        "/**",
                        " * Describes the purpose and behavior of this function.",
                        " */",
                    ]

                    corrected_lines = (
                        lines[:insertion_index]
                        + jsdoc
                        + lines[insertion_index:]
                    )

                    corrected_code = "\n".join(corrected_lines)

                    why_it_works = (
                        "JSDoc and TypeDoc comments document JavaScript "
                        "and TypeScript declarations. The original source "
                        "is preserved instead of replacing it with a "
                        "placeholder function."
                    )

                else:
                    corrected_code = original_code

                    why_it_works = (
                        "The supplied source is empty, so no fabricated "
                        "function is generated."
                    )

            else:

                corrected_code = original_code

                why_it_works = (
                    "The language is not supported by the deterministic "
                    "documentation remediation rules, so the original "
                    "source is preserved rather than generating "
                    "placeholder code."
                )

            benefits = [
                "Improves readability.",
                "Improves maintainability.",
                "Makes function behavior easier to understand.",
                "Supports documentation tooling.",
            ]

            refactoring_suggestions = [
                "Document public functions and methods.",
                "Document parameters and return values when appropriate.",
                "Keep documentation focused on behavior.",
            ]
        # ========================================================
        # 6. SOFTWARE ARCHITECTURE METRICS
        # ========================================================

        elif "software architecture metrics" in title:

            recommendation = (
                "Review the reported architecture metrics and refactor "
                "only the specific structural issues identified by the analyzer."
            )

            explanation = (
                "Architecture metrics summarize properties such as lines of "
                "code, function count, class count, and complexity. The metrics "
                "finding itself does not identify a specific source-level defect."
            )

            corrected_code = original_code

            why_it_works = (
                "No fabricated source transformation is claimed because the "
                "finding is a metrics summary rather than a specific code defect."
            )

            benefits = [
                "Avoids fabricated corrections.",
                "Preserves the original source context.",
                "Separates metrics reporting from source-level remediation.",
            ]

            refactoring_suggestions = [
                "Review functions with elevated complexity.",
                "Reduce unnecessary nesting where appropriate.",
                "Split large responsibilities into focused functions.",
                "Run tests after structural refactoring.",
            ]

        # ========================================================
        # 6. EXCESSIVE COMPLEXITY / NESTING
        # ========================================================

        elif (
            "software architecture metrics" not in title
            and (
                "excessive nesting" in combined
                or "nesting complexity" in combined
                or "cyclomatic complexity" in combined
                or "high complexity" in combined
            )
        ):

            recommendation = (
                "Reduce unnecessary nesting using guard clauses and "
                "extract independent logic into focused functions."
            )

            explanation = (
                "Deeply nested control flow increases cognitive load "
                "and makes the code harder to test and maintain."
            )

            # We only perform an automatic transformation when the
            # supplied source clearly contains nested Python if blocks.
            if lang == "python" and original_code.strip():

                lines = original_code.splitlines()

                conditions = []

                for line in lines[1:]:
                    stripped = line.strip()

                    if stripped.startswith("if ") and stripped.endswith(":"):
                        condition = stripped[3:-1].strip()
                        conditions.append(condition)

                body_lines = [
                    line.strip()
                    for line in lines[1:]
                    if line.strip()
                    and not line.strip().startswith("if ")
                ]

                # Only automatically refactor a simple nested-if chain.
                if len(conditions) >= 3 and body_lines:

                    combined_condition = " or ".join(
                        f"not ({condition})"
                        for condition in conditions
                    )

                    corrected_lines = [
                        lines[0],
                        f"    if {combined_condition}:",
                        "        return",
                    ]

                    for body in body_lines:
                        corrected_lines.append(
                            f"    {body}"
                        )

                    corrected_code = "\n".join(corrected_lines)

                    why_it_works = (
                        "The nested conditions are converted into a guard "
                        "clause. When any required condition fails, the "
                        "function returns immediately, removing deep "
                        "nesting while preserving the successful path."
                    )

                else:

                    corrected_code = (
                        "Refactor the affected nested logic into smaller "
                        "single-responsibility functions and use guard "
                        "clauses where appropriate."
                    )

                    why_it_works = (

                        "Guard clauses and smaller functions reduce "
                        "control-flow nesting and make the code easier "
                        "to understand and test."
                    )

            else:

                corrected_code = (
                    "Refactor the affected logic into smaller "
                    "single-responsibility functions and reduce "
                    "unnecessary nesting."
                )

                why_it_works = (
                    "Smaller responsibilities and flatter control flow "
                    "make the code easier to understand and test."
                )

            benefits = [
                "Improves maintainability.",
                "Makes testing easier.",
                "Reduces cognitive complexity.",
                "Reduces regression risk.",
            ]

            refactoring_suggestions = [
                "Use guard clauses.",
                "Extract independent logic into functions.",
                "Keep functions focused on one responsibility.",
                "Add tests before major refactoring.",
            ]

        # ========================================================
        # 7. UNKNOWN FINDING
        # ========================================================

        else:

            recommendation = analysis_recommendation or (
                f"No verified automatic remediation rule exists for "
                f"'{finding.title}'. Review the finding against the "
                f"source code before making a change."
            )

            explanation = finding.description or (
                "The finding does not match a verified remediation rule."
            )

            # IMPORTANT:
            # We do NOT fabricate a code correction for unknown findings.
            corrected_code = original_code

            why_it_works = (
                "No unsupported source transformation is claimed because "
                "the finding is outside the verified remediation rules."
            )

            benefits = [
                "Avoids introducing unrelated changes.",
                "Prevents fabricated fixes.",
                "Preserves the supplied source context.",
            ]

            refactoring_suggestions = [
                "Review the exact source location.",
                "Confirm the finding with an appropriate static-analysis rule.",
                "Apply a verified language-specific fix.",
                "Run tests after remediation.",
            ]

        # ========================================================
        # FINAL SAFETY CHECK
        # ========================================================

        # A known rule must not silently return its unchanged source
        # as if it were a successful correction.
        known_finding = any(
            keyword in combined
            for keyword in (
                "sql injection",
                "xss",
                "cross-site scripting",
                "cross site scripting",
                "hardcoded",
                "hard-coded",
                "debug mode",
                "missing docstring",
                "docstring",
                "documentation",
                "excessive nesting",
                "nesting complexity",
                "cyclomatic complexity",
                "complexity",
            )
        )

        if known_finding and (
            not corrected_code.strip()
            or self._contains_placeholder(corrected_code)
        ):
            corrected_code = (
                "Automatic correction could not be generated safely "
                "from the supplied source context. Apply the finding-"
                "specific recommendation and review the affected code."
            )

        return {
            "finding_title": finding.title,
            "severity": finding.severity,
            "line": finding.line,
            "language": language,
            "status": "fallback",
            "recommendation": recommendation,
            "explanation": explanation,
            "original_code": original_code,
            "corrected_code": corrected_code,
            "why_it_works": why_it_works,
            "benefits": benefits,
            "refactoring_suggestions": refactoring_suggestions,
            "secure_guidance": self._language_guidance(lang),
            "references": [
                "Project secure-coding RAG knowledge base",
            ],
        }

    # ============================================================
    # GEMINI BATCH REMEDIATION
    # ============================================================

    def remediate_batch(
        self,
        findings: List[Finding],
        code: str,
        language: str,
    ) -> List[Dict[str, Any]]:

        if not findings:
            return []

        lang = self._normalize_language(language)

        finding_sections = []

        for index, finding in enumerate(findings):

            rag_results = self.rag_service.query(
                query_text=(
                    f"{finding.title} "
                    f"{finding.description} "
                    f"{finding.recommendation}"
                ),
                language=lang,
                top_k=3,
            )

            rag_guidance = "\n\n".join(
                [
                    (
                        f"Title: {result.get('title', '')}\n"
                        f"Category: {result.get('category', '')}\n"
                        f"Guidance: {result.get('content', '')}"
                    )
                    for result in rag_results
                ]
            )

            if not rag_guidance:
                rag_guidance = (
                    "No matching RAG guidance was found. "
                    "Use verified language-specific secure coding practices."
                )

            finding_sections.append(
                f"""
========================
FINDING {index + 1}
========================

Title:
{finding.title}

Type:
{finding.type}

Severity:
{finding.severity}

Line:
{finding.line}

Description:
{finding.description}

Vulnerable Code:
{finding.code_snippet or ""}

Recommendation:
{finding.recommendation}

RAG Guidance:
{rag_guidance}
"""
            )

        all_findings = "\n".join(finding_sections)

        prompt = f"""
You are a senior software security engineer.

Generate exactly one remediation for every supplied finding.

Programming language:
{lang}

Full source code:
{code}

Findings:
{all_findings}

For every finding provide:

- recommendation
- explanation
- original_code
- corrected_code
- why_it_works
- benefits
- refactoring_suggestions
- secure_guidance
- references

STRICT RULES:

1. Return exactly one remediation per finding.
2. Preserve the original finding order.
3. Match each remediation ONLY to its corresponding finding.
4. original_code must come from the supplied source.
5. corrected_code must be an actual correction of original_code or
   the smallest safe corrected code supported by the supplied source.
6. Do not invent unrelated code.
7. Do not invent variables, APIs, database libraries, frameworks,
   functions, or surrounding application architecture unless they are
   clearly required and identified as an example.
8. Do not return TODO.
9. Do not return "...".
10. Do not return placeholder comments such as "add code here".
11. Do not return the unchanged vulnerable code as corrected_code.
12. Preserve intended functionality.
13. Use syntax appropriate for {lang}.
14. SQL Injection:
    use parameterized queries/prepared statements appropriate to the
    language/database API shown in the source.
15. XSS:
    use contextual output encoding or safe text rendering appropriate
    to the framework actually shown in the source.
16. Hardcoded credentials:
    move secrets to environment/secret management using the language's
    actual configuration mechanism.
17. Debug mode:
    explicitly disable production debug mode using the framework/config
    shown in the source.
18. Missing documentation:
    add documentation appropriate to the language without changing
    program behavior.
19. Complexity:
    make a real, behavior-preserving refactoring only when enough
    source context is available.
20. If there is insufficient context for a safe automatic rewrite,
    provide the smallest source-supported correction rather than
    fabricating surrounding code.
21. secure_guidance must match the actual finding.
22. Never copy unrelated RAG guidance.
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config={
                    "temperature": 0.1,
                    "response_mime_type": "application/json",
                    "response_schema": RemediationBatchResponse,
                },
            )

            batch_response = (
                RemediationBatchResponse.model_validate_json(
                    response.text
                )
            )

            if len(batch_response.remediations) != len(findings):
                raise ValueError(
                    "Gemini returned an incorrect number of remediations."
                )

            results = []

            for finding, remediation in zip(
                findings,
                batch_response.remediations,
            ):

                result = remediation.model_dump()

                result["finding_title"] = finding.title
                result["severity"] = finding.severity
                result["line"] = finding.line
                result["language"] = lang
                result["status"] = "generated"

                original = finding.code_snippet or ""
                corrected = result.get("corrected_code", "")

                # -----------------------------
                # Validate generated correction
                # -----------------------------

                if not corrected or not corrected.strip():
                    raise ValueError(
                        f"Empty corrected_code for '{finding.title}'."
                    )

                if self._contains_placeholder(corrected):
                    raise ValueError(
                        f"Placeholder corrected_code for '{finding.title}'."
                    )

                # If Gemini simply copied the vulnerable snippet,
                # don't accept it as a correction.
                if original.strip() and not self._has_real_change(
                    original,
                    corrected,
                ):
                    raise ValueError(
                        f"Gemini returned unchanged code for "
                        f"'{finding.title}'."
                    )

                # Make sure the remediation remains tied to the finding.
                generated_text = (
                    f"{result.get('recommendation', '')} "
                    f"{result.get('explanation', '')} "
                    f"{result.get('secure_guidance', '')}"
                ).lower()

                title_words = [
                    word
                    for word in re.findall(
                        r"[a-zA-Z]+",
                        finding.title.lower(),
                    )
                    if len(word) > 3
                ]

                if title_words and not any(
                    word in generated_text
                    for word in title_words
                ):
                    raise ValueError(
                        f"Generated remediation appears unrelated to "
                        f"finding '{finding.title}'."
                    )

                results.append(result)

            return results

        except Exception:
            return [
                self._fallback_remediation(
                    finding=finding,
                    code=code,
                    language=lang,
                )
                for finding in findings
            ]

    # ============================================================
    # SINGLE FINDING
    # ============================================================

    def remediate(
        self,
        finding: Finding,
        code: str,
        language: str,
    ) -> Dict[str, Any]:

        results = self.remediate_batch(
            findings=[finding],
            code=code,
            language=language,
        )

        if not results:
            raise ValueError("No remediation was generated.")

        return results[0]


# Shared backend instance.
remediation_agent = RemediationAgent()