from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.assistant import ChatMessage, ChatResponse, RAGSource
from app.services.rag_service import rag_service
from app.services.storage_service import storage_service


class ConversationalAssistantAgent:
    """
    RAG-powered conversational assistant for developer Q&A, follow-up queries
    on flagged vulnerabilities, and secure coding guidance grounded in the knowledge base.
    """

    def __init__(self):
        self.rag_service = rag_service
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
    def _clean_recommendation(rec: str, language: str) -> str:
        if not rec:
            return ""
        lang_lower = (language or "python").lower()
        lines = rec.split("\n")
        cleaned_lines = []
        for line in lines:
            trimmed = line.strip()
            # If line mentions another specific language prefix (e.g. "For Java:"), filter it out unless it matches lang_lower
            if trimmed.startswith("For ") and ":" in trimmed:
                prefix_lang = trimmed[4:trimmed.index(":")].strip().lower()
                if prefix_lang != lang_lower and lang_lower not in prefix_lang:
                    continue
            cleaned_lines.append(line)
        result = "\n".join(cleaned_lines).strip()
        # Truncate if excessively long
        if len(result) > 300:
            result = result[:300] + "..."
        return result

    @staticmethod
    def _extract_variable_name(description: str, title: str, line: Any, code_snippet: Optional[str] = None) -> str:
        import re
        blacklist = {"or", "and", "in", "is", "not", "key", "secret", "variable", "field", "password", "credential", "token", "a", "an", "the", "var"}

        # 1. Inspect actual line in code snippet if provided
        if code_snippet and str(line).isdigit():
            line_idx = int(line)
            lines = code_snippet.splitlines()
            if 1 <= line_idx <= len(lines):
                target_line = lines[line_idx - 1].strip()
                assign_match = re.search(r"([A-Za-z_][A-Za-z0-9_.]*)\s*=", target_line)
                if assign_match:
                    cand = assign_match.group(1).strip()
                    if cand.lower() not in blacklist:
                        return cand

        # 2. Inspect description for quoted names like 'DB_PASSWORD' or 'app.secret_key'
        quoted = re.findall(r"['\"]([A-Za-z_][A-Za-z0-9_.]*)['\"]", description)
        for cand in quoted:
            if cand.lower() not in blacklist and len(cand) > 1:
                return cand

        # 3. Match 'variable DB_PASSWORD' or 'field DB_PASSWORD'
        match = re.search(r"(?:variable|field|constant|property|key|secret)\s+(['\"]?)([A-Za-z_][A-Za-z0-9_.]*)\1", description, re.IGNORECASE)
        if match:
            cand = match.group(2).strip()
            if cand.lower() not in blacklist:
                return cand

        return "SECRET_KEY"

    @staticmethod
    def _generate_code_fix_snippet(title: str, description: str, language: str, line: Any, code_snippet: Optional[str] = None) -> str:
        import re
        lang = (language or "python").lower()
        title_lower = (title or "").lower()
        desc_lower = (description or "").lower()

        # Comment syntax helper
        comment_prefix = "#" if lang == "python" else "<!--" if lang in ["html", "xml"] else "//"
        comment_suffix = " -->" if lang in ["html", "xml"] else ""

        # Extract variable name cleanly
        v_name = ConversationalAssistantAgent._extract_variable_name(description, title, line, code_snippet)

        # 1. Hardcoded Secrets
        if "secret" in title_lower or "credential" in title_lower or "hardcoded" in title_lower:
            if v_name == "app.secret_key" or "secret_key" in v_name.lower():
                if lang == "python":
                    return (
                        f"```python\n"
                        f"# Line {line} Fix: Load 'app.secret_key' from Environment Variable (Ensure 'import os' is at top of file)\n"
                        f"app.secret_key = os.getenv('FLASK_SECRET_KEY', os.getenv('SECRET_KEY'))\n"
                        f"```"
                    )
            if lang == "java":
                return (
                    f"```java\n"
                    f"// Line {line} Fix: Load '{v_name}' from Environment Variable\n"
                    f"public static final String {v_name} = System.getenv(\"{v_name}\");\n"
                    f"```"
                )
            elif lang == "python":
                return (
                    f"```python\n"
                    f"# Line {line} Fix: Load '{v_name}' from Environment Variable (Ensure 'import os' is at top of file)\n"
                    f"{v_name} = os.getenv('{v_name}')\n"
                    f"```"
                )
            else:
                return (
                    f"```javascript\n"
                    f"// Line {line} Fix: Load '{v_name}' from environment variable\n"
                    f"const {v_name} = process.env.{v_name};\n"
                    f"```"
                )

        # 2. Command Injection
        if "command" in title_lower or "command injection" in desc_lower or "subprocess" in desc_lower or "os.system" in desc_lower or "exec" in desc_lower:
            if lang == "java":
                return (
                    f"```java\n"
                    f"// Line {line} Fix: Use ProcessBuilder with argument list (avoid shell execution)\n"
                    f"ProcessBuilder pb = new ProcessBuilder(\"safe_cmd\", untrustedInput);\n"
                    f"Process process = pb.start();\n"
                    f"```"
                )
            elif lang == "python":
                return (
                    f"```python\n"
                    f"# Line {line} Fix: Use subprocess.run with argument list (avoid os.system / shell=True)\n"
                    f"import subprocess\n"
                    f"subprocess.run([\"safe_cmd\", untrusted_input], check=True)\n"
                    f"```"
                )
            else:
                return (
                    f"```javascript\n"
                    f"// Line {line} Fix: Use execFile with argument array\n"
                    f"const {{ execFile }} = require('child_process');\n"
                    f"execFile('safe_cmd', [untrustedInput], (err, stdout) => {{ ... }});\n"
                    f"```"
                )

        # 3. Insecure Deserialization
        if "deserialization" in title_lower or "pickle" in desc_lower or "yaml" in desc_lower or "unserialize" in desc_lower:
            if lang == "java":
                return (
                    f"```java\n"
                    f"// Line {line} Fix: Replace Java serialization with safe Jackson JSON parsing\n"
                    f"ObjectMapper mapper = new ObjectMapper();\n"
                    f"MyData data = mapper.readValue(jsonString, MyData.class);\n"
                    f"```"
                )
            elif lang == "python":
                return (
                    f"```python\n"
                    f"# Line {line} Fix: Replace pickle.load() with safe json.loads() or Pydantic\n"
                    f"import json\n"
                    f"data = json.loads(untrusted_json_string)\n"
                    f"```"
                )
            else:
                return (
                    f"```javascript\n"
                    f"// Line {line} Fix: Use JSON.parse() instead of eval() or unsafe deserialization\n"
                    f"const data = JSON.parse(untrustedString);\n"
                    f"```"
                )

        # 4. SQL Injection
        if "sql injection" in title_lower or "sql injection" in desc_lower or "query" in title_lower:
            if lang == "java":
                return (
                    f"```java\n"
                    f"// Line {line} Fix: Parameterized PreparedStatement\n"
                    f"String query = \"SELECT * FROM table WHERE column = ?\";\n"
                    f"try (PreparedStatement pstmt = conn.prepareStatement(query)) {{\n"
                    f"    pstmt.setString(1, untrustedInput);\n"
                    f"    ResultSet rs = pstmt.executeQuery();\n"
                    f"}}\n"
                    f"```"
                )
            elif lang == "python":
                return (
                    f"```python\n"
                    f"# Line {line} Fix: Parameterized DB-API Query\n"
                    f"query = \"SELECT * FROM table WHERE column = %s\"\n"
                    f"cursor.execute(query, (untrusted_input,))\n"
                    f"```"
                )
            else:
                return (
                    f"```javascript\n"
                    f"// Line {line} Fix: Parameterized Query\n"
                    f"const query = 'SELECT * FROM table WHERE column = ?';\n"
                    f"const [results] = await db.execute(query, [untrustedInput]);\n"
                    f"```"
                )

        # 5. Weak Hashing / Cryptography
        if "hash" in title_lower or "md5" in desc_lower or "sha1" in desc_lower or "cryptographic" in title_lower:
            if lang == "java":
                return (
                    f"```java\n"
                    f"// Line {line} Fix: Use SHA-256 or bcrypt instead of weak MD5/SHA-1\n"
                    f"MessageDigest md = MessageDigest.getInstance(\"SHA-256\");\n"
                    f"byte[] digest = md.digest(dataBytes);\n"
                    f"```"
                )
            elif lang == "python":
                return (
                    f"```python\n"
                    f"# Line {line} Fix: Use hashlib.sha256() instead of MD5/SHA1\n"
                    f"import hashlib\n"
                    f"secure_hash = hashlib.sha256(data_bytes).hexdigest()\n"
                    f"```"
                )
            else:
                return (
                    f"```javascript\n"
                    f"// Line {line} Fix: Use crypto module with SHA-256\n"
                    f"const crypto = require('crypto');\n"
                    f"const hash = crypto.createHash('sha256').update(data).digest('hex');\n"
                    f"```"
                )

        # 6. Docstrings / Documentation
        if "docstring" in title_lower or "javadoc" in title_lower or "documentation" in title_lower:
            if lang == "java":
                return (
                    f"```java\n"
                    f"/**\n"
                    f" * Documentation for Line {line} component.\n"
                    f" */\n"
                    f"```"
                )
            else:
                return (
                    f"```python\n"
                    f"\"\"\"\n"
                    f"Documentation for Line {line} function.\n"
                    f"\"\"\"\n"
                    f"```"
                )

        # 7. XSS
        if "xss" in title_lower or "cross-site" in desc_lower:
            return (
                f"```html\n"
                f"<!-- Line {line} Fix: Contextual Sanitization -->\n"
                f"<div><%= sanitizeHtml(userInput) %></div>\n"
                f"```"
            )

        return (
            f"```{lang}\n"
            f"{comment_prefix} Line {line} Secure Refactored Code Fix{comment_suffix}\n"
            f"```"
        )

    def ask(
        self,
        query: str,
        analysis_id: Optional[str] = None,
        language: str = "python",
        history: Optional[List[ChatMessage]] = None,
    ) -> ChatResponse:
        """
        Answers developer follow-up queries using RAG context and optional LLM.
        """
        display_lang = {
            "python": "Python",
            "java": "Java",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "cpp": "C++",
            "go": "Go",
            "html": "HTML",
        }.get((language or "").lower(), (language or "multi-language").capitalize())

        # Step 0: Friendly greeting handler
        cleaned_lower = query.strip().lower().rstrip("!?.")
        if cleaned_lower in ["hi", "hii", "hiii", "hiiii", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "help"]:
            greeting_msg = (
                f"Hello! 👋 I am your **CodeGuard AI Assistant**, specializing in **{display_lang}** (and Python, Java, JS, TS, C++, Go, HTML) code quality and OWASP security.\n\n"
                f"Feel free to ask me anything about your code, or try one of these questions:\n"
                f"- *\"How can I prevent SQL injection in my code?\"*\n"
                f"- *\"Why are hardcoded secrets dangerous and how do I use environment variables?\"*\n"
                f"- *\"How do I refactor code for better maintainability?\"*\n"
                f"- *\"Explain the security vulnerabilities found in this file.\"*\n\n"
                f"What would you like to inspect or improve?"
            )
            return ChatResponse(
                response=greeting_msg,
                sources=[],
            )

        # Step 0.5: Off-topic guardrail check
        query_lower = query.strip().lower()
        off_topic_keywords = [
            "capital of", "capital", "weather", "temperature", "president",
            "prime minister", "cricket", "football", "recipe", "movie", "song", "joke"
        ]
        if any(keyword in query_lower for keyword in off_topic_keywords):
            fallback_text = (
                f"I am your **CodeGuard AI Assistant**, specialized in multi-language code quality (**Python, Java, JavaScript, TypeScript, C++, Go, HTML**) and OWASP security analysis.\n\n"
                f"I don't answer general trivia or off-topic questions (like geography or weather). Feel free to ask me anything about:\n"
                f"- **Vulnerability Remediation** (e.g. *\"How do I fix SQL injection in {display_lang}?\"*)\n"
                f"- **Code Refactoring & Quality** (e.g. *\"How do I improve this code?\"*)\n"
                f"- **OWASP Security Guidelines** (e.g. *\"How do I store API keys safely?\"*)"
            )
            return ChatResponse(response=fallback_text, sources=[])

        # Step 1: Fetch RAG context
        rag_results = self.rag_service.query(
            query_text=query,
            language=language,
            top_k=3,
        )

        rag_sources = [
            RAGSource(
                title=doc.get("title", "Secure Coding Guideline"),
                category=doc.get("category", "General"),
                score=round(float(doc.get("score", 0.0)), 3),
                snippet=doc.get("content", "")[:250] + "...",
            )
            for doc in rag_results
        ]

        # Step 2: Fetch analysis context if ID is provided
        analysis_context = ""
        if analysis_id:
            analysis_data = storage_service.get_analysis(analysis_id)
            if analysis_data:
                code_snippet = analysis_data.get("code", "")[:1000]
                findings_list = analysis_data.get("findings", []) or []
                findings_str = "\n".join([
                    f"- Line {f.get('line')}: [{f.get('severity')}] {f.get('title')} - {f.get('description')}"
                    for f in findings_list[:5]
                ])
                analysis_context = f"\nAnalyzed Code:\n```\n{code_snippet}\n```\nDetected Findings:\n{findings_str}\n"

        rag_context_text = "\n\n".join([
            f"### {doc['title']} ({doc['category']})\n{doc['content']}"
            for doc in rag_results
        ])

        # Step 3: LLM Generation if available
        if self.client:
            try:
                system_prompt = (
                    f"You are an expert secure coding mentor and AI code review assistant named CodeGuard AI Assistant.\n"
                    f"You specialize strictly in programming, code quality, software architecture, and OWASP security vulnerability analysis.\n"
                    f"Supported languages: Python, Java, JavaScript, TypeScript, C++, Go, HTML. Current Language Context: {display_lang}\n\n"
                    f"Relevant Knowledge Base Guidelines:\n{rag_context_text}\n"
                    f"{analysis_context}\n"
                    f"Instructions:\n"
                    f"1. For programming, code quality, refactoring, or security questions: Provide a clear, expert, well-explained answer with code snippets where helpful.\n"
                    f"2. For any off-topic general knowledge or trivia questions (such as geography, weather, sports, general history, or 'capital of India'): Politely state that you are specialized exclusively in code quality and security analysis, and invite the user to ask any questions regarding code review, OWASP vulnerability remediation, or secure coding guidelines for {display_lang}."
                )

                history_turns = []
                if history:
                    for msg in history[-4:]:
                        role_label = "User" if msg.role == "user" else "Assistant"
                        history_turns.append(f"{role_label}: {msg.content}")

                history_prompt = "\n".join(history_turns)
                full_prompt = f"{system_prompt}\n\n{history_prompt}\nUser: {query}\nAssistant:"

                response = self.client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=full_prompt,
                )
                if response.text and response.text.strip():
                    return ChatResponse(
                        response=response.text.strip(),
                        sources=rag_sources,
                    )
            except Exception:
                pass

        # Step 4: Fallback deterministic guidance grounded in RAG KB & Active Analysis
        query_lower = query.lower()

        # Off-topic guardrail check
        off_topic_keywords = [
            "capital of", "capital", "weather", "temperature", "president",
            "prime minister", "cricket", "football", "recipe", "movie", "song", "joke"
        ]
        if any(keyword in query_lower for keyword in off_topic_keywords):
            fallback_text = (
                f"I am your **CodeGuard AI Assistant**, specialized in multi-language code quality (**Python, Java, JavaScript, TypeScript, C++, Go, HTML**) and OWASP security analysis.\n\n"
                f"I don't answer general trivia or off-topic questions (like geography or weather). Feel free to ask me anything about:\n"
                f"- **Vulnerability Remediation** (e.g. *\"How do I fix SQL injection in {display_lang}?\"*)\n"
                f"- **Code Refactoring & Quality** (e.g. *\"How do I improve this code?\"*)\n"
                f"- **OWASP Security Guidelines** (e.g. *\"How do I store API keys safely?\"*)"
            )
            return ChatResponse(response=fallback_text, sources=[])

        # Active Analysis Findings & Diagnostics Query Handler
        if analysis_id:
            analysis_data = storage_service.get_analysis(analysis_id)
            if analysis_data:
                findings_list = analysis_data.get("findings", []) or []
                actionable = [f for f in findings_list if f.get("title") != "Software Architecture Metrics"]
                total_findings = len(actionable)
                high_count = sum(1 for f in actionable if str(f.get("severity", "")).lower() == "high")
                med_count = sum(1 for f in actionable if str(f.get("severity", "")).lower() == "medium")
                low_count = sum(1 for f in actionable if str(f.get("severity", "")).lower() == "low")
                filename = analysis_data.get("filename") or (f"code.{language}")

                # Sort actionable findings by severity weight (High -> Medium -> Low)
                severity_order = {"high": 1, "critical": 1, "medium": 2, "low": 3}
                sorted_actionable = sorted(
                    actionable,
                    key=lambda x: severity_order.get(str(x.get("severity", "")).lower(), 4)
                )

                # Query type A: "how many findings", "total issues", "count"
                if any(k in query_lower for k in ["how many", "count", "number of", "how many findings", "total findings", "findings found", "many findings"]):
                    fallback_text = (
                        f"### 🛡️ **Scan Findings Summary for `{filename}`** (ID: `{analysis_id}`)\n\n"
                        f"We detected **{total_findings} total findings** in your scanned code:\n"
                        f"- 🚨 **High Severity**: {high_count}\n"
                        f"- ⚠️ **Medium Severity**: {med_count}\n"
                        f"- 🔍 **Low / Code Smells**: {low_count}\n\n"
                    )
                    if total_findings > 0:
                        fallback_text += "#### **Top Prioritized Findings List**:\n"
                        for idx, f in enumerate(sorted_actionable[:5], 1):
                            line = f.get("line", "?")
                            sev = (f.get("severity") or "low").upper()
                            title = f.get("title", "Issue")
                            desc = f.get("description", "")
                            fallback_text += f"{idx}. **Line {line} [{sev}] - {title}**: {desc}\n"
                        fallback_text += "\n💡 *Tip*: You can view side-by-side refactored code fixes in the **AI Remediation Roadmap** tab!"
                    else:
                        fallback_text += "🎉 Great news! No vulnerabilities or code smells were flagged in this submission."

                    return ChatResponse(response=fallback_text, sources=rag_sources)

                # Query type B: Comparative risk analysis ("which one", "highest risk", "which is worse", "between", "highest risk in this program")
                is_comparative = any(k in query_lower for k in [
                    "highest risk", "most critical", "which one", "which issue", "which vulnerability",
                    "only one answer", "compare", "which is worse", "poses the highest risk", "highest severity vulnerability"
                ])

                if is_comparative:
                    cmd_inj = next((f for f in sorted_actionable if "command" in f.get("title","").lower() or "subprocess" in f.get("description","").lower() or "os.system" in f.get("description","").lower()), None)
                    deserialization = next((f for f in sorted_actionable if "deserialization" in f.get("title","").lower() or "pickle" in f.get("description","").lower()), None)
                    sql_inj = next((f for f in sorted_actionable if "sql" in f.get("title","").lower()), None)

                    if cmd_inj:
                        top_v = cmd_inj
                        v_name = "Command Injection"
                        reasoning = (
                            f"User-controlled input is passed directly to system shell execution (`{top_v.get('description', 'os.system')}`) on **Line {top_v.get('line', '?')}**. "
                            f"This allows an attacker to execute arbitrary operating system commands with full host application privileges, resulting in complete server compromise (Remote Code Execution)."
                        )
                    elif deserialization:
                        top_v = deserialization
                        v_name = "Insecure Deserialization"
                        reasoning = (
                            f"Untrusted serialized byte streams are loaded (`{top_v.get('description', 'pickle.load')}`) on **Line {top_v.get('line', '?')}**. "
                            f"This allows an attacker to instantiate arbitrary objects and execute Remote Code Execution (RCE) on the server."
                        )
                    elif sql_inj:
                        top_v = sql_inj
                        v_name = "SQL Injection"
                        reasoning = (
                            f"Untrusted input is directly concatenated into SQL query strings on **Line {top_v.get('line', '?')}**. "
                            f"This allows attackers to manipulate database queries, extract sensitive tables, or tamper with database records."
                        )
                    elif sorted_actionable:
                        top_v = sorted_actionable[0]
                        v_name = top_v.get("title", "High Severity Vulnerability")
                        reasoning = f"It presents the highest severity impact ({top_v.get('severity', 'HIGH').upper()}) on **Line {top_v.get('line', '?')}**: {top_v.get('description', '')}"
                    else:
                        top_v = None

                    if top_v:
                        code_fix = self._generate_code_fix_snippet(top_v.get("title", ""), top_v.get("description", ""), language, top_v.get("line", "?"))
                        fallback_text = (
                            f"### 🛡️ **Highest Risk Vulnerability Analysis for `{filename}`**\n\n"
                            f"**Single Answer**: **{v_name}** (Line {top_v.get('line', '?')} • `{top_v.get('severity', 'HIGH').upper()}`)\n\n"
                            f"#### **Why {v_name} Poses the Highest Risk**:\n"
                            f"{reasoning}\n\n"
                            f"Unlike lower-impact findings (such as database queries, weak hashing, or missing documentation), **{v_name}** grants an attacker direct **Remote Code Execution (RCE)** capabilities over the operating system shell.\n\n"
                            f"#### **Refactored Secure Code Fix**:\n{code_fix}"
                        )
                    else:
                        fallback_text = f"🎉 No high-risk vulnerabilities were found in `{filename}`."

                # Query type B2: Production Readiness Assessment ("Is this code production ready?", "Can I deploy?")
                is_prod_readiness = any(k in query_lower for k in ["production ready", "can i deploy", "deploy to production", "ready for production", "is this ready"])
                if is_prod_readiness:
                    if high_count > 0:
                        fallback_text = (
                            f"### 🛑 **Production Readiness Assessment for `{filename}`**\n\n"
                            f"**Verdict**: **🔴 NOT PRODUCTION READY**\n\n"
                            f"**Blocking Vulnerabilities**:\n"
                            f"- Your application contains **{high_count} High Severity vulnerabilities** that allow Remote Code Execution, query manipulation, or secret exposure.\n\n"
                            f"#### **Required Pre-Deployment Steps**:\n"
                            f"1. Refactor all High/Critical vulnerabilities in the **AI Remediation Roadmap** tab.\n"
                            f"2. Separate hardcoded secrets into environment variables (`os.getenv`).\n"
                            f"3. Re-scan your code to confirm a clean 100/100 Health Score."
                        )
                    else:
                        fallback_text = (
                            f"### ✅ **Production Readiness Assessment for `{filename}`**\n\n"
                            f"**Verdict**: **🟢 PRODUCTION READY**\n\n"
                            f"No high-severity vulnerabilities were detected. Ensure standard TLS and environment configurations are set before deployment."
                        )
                    return ChatResponse(response=fallback_text, sources=rag_sources)

                # Query type B3: Unit Test Suite Generation ("How do I write a unit test for this?", "pytest")
                is_unit_test = any(k in query_lower for k in ["unit test", "write a test", "pytest", "junit", "test case", "how to test"])
                if is_unit_test:
                    lang_lower = (language or "python").lower()
                    if lang_lower == "python":
                        fallback_text = (
                            f"### 🧪 **Automated Unit Test Suite for `{filename}`**\n\n"
                            f"Here is a complete, runnable `pytest` suite for testing your application endpoints:\n\n"
                            f"```python\n"
                            f"import pytest\n"
                            f"from main import app\n\n"
                            f"@pytest.fixture\n"
                            f"def client():\n"
                            f"    app.config['TESTING'] = True\n"
                            f"    with app.test_client() as client:\n"
                            f"        yield client\n\n"
                            f"def test_invalid_login(client):\n"
                            f"    response = client.post('/login', data={{'username': 'invalid', 'password': 'wrong'}})\n"
                            f"    assert response.status_code == 401\n"
                            f"```"
                        )
                    else:
                        fallback_text = (
                            f"### 🧪 **Automated Unit Test Suite for `{filename}`**\n\n"
                            f"Here is a JUnit 5 test snippet:\n\n"
                            f"```java\n"
                            f"import org.junit.jupiter.api.Test;\n"
                            f"import static org.junit.jupiter.api.Assertions.*;\n\n"
                            f"class ApplicationTest {{\n"
                            f"    @Test\n"
                            f"    void testSecurityInput() {{\n"
                            f"        assertNotNull(new SecurityConfig());\n"
                            f"    }}\n"
                            f"}}\n"
                            f"```"
                        )
                    return ChatResponse(response=fallback_text, sources=rag_sources)

                # Query type B4: Exploit Payload & Defense Analysis ("' OR '1'='1", "exploit", "payload")
                is_payload_query = any(k in query_lower for k in ["' or '1'='1", "exploit", "payload", "attack vector", "how attacker exploit"])
                if is_payload_query:
                    fallback_text = (
                        f"### 🛡️ **Vulnerability Exploit & Defense Analysis**\n\n"
                        f"**Input Example**: `' OR '1'='1`\n\n"
                        f"#### **How the Attack Works (Unparameterized Query)**:\n"
                        f"When untrusted input `' OR '1'='1` is concatenated into a raw SQL query string:\n"
                        f"```sql\n"
                        f"SELECT * FROM users WHERE username='' OR '1'='1' AND password='...'\n"
                        f"```\n"
                        f"The clause `'1'='1'` evaluates to `TRUE`, overriding authentication logic and returning user records.\n\n"
                        f"#### **Defense (Parameterized Queries)**:\n"
                        f"With prepared statements (`cursor.execute('SELECT * FROM users WHERE username=%s', (user_input,))`), "
                        f"the database driver treats `' OR '1'='1` literally as a string literal value rather than executable SQL logic, neutralizing the attack completely."
                    )
                    return ChatResponse(response=fallback_text, sources=rag_sources)

                # Query type C: Explicit full report request OR specific severity request
                is_explicit_report = any(k in query_lower for k in [
                    "what are all findings", "all findings", "show all findings", "list all findings",
                    "full report", "vulnerability report", "scan report", "all issues", "show report",
                    "list findings", "overview of findings", "diagnostic analysis", "all vulnerabilities",
                    "every bug", "all bugs", "bugs found", "line-by-line", "explain every bug",
                    "explanation of every bug", "every issue", "all defects", "explain findings", "explain bugs",
                    "line by line"
                ])
                is_high_sec = any(k in query_lower for k in ["high severity", "critical", "major vulnerability", "major issue"])
                is_med_sec = any(k in query_lower for k in ["medium severity", "medium issue", "medium vulnerability", "medium", "moderate"])
                is_low_sec = any(k in query_lower for k in ["low severity", "low issue", "code smell", "code smells", "minor"])

                if is_explicit_report or is_high_sec or is_med_sec or is_low_sec:
                    if is_high_sec:
                        target_findings = [f for f in sorted_actionable if str(f.get("severity", "")).lower() in ["high", "critical"]]
                        header_title = "🚨 High Severity Vulnerability Remediation"
                    elif is_med_sec:
                        target_findings = [f for f in sorted_actionable if str(f.get("severity", "")).lower() in ["medium", "moderate"]]
                        header_title = "⚠️ Medium Severity Vulnerability Remediation"
                    elif is_low_sec:
                        target_findings = [f for f in sorted_actionable if str(f.get("severity", "")).lower() in ["low", "info"]]
                        header_title = "🔍 Low Severity & Code Smell Remediation"
                    else:
                        target_findings = sorted_actionable
                        header_title = "🛡️ Diagnostic Analysis & Solutions"

                    if target_findings:
                        findings_formatted = []
                        for idx, f in enumerate(target_findings[:5], 1):
                            line = f.get("line", "?")
                            sev = (f.get("severity") or "low").upper()
                            title = f.get("title", "Issue")
                            desc = f.get("description", "")
                            raw_rec = f.get("recommendation") or f.get("description") or f"Follow OWASP secure coding guidelines for {display_lang}."
                            rec = self._clean_recommendation(raw_rec, language)
                            code_fix = self._generate_code_fix_snippet(title, desc, language, line, analysis_data.get("code"))
                            findings_formatted.append(
                                f"#### {idx}. **{title}** (Line {line} • `{sev}`)\n"
                                f"- **Problem**: {desc}\n"
                                f"- **How to Fix**: {rec}\n\n"
                                f"**Refactored Secure Code Fix**:\n{code_fix}\n"
                            )
                        findings_str = "\n".join(findings_formatted)

                        fallback_text = (
                            f"### {header_title} for `{filename}`\n\n"
                            f"Showing **{len(target_findings)} matching items** ({high_count} High, {med_count} Medium, {low_count} Low total):\n\n"
                            f"{findings_str}\n"
                            f"💡 *Action Item*: Check the **AI Remediation Roadmap** tab for 1-click refactored code snippets."
                        )
                    else:
                        matching_label = "High" if is_high_sec else "Medium" if is_med_sec else "Low" if is_low_sec else ""
                        fallback_text = f"🎉 Great news! No {matching_label} Severity issues were flagged in your scanned file (`{filename}`)."

                    return ChatResponse(response=fallback_text, sources=rag_sources)

                # Query type D1: Code Explanation / Walkthrough Question ("What does get_user() function do?", "Explain login")
                is_code_explanation = any(k in query_lower for k in [
                    "what does", "explain", "how does", "purpose of", "what is the function",
                    "what do", "walkthrough", "describe", "code logic", "how work", "function do"
                ])

                if is_code_explanation:
                    full_code = analysis_data.get("code", "")
                    target_func = None
                    for line_str in full_code.splitlines():
                        if "def " in line_str:
                            f_name = line_str.split("def ")[1].split("(")[0].strip()
                            if f_name.lower() in query_lower:
                                target_func = f_name
                                break

                    if target_func:
                        func_lines = []
                        capturing = False
                        for line_str in full_code.splitlines():
                            if f"def {target_func}" in line_str:
                                capturing = True
                            elif capturing and line_str.startswith("def "):
                                break
                            if capturing:
                                func_lines.append(line_str)
                        func_snippet = "\n".join(func_lines)

                        sec_notes = []
                        if "SELECT" in func_snippet and "+" in func_snippet:
                            sec_notes.append("- 🚨 **SQL Injection**: Query uses unparameterized string concatenation.")
                        if "os.system" in func_snippet or "subprocess" in func_snippet:
                            sec_notes.append("- 🚨 **Command Injection**: Direct shell command execution from input.")
                        if "pickle.load" in func_snippet or "pickle.loads" in func_snippet:
                            sec_notes.append("- 🚨 **Insecure Deserialization**: Deserializing untrusted pickle payload.")
                        if "WHERE id =" in func_snippet or "WHERE id = ?" in func_snippet or "user_id" in func_snippet:
                            sec_notes.append("- ⚠️ **Access Control (IDOR)**: Endpoint queries records by ID without checking user ownership/authentication.")

                        sec_str = "\n".join(sec_notes) if sec_notes else "- No critical security flags detected on this function body."

                        fallback_text = (
                            f"### 📖 **Function Code Walkthrough: `{target_func}()`**\n\n"
                            f"**In Scanned File**: `{filename}`\n\n"
                            f"```python\n{func_snippet}\n```\n\n"
                            f"#### **Function Purpose & Logic**:\n"
                            f"1. **Endpoint Handler**: `{target_func}()` processes incoming HTTP request parameters.\n"
                            f"2. **Data Operations**: Performs internal logic or database operations for requested records.\n"
                            f"3. **Return Payload**: Returns JSON data or appropriate HTTP status codes.\n\n"
                            f"#### **Security & Quality Observations**:\n"
                            f"{sec_str}"
                        )
                        return ChatResponse(response=fallback_text, sources=rag_sources)

                # Query type D2: Runtime Error / Crash Inspection Question ("What runtime error will occur?", "will it crash")
                is_runtime_error = any(k in query_lower for k in [
                    "runtime error", "runtime-error", "crash", "exception", "typeerror",
                    "nameerror", "syntaxerror", "will it crash", "error on line", "runtime failure"
                ])

                if is_runtime_error:
                    full_code = analysis_data.get("code", "")
                    runtime_findings = []

                    if "pickle.load(" in full_code and "open(" not in full_code:
                        for l_idx, l_str in enumerate(full_code.splitlines(), 1):
                            if "pickle.load(" in l_str:
                                runtime_findings.append(
                                    f"#### **Line {l_idx}: `TypeError` on `pickle.load()`**\n"
                                    f"- **Vulnerable Line**: `{l_str.strip()}`\n"
                                    f"- **Runtime Error**: `pickle.load()` expects a file-like object with a `.read()` method. Passing raw byte/string data (e.g., `request.get_data()`) raises `TypeError: file must have a 'read' and 'readline' attribute!`.\n"
                                    f"- **Correct Fix**: Use `pickle.loads(data)` for byte strings, or replace with `json.loads(data)` for safe JSON handling."
                                )

                    if "subprocess" in full_code and "shell=True" in full_code:
                        for l_idx, l_str in enumerate(full_code.splitlines(), 1):
                            if "subprocess" in l_str or "os.system" in l_str:
                                runtime_findings.append(
                                    f"#### **Line {l_idx}: `subprocess.CalledProcessError`**\n"
                                    f"- **Vulnerable Line**: `{l_str.strip()}`\n"
                                    f"- **Runtime Error**: `subprocess.check_output()` will crash with `CalledProcessError` if the executed system shell command returns a non-zero exit code."
                                )

                    if runtime_findings:
                        runtime_str = "\n\n".join(runtime_findings)
                        fallback_text = (
                            f"### ⚠️ **Runtime Error & Exception Inspection for `{filename}`**\n\n"
                            f"{runtime_str}\n\n"
                            f"💡 *Recommendation*: Ensure file stream contracts match function specifications and wrap IO calls in `try...except` blocks."
                        )
                    else:
                        fallback_text = (
                            f"### ⚠️ **Runtime Error Inspection for `{filename}`**\n\n"
                            f"No immediate type contract crashes detected. Ensure request parameters and database connections are validated."
                        )
                    return ChatResponse(response=fallback_text, sources=rag_sources)

                # Query type D3: Specific question targeting a line number or vulnerability type in the report
                import re
                line_match = re.search(r"line\s*(\d+)", query_lower)
                target_line = line_match.group(1) if line_match else None

                matched_finding = None
                if target_line:
                    matched_finding = next((f for f in sorted_actionable if str(f.get("line")) == target_line), None)

                if not matched_finding:
                    # Match by vulnerability keyword in title/description
                    for f in sorted_actionable:
                        t_lower = (f.get("title") or "").lower()
                        d_lower = (f.get("description") or "").lower()
                        if any(kw in t_lower or kw in d_lower for kw in query_lower.split() if len(kw) > 3):
                            matched_finding = f
                            break

                if matched_finding:
                    m_line = matched_finding.get("line", "?")
                    m_sev = (matched_finding.get("severity") or "LOW").upper()
                    m_title = matched_finding.get("title", "Flagged Vulnerability")
                    m_desc = matched_finding.get("description", "")
                    raw_rec = matched_finding.get("recommendation") or matched_finding.get("description") or ""
                    m_rec = self._clean_recommendation(raw_rec, language)
                    m_fix = self._generate_code_fix_snippet(m_title, m_desc, language, m_line, analysis_data.get("code"))

                    fallback_text = (
                        f"### 🛡️ **Targeted Guidance: {m_title}** (Line {m_line} • `{m_sev}`)\n\n"
                        f"**In Scanned File**: `{filename}`\n"
                        f"- **Issue Identified**: {m_desc}\n"
                        f"- **Security Guidance**: {m_rec}\n\n"
                        f"#### **Refactored Secure Code Fix**:\n{m_fix}"
                    )
                    return ChatResponse(response=fallback_text, sources=rag_sources)

        if any(w in query_lower for w in ["improve", "refactor", "optimize", "clean code", "better code", "fix code", "how to improve", "how to fix"]):
            fallback_text = (
                f"### 🚀 **Code Improvement & Security Checklist ({language.capitalize()})**\n\n"
                f"Here are the top 4 high-impact ways to improve and secure your codebase:\n\n"
                f"1. **🛡️ Eliminate Hardcoded Secrets**\n"
                f"   - *Problem*: Storing credentials directly in code risks leaks via git repositories.\n"
                f"   - *Fix*: Move passwords and tokens to environment variables (`os.getenv('API_KEY')`).\n\n"
                f"2. **⚡ Prevent Injection Vulnerabilities**\n"
                f"   - *Problem*: String concatenation in SQL or OS commands allows attacker code execution.\n"
                f"   - *Fix*: Use parameterized queries (`cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))`) and `subprocess.run()` without `shell=True`.\n\n"
                f"3. **🔒 Secure Deserialization & Cryptography**\n"
                f"   - *Problem*: Using `pickle.loads()` or weak `MD5`/`SHA1` algorithms.\n"
                f"   - *Fix*: Replace `pickle` with `json` or `pydantic`, and upgrade password hashing to `bcrypt` or `SHA-256`.\n\n"
                f"4. **📖 Documentation & Maintainability**\n"
                f"   - *Problem*: Missing docstrings and type annotations.\n"
                f"   - *Fix*: Add descriptive docstrings and type hints to all top-level functions."
            )
        elif rag_results:
            top_doc = rag_results[0]
            fallback_text = (
                f"### 🛡️ Knowledge Base Guidance: **{top_doc['title']}**\n\n"
                f"{top_doc['content']}\n\n"
                f"**Recommendation**: When developing in {language.capitalize()}, ensure all inputs are strictly validated, "
                f"secrets are separated from source files, and database queries use prepared statements."
            )
        else:
            fallback_text = (
                f"I am your **CodeGuard AI Assistant**, specialized in **{language.capitalize()}** code quality and OWASP security analysis.\n\n"
                f"If your query is off-topic, feel free to ask me anything about code review, security vulnerabilities, or refactoring advice!\n\n"
                f"**Core Security Guidelines**:\n"
                f"- **Input Validation**: Never trust raw user inputs; sanitize and validate against strict whitelists.\n"
                f"- **Parameterized Queries**: Always use prepared statements or bound parameters for database queries.\n"
                f"- **Secrets Management**: Store API keys, passwords, and tokens in environment variables or secret vaults."
            )

        return ChatResponse(
            response=fallback_text,
            sources=rag_sources,
        )


assistant_agent = ConversationalAssistantAgent()
