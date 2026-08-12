import ast
import re
from typing import Any, Dict, List

from app.schemas.analysis import Finding
from app.services.rag_service import rag_service


class PythonCodeAnalyzer(ast.NodeVisitor):
    def __init__(self, code: str):
        self.code = code
        self.lines = code.splitlines()
        self.findings: List[Finding] = []

        self.SQL_RE = re.compile(
            r"\b(select|insert|update|delete|create|drop|alter)\b",
            re.IGNORECASE,
        )

        self.SUSPICIOUS_VAR_NAMES = {
            "password",
            "passwd",
            "secret",
            "api_key",
            "apikey",
            "token",
            "private_key",
            "secret_key",
        }

    def add_finding(
        self,
        node: ast.AST,
        title: str,
        category: str,
        severity: str,
        message: str,
    ) -> None:
        line_num = getattr(node, "lineno", 1)

        if 0 < line_num <= len(self.lines):
            snippet = self.lines[line_num - 1].strip()
        else:
            snippet = ""

        # Get remediation suggestion from RAG service
        remediation = rag_service.get_remediation(
            title,
            message,
            "python",
        )

        self.findings.append(
            Finding(
                type=(
                    "security_vulnerability"
                    if category.lower() == "security"
                    else "code_smell"
                ),
                title=title,
                severity=severity,
                line=line_num,
                description=message,
                recommendation=remediation,
                code_snippet=snippet,
            )
        )

    def _get_call_name(self, node_func: ast.AST) -> str | None:
        if isinstance(node_func, ast.Name):
            return node_func.id

        if isinstance(node_func, ast.Attribute):
            prefix = self._get_call_name(node_func.value)

            if prefix:
                return f"{prefix}.{node_func.attr}"

            return node_func.attr

        return None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # 1. Mutable default arguments
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.add_finding(
                    default,
                    "Mutable Default Argument",
                    "Code Quality",
                    "medium",
                    "Mutable default argument (list, dict, set) used. "
                    "Default parameters are evaluated once and shared across calls.",
                )

        # 2. Function length
        if hasattr(node, "end_lineno") and node.end_lineno:
            length = node.end_lineno - node.lineno + 1

            if length > 50:
                self.add_finding(
                    node,
                    "Excessive Function Length",
                    "Code Quality",
                    "low",
                    f"Function '{node.name}' is too long ({length} lines). "
                    "Consider refactoring it into smaller modules.",
                )

        # 3. Missing docstring
        docstring = ast.get_docstring(node)

        if not docstring:
            self.add_finding(
                node,
                "Missing Docstring",
                "Style",
                "low",
                f"Function '{node.name}' is missing a docstring.",
            )

        # 4. Cognitive / nesting complexity
        self.check_complexity(node)

        # 5. Excessive parameters
        parameter_count = len(node.args.args)

        if parameter_count > 5:
            self.add_finding(
                node,
                "Excessive Parameters",
                "Code Quality",
                "medium",
                f"Function '{node.name}' has {parameter_count} parameters. "
                "Recommended maximum is 5.",
            )

        self.generic_visit(node)

    def visit_AsyncFunctionDef(
        self,
        node: ast.AsyncFunctionDef,
    ) -> None:
        # Apply the same checks used for normal functions.
        self._analyze_function(node)
        self.generic_visit(node)

    def _analyze_function(self, node: ast.AST) -> None:
        name = getattr(node, "name", "<unknown>")

        # Mutable defaults
        args = getattr(node, "args", None)

        if args:
            for default in args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    self.add_finding(
                        default,
                        "Mutable Default Argument",
                        "Code Quality",
                        "medium",
                        "Mutable default argument (list, dict, set) used. "
                        "Default parameters are evaluated once and shared across calls.",
                    )

        # Function length
        end_lineno = getattr(node, "end_lineno", None)
        start_lineno = getattr(node, "lineno", 1)

        if end_lineno:
            length = end_lineno - start_lineno + 1

            if length > 50:
                self.add_finding(
                    node,
                    "Excessive Function Length",
                    "Code Quality",
                    "low",
                    f"Function '{name}' is too long ({length} lines). "
                    "Consider refactoring it into smaller modules.",
                )

        # Missing docstring
        if not ast.get_docstring(node):
            self.add_finding(
                node,
                "Missing Docstring",
                "Style",
                "low",
                f"Function '{name}' is missing a docstring.",
            )

        # Complexity
        self.check_complexity(node)

        # Parameters
        if args:
            parameter_count = len(args.args)

            if parameter_count > 5:
                self.add_finding(
                    node,
                    "Excessive Parameters",
                    "Code Quality",
                    "medium",
                    f"Function '{name}' has {parameter_count} parameters. "
                    "Recommended maximum is 5.",
                )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Missing class docstring
        docstring = ast.get_docstring(node)

        if not docstring:
            self.add_finding(
                node,
                "Missing Docstring",
                "Style",
                "low",
                f"Class '{node.name}' is missing a docstring.",
            )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = self._get_call_name(node.func)

        # Unsafe eval / exec
        if call_name in ("eval", "exec"):
            self.add_finding(
                node,
                "Unsafe Dynamic Code Execution",
                "Security",
                "high",
                f"Use of unsafe function '{call_name}()' detected. "
                "This can lead to arbitrary code execution if user input is used.",
            )

        # os.system / os.popen
        elif call_name in ("os.system", "os.popen"):
            self.add_finding(
                node,
                "Command Injection Risk",
                "Security",
                "high",
                f"Insecure subprocess execution via '{call_name}()'. "
                "Use the subprocess module with shell=False instead.",
            )

        # subprocess(..., shell=True)
        elif call_name and call_name.startswith("subprocess."):
            for keyword in node.keywords:
                if (
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                ):
                    self.add_finding(
                        node,
                        "Command Injection Risk",
                        "Security",
                        "high",
                        f"Subprocess call '{call_name}' with shell=True detected. "
                        "This can be vulnerable to shell injection.",
                    )

        # pickle
        elif call_name in ("pickle.loads", "pickle.load"):
            self.add_finding(
                node,
                "Insecure Deserialization",
                "Security",
                "high",
                f"Insecure deserialization using '{call_name}()' detected. "
                "Untrusted pickle data can lead to arbitrary code execution.",
            )

        # yaml.load
        elif call_name == "yaml.load":
            has_safe_loader = False

            for keyword in node.keywords:
                if keyword.arg == "Loader":
                    loader_name = self._get_call_name(keyword.value)

                    if loader_name in ("yaml.SafeLoader", "SafeLoader"):
                        has_safe_loader = True

            if not has_safe_loader:
                self.add_finding(
                    node,
                    "Insecure Deserialization",
                    "Security",
                    "high",
                    "Unsafe yaml.load() call detected. "
                    "Use yaml.safe_load() or SafeLoader.",
                )

        # Weak hashing
        elif call_name in ("hashlib.md5", "hashlib.sha1"):
            self.add_finding(
                node,
                "Weak Cryptographic Hashing",
                "Security",
                "medium",
                f"Weak hashing algorithm '{call_name}' detected. "
                "Use SHA-256 or SHA-3 for secure contexts.",
            )

        # SQL string formatting using .format()
        elif call_name and call_name.endswith(".format"):
            base_str = None

            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Constant)
                and isinstance(node.func.value.value, str)
            ):
                base_str = node.func.value.value

            if base_str and self.SQL_RE.search(base_str):
                if node.args or node.keywords:
                    self.add_finding(
                        node,
                        "SQL Injection Risk",
                        "Security",
                        "high",
                        "Potential SQL injection vulnerability via "
                        ".format() in SQL query. Use parameterized queries instead.",
                    )

        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        for handler in node.handlers:
            # Bare except
            if handler.type is None:
                self.add_finding(
                    handler,
                    "Bare Except Clause",
                    "Code Quality",
                    "medium",
                    "Bare except clause used. This catches all exceptions "
                    "including SystemExit and KeyboardInterrupt.",
                )

            # Broad Exception
            elif (
                isinstance(handler.type, ast.Name)
                and handler.type.id in ("Exception", "BaseException")
            ):
                self.add_finding(
                    handler,
                    "Broad Exception Handler",
                    "Code Quality",
                    "low",
                    f"Broad exception handler 'except {handler.type.id}' used. "
                    "Consider catching specific exceptions.",
                )

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()

                if any(
                    keyword in var_name
                    for keyword in self.SUSPICIOUS_VAR_NAMES
                ):
                    if (
                        isinstance(node.value, ast.Constant)
                        and isinstance(node.value.value, str)
                    ):
                        value = node.value.value

                        if len(value) > 4:
                            self.add_finding(
                                node,
                                "Hardcoded Secrets",
                                "Security",
                                "high",
                                f"Possible hardcoded credential or secret "
                                f"detected in variable '{target.id}'.",
                            )

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        # SQL string concatenation / formatting
        if isinstance(node.op, (ast.Add, ast.Mod)):
            is_left_sql = False

            if (
                isinstance(node.left, ast.Constant)
                and isinstance(node.left.value, str)
            ):
                if self.SQL_RE.search(node.left.value):
                    is_left_sql = True

            if is_left_sql and not isinstance(node.right, ast.Constant):
                self.add_finding(
                    node,
                    "SQL Injection Risk",
                    "Security",
                    "high",
                    "Potential SQL injection vulnerability via string "
                    "formatting or concatenation in SQL query. "
                    "Use parameterized queries.",
                )

        # Division by zero
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            if (
                isinstance(node.right, ast.Constant)
                and node.right.value == 0
            ):
                self.add_finding(
                    node,
                    "Potential Division by Zero",
                    "Code Quality",
                    "high",
                    "Potential division by zero detected.",
                )

        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        full_text = ""
        has_expressions = False

        for value in node.values:
            if (
                isinstance(value, ast.Constant)
                and isinstance(value.value, str)
            ):
                full_text += value.value

            elif isinstance(value, ast.FormattedValue):
                has_expressions = True

        if has_expressions and self.SQL_RE.search(full_text):
            self.add_finding(
                node,
                "SQL Injection Risk",
                "Security",
                "high",
                "Potential SQL injection risk via f-string expression "
                "inside a SQL query. Use parameterized queries instead.",
            )

        self.generic_visit(node)

    def check_complexity(self, node: ast.AST) -> None:
        max_depth = [0]

        def traverse(current_node: ast.AST, current_depth: int) -> None:
            if isinstance(
                current_node,
                (ast.If, ast.For, ast.While, ast.Try),
            ):
                current_depth += 1

                if current_depth > max_depth[0]:
                    max_depth[0] = current_depth

            for child in ast.iter_child_nodes(current_node):
                traverse(child, current_depth)

        traverse(node, 0)

        if max_depth[0] > 3:
            function_name = getattr(node, "name", "<unknown>")

            self.add_finding(
                node,
                "Excessive Nesting Complexity",
                "Code Quality",
                "medium",
                f"High nesting complexity ({max_depth[0]} levels deep) "
                f"in function '{function_name}'. "
                "Consider breaking it into smaller functions.",
            )


class CodeAnalysisService:
    def _compute_metrics(
        self,
        code: str,
        language: str,
    ) -> Dict[str, Any]:
        """
        Computes general software metrics such as LOC,
        function count, class count, and cyclomatic complexity.
        """

        lines = code.splitlines()

        loc = len(
            [
                line
                for line in lines
                if line.strip()
                and not line.strip().startswith("#")
                and not line.strip().startswith("//")
            ]
        )

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

        keywords = decision_keywords.get(
            lang,
            [r"\bif\b"],
        )

        for line in lines:
            line_stripped = line.strip()

            # Function and class counting
            if lang == "python":
                if line_stripped.startswith("def "):
                    func_count += 1

                if line_stripped.startswith("async def "):
                    func_count += 1

                if line_stripped.startswith("class "):
                    class_count += 1

            else:
                if "class " in line_stripped and "{" in line_stripped:
                    class_count += 1

                if (
                    "function " in line_stripped
                    or (
                        (
                            "public" in line_stripped
                            or "private" in line_stripped
                        )
                        and "(" in line_stripped
                        and ")" in line_stripped
                        and ";" not in line_stripped
                    )
                ):
                    func_count += 1

            # Approximate cyclomatic complexity
            for keyword in keywords:
                complexity += len(
                    re.findall(keyword, line_stripped)
                )

        return {
            "lines_of_code": loc,
            "number_of_functions": func_count,
            "number_of_classes": class_count,
            "cyclomatic_complexity": complexity,
        }

    def _analyze_patterns(
        self,
        code: str,
        language: str,
    ) -> List[Finding]:
        """
        Generic multi-language static analysis
        using regex pattern matching.
        """

        findings: List[Finding] = []
        lines = code.splitlines()
        lang = language.lower()

        patterns = [
            (
                r'(?i)\b(password|passwd|secret|api_key|apikey|token|private_key|secret_key)\s*=\s*["\'][^"\']{5,}["\']',
                "Hardcoded Secrets",
                "Security",
                "high",
                "Possible hardcoded credential, password, or API secret key detected.",
            ),
            (
                r'(?i)["\'].*?\b(select|insert|update|delete|create|drop|alter)\b.*?["\']\s*[\+\%]',
                "SQL Injection Risk",
                "Security",
                "high",
                "Potential SQL injection detected via string concatenation "
                "in SQL query. Use prepared statements or bind parameters.",
            ),
            (
                r"\beval\s*\(",
                "Unsafe Dynamic Code Execution",
                "Security",
                "high",
                "Unsafe execution of dynamic code using eval(). "
                "This allows execution of arbitrary commands.",
            ),
            (
                r"\bexec\s*\(",
                "Unsafe Dynamic Code Execution",
                "Security",
                "high",
                "Unsafe execution of dynamic code using exec(). "
                "This allows execution of arbitrary commands.",
            ),
            (
                r"\.innerHTML\s*=",
                "Cross-Site Scripting (XSS) Risk",
                "Security",
                "high",
                "Potential DOM XSS via innerHTML assignment. "
                "Use textContent or innerText instead.",
            ),
        ]

        # Java, C++, JavaScript and TypeScript
        if lang in (
            "java",
            "cpp",
            "javascript",
            "typescript",
        ):
            patterns.append(
                (
                    r"\bcatch\s*\(\s*(Exception|Throwable)\b",
                    "Broad Exception Handler",
                    "Code Quality",
                    "low",
                    "Broad exception catching detected. "
                    "Catch specific exception subclasses instead.",
                )
            )

        # Java
        if lang == "java":
            patterns.extend(
                [
                    (
                        r"Runtime\.getRuntime\(\)\.exec\(",
                        "Command Injection Risk",
                        "Security",
                        "high",
                        "Process execution via Runtime.exec() can be "
                        "vulnerable to command injection if input is concatenated.",
                    ),
                    (
                        r'MessageDigest\.getInstance\(\s*["\'](MD5|SHA-1)["\']',
                        "Weak Cryptographic Hashing",
                        "Security",
                        "medium",
                        "Use of MD5/SHA-1 weak cryptographic hashing detected. "
                        "Upgrade to SHA-256 or SHA-3.",
                    ),
                ]
            )

        # C++
        elif lang == "cpp":
            patterns.append(
                (
                    r"\b(strcpy|gets|sprintf)\b\(",
                    "Buffer Overflow Risk",
                    "Security",
                    "high",
                    "Unbounded memory copies using strcpy, gets, or sprintf "
                    "can trigger buffer overflows. "
                    "Use safer alternatives such as strncpy, fgets, or snprintf.",
                )
            )

        # JavaScript / TypeScript
        elif lang in ("javascript", "typescript"):
            patterns.append(
                (
                    r"child_process\.exec\(",
                    "Command Injection Risk",
                    "Security",
                    "high",
                    "Insecure command execution using child_process.exec(). "
                    "Use execFile or spawn instead.",
                )
            )

        # Go
        elif lang == "go":
            patterns.append(
                (
                    r"exec\.Command\(",
                    "Command Injection Risk",
                    "Security",
                    "high",
                    "Command execution via exec.Command detected. "
                    "Ensure arguments are parameterized.",
                )
            )

        # HTML
        elif lang == "html":
            patterns.append(
                (
                    r"<script\b[^>]*>",
                    "Inline Script Tag",
                    "Security",
                    "medium",
                    "Inline script tag detected. Consider moving JavaScript "
                    "to external files and enforcing Content Security Policy (CSP).",
                )
            )

        # Scan line by line
        for index, line in enumerate(lines):
            line_num = index + 1
            line_stripped = line.strip()

            # Skip comments
            if (
                line_stripped.startswith("#")
                or line_stripped.startswith("//")
                or line_stripped.startswith("/*")
                or line_stripped.startswith("*")
            ):
                continue

            for (
                regex,
                title,
                category,
                severity,
                description,
            ) in patterns:

                if re.search(regex, line_stripped):
                    remediation = rag_service.get_remediation(
                        title,
                        description,
                        lang,
                    )

                    findings.append(
                        Finding(
                            type=(
                                "security_vulnerability"
                                if category.lower() == "security"
                                else "code_smell"
                            ),
                            title=title,
                            severity=severity,
                            line=line_num,
                            description=description,
                            recommendation=remediation,
                            code_snippet=line_stripped,
                        )
                    )

        return findings

    def analyze_code(
        self,
        code: str,
        language: str,
    ) -> List[Finding]:
        """
        Main analysis entrypoint.

        Runs:
        1. Python AST analysis
        2. Generic multi-language pattern checks
        3. Software metrics
        4. RAG-based remediation recommendations
        """

        findings: List[Finding] = []
        lang = language.lower()

        # 1. Python AST analysis
        if lang == "python":
            try:
                tree = ast.parse(code)

                analyzer = PythonCodeAnalyzer(code)
                analyzer.visit(tree)

                findings.extend(analyzer.findings)

            except SyntaxError as exc:
                findings.append(
                    Finding(
                        type="code_smell",
                        title="Static Analysis Skipped",
                        severity="high",
                        line=getattr(exc, "lineno", 1) or 1,
                        description=(
                            "Python parsing failed, so AST analysis "
                            f"was skipped: {str(exc)}"
                        ),
                        recommendation=(
                            "Fix Python syntax errors before running "
                            "full static analysis."
                        ),
                        code_snippet="",
                    )
                )

            except Exception as exc:
                findings.append(
                    Finding(
                        type="code_smell",
                        title="Static Analysis Error",
                        severity="high",
                        line=1,
                        description=(
                            "Unexpected error during Python AST analysis: "
                            f"{str(exc)}"
                        ),
                        recommendation=(
                            "Review the analyzer configuration and "
                            "try the analysis again."
                        ),
                        code_snippet="",
                    )
                )

        # 2. Generic pattern checks
        generic_findings = self._analyze_patterns(
            code,
            lang,
        )

        # Avoid duplicate findings on the same line
        existing_keys = {
            (
                finding.line,
                finding.title,
            )
            for finding in findings
        }

        for generic_finding in generic_findings:
            key = (
                generic_finding.line,
                generic_finding.title,
            )

            if key not in existing_keys:
                findings.append(generic_finding)
                existing_keys.add(key)

        # 3. Compute software metrics
        metrics = self._compute_metrics(
            code,
            lang,
        )

        # 4. Add metrics as informational finding
        complexity = metrics["cyclomatic_complexity"]

        if complexity < 10:
            complexity_label = "Low Complexity"
        elif complexity < 20:
            complexity_label = "Moderate Complexity"
        else:
            complexity_label = "High Complexity"

        metric_msg = (
            "Software Code Metrics:\n"
            f"- Non-comment Lines of Code (LOC): "
            f"{metrics['lines_of_code']}\n"
            f"- Number of Functions: "
            f"{metrics['number_of_functions']}\n"
            f"- Number of Classes: "
            f"{metrics['number_of_classes']}\n"
            f"- Cyclomatic Complexity Index: "
            f"{complexity} ({complexity_label})"
        )

        first_line = (
            code.splitlines()[0]
            if code.splitlines()
            else ""
        )

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

    def analyze_python_code(
        self,
        code: str,
    ) -> Dict[str, Any]:
        """
        Backward-compatible wrapper for Python analysis.
        """

        findings = self.analyze_code(
            code,
            "python",
        )

        return {
            "findings": [
                finding.model_dump()
                for finding in findings
            ]
        }


code_analysis_service = CodeAnalysisService()