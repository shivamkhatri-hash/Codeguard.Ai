import ast
import re
from typing import List, Dict, Any, Optional
import javalang

from app.schemas.analysis import Finding
from app.services.rag_service import rag_service

class PythonCodeQualityAnalyzer(ast.NodeVisitor):
    def __init__(self, code: str):
        self.code = code
        self.lines = code.splitlines()
        self.findings: List[Dict[str, Any]] = []

    def add_finding(self, node: ast.AST, title: str, severity: str, message: str) -> None:
        line_num = getattr(node, "lineno", 1)
        if 0 < line_num <= len(self.lines):
            snippet = self.lines[line_num - 1].strip()
        else:
            snippet = ""
        self.findings.append({
            "title": title,
            "severity": severity,
            "line": line_num,
            "description": message,
            "code_snippet": snippet
        })

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._analyze_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._analyze_function(node)
        self.generic_visit(node)

    def _analyze_function(self, node: ast.AST) -> None:
        name = getattr(node, "name", "<unknown>")
        args = getattr(node, "args", None)

        # 1. Mutable default arguments
        if args and args.defaults:
            for default in args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    self.add_finding(
                        default,
                        "Mutable Default Argument",
                        "medium",
                        "Mutable default argument (list, dict, set) used. "
                        "Default parameters are evaluated once and shared across calls."
                    )

        # 2. Function length
        start_lineno = getattr(node, "lineno", 1)
        end_lineno = getattr(node, "end_lineno", None)
        if end_lineno:
            length = end_lineno - start_lineno + 1
            if length > 50:
                self.add_finding(
                    node,
                    "Excessive Function Length",
                    "low",
                    f"Function '{name}' is too long ({length} lines). "
                    "Consider refactoring it into smaller modules."
                )

        # 3. Missing docstring
        if not ast.get_docstring(node):
            self.add_finding(
                node,
                "Missing Docstring",
                "low",
                f"Function '{name}' is missing a docstring."
            )

        # 4. Nesting complexity
        self.check_complexity(node)

        # 5. Excessive parameters
        if args:
            parameter_count = len(args.args)
            if parameter_count > 5:
                self.add_finding(
                    node,
                    "Excessive Parameters",
                    "medium",
                    f"Function '{name}' has {parameter_count} parameters. "
                    "Recommended maximum is 5."
                )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if not ast.get_docstring(node):
            self.add_finding(
                node,
                "Missing Docstring",
                "low",
                f"Class '{node.name}' is missing a docstring."
            )
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        for handler in node.handlers:
            if handler.type is None:
                self.add_finding(
                    handler,
                    "Bare Except Clause",
                    "medium",
                    "Bare except clause used. This catches all exceptions "
                    "including SystemExit and KeyboardInterrupt."
                )
            elif isinstance(handler.type, ast.Name) and handler.type.id in ("Exception", "BaseException"):
                self.add_finding(
                    handler,
                    "Broad Exception Handler",
                    "low",
                    f"Broad exception handler 'except {handler.type.id}' used. "
                    "Consider catching specific exceptions."
                )
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            if isinstance(node.right, ast.Constant) and node.right.value == 0:
                self.add_finding(
                    node,
                    "Potential Division by Zero",
                    "high",
                    "Potential division by zero detected."
                )
        self.generic_visit(node)

    def check_complexity(self, node: ast.AST) -> None:
        max_depth = [0]
        def traverse(current_node: ast.AST, current_depth: int) -> None:
            if isinstance(current_node, (ast.If, ast.For, ast.While, ast.Try)):
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
                "medium",
                f"High nesting complexity ({max_depth[0]} levels deep) "
                f"in function '{function_name}'. "
                "Consider breaking it into smaller functions."
            )


class JavaCodeQualityAnalyzer:
    def __init__(self, code: str):
        self.code = code
        self.lines = code.splitlines()
        self.findings: List[Dict[str, Any]] = []

    def _get_line(self, node: Any, path: List[Any]) -> int:
        if hasattr(node, 'position') and node.position is not None:
            return node.position.line
        for p in reversed(path):
            if hasattr(p, 'position') and p.position is not None:
                return p.position.line
        return 1

    def _get_snippet(self, line_num: int) -> str:
        if 0 < line_num <= len(self.lines):
            return self.lines[line_num - 1].strip()
        return ""

    def check_nesting(self, node: Any) -> int:
        max_depth = [0]
        def traverse(current_node: Any, current_depth: int):
            if isinstance(current_node, (
                javalang.tree.IfStatement,
                javalang.tree.ForStatement,
                javalang.tree.WhileStatement,
                javalang.tree.DoStatement,
                javalang.tree.TryStatement,
                javalang.tree.SwitchStatement
            )):
                current_depth += 1
                if current_depth > max_depth[0]:
                    max_depth[0] = current_depth
            if isinstance(current_node, javalang.tree.Node):
                for child in current_node.children:
                    if isinstance(child, list):
                        for item in child:
                            if isinstance(item, javalang.tree.Node):
                                traverse(item, current_depth)
                    elif isinstance(child, javalang.tree.Node):
                        traverse(child, current_depth)
        traverse(node, 0)
        return max_depth[0]

    def analyze(self) -> None:
        try:
            wrapped = False
            parse_code = self.code
            if "class" not in self.code and "interface" not in self.code:
                parse_code = (
                    "public class DummySnippetWrapper {\n"
                    "    public void dummyMethod() {\n"
                    f"{self.code}\n"
                    "    }\n"
                    "}"
                )
                wrapped = True

            tree = javalang.parse.parse(parse_code)

            # 1. Missing Javadoc
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                if 'public' in node.modifiers and not node.documentation:
                    line = self._get_line(node, path)
                    if wrapped:
                        line = max(1, line - 2)
                    self.findings.append({
                        "title": "Missing Docstring",
                        "severity": "low",
                        "line": line,
                        "description": f"Public class '{node.name}' is missing Javadoc documentation.",
                        "code_snippet": self._get_snippet(line)
                    })

            for path, node in tree.filter(javalang.tree.MethodDeclaration):
                if 'public' in node.modifiers and not node.documentation:
                    if wrapped and node.name == "dummyMethod":
                        continue
                    line = self._get_line(node, path)
                    if wrapped:
                        line = max(1, line - 2)
                    self.findings.append({
                        "title": "Missing Docstring",
                        "severity": "low",
                        "line": line,
                        "description": f"Public method '{node.name}' is missing Javadoc documentation.",
                        "code_snippet": self._get_snippet(line)
                    })

            # 2. Parameters, Length, Complexity
            for path, node in tree.filter(javalang.tree.MethodDeclaration):
                if wrapped and node.name == "dummyMethod":
                    # For wrapped snippets, check inner nesting/divzero but skip method signature rules
                    pass
                else:
                    # Excessive Parameters
                    param_count = len(node.parameters)
                    if param_count > 5:
                        line = self._get_line(node, path)
                        if wrapped:
                            line = max(1, line - 2)
                        self.findings.append({
                            "title": "Excessive Parameters",
                            "severity": "medium",
                            "line": line,
                            "description": f"Method '{node.name}' has {param_count} parameters. Recommended maximum is 5.",
                            "code_snippet": self._get_snippet(line)
                        })

                    # Method Length
                    start_line = self._get_line(node, path)
                    max_line = start_line
                    for path_c, node_c in node.filter(javalang.tree.Node):
                        line_c = self._get_line(node_c, path_c)
                        if line_c > max_line:
                            max_line = line_c
                    length = max_line - start_line + 1
                    if length > 50:
                        line = start_line
                        if wrapped:
                            line = max(1, line - 2)
                        self.findings.append({
                            "title": "Excessive Function Length",
                            "severity": "low",
                            "line": line,
                            "description": f"Method '{node.name}' is too long ({length} lines). "
                            "Consider refactoring it into smaller modules.",
                            "code_snippet": self._get_snippet(line)
                        })

                # Nesting complexity inside method body
                if node.body:
                    for statement in node.body:
                        max_nesting = self.check_nesting(statement)
                        if max_nesting > 3:
                            line = self._get_line(statement, path + (node, node.body))
                            if wrapped:
                                line = max(1, line - 2)
                            self.findings.append({
                                "title": "Excessive Nesting Complexity",
                                "severity": "medium",
                                "line": line,
                                "description": f"High nesting complexity ({max_nesting} levels deep) "
                                "detected in method block. Consider breaking it into smaller functions.",
                                "code_snippet": self._get_snippet(line)
                            })

            # 3. Empty Catch Block or Broad catch block
            for path, node in tree.filter(javalang.tree.CatchClause):
                line = self._get_line(node, path)
                if wrapped:
                    line = max(1, line - 2)

                is_broad = False
                if node.parameter and node.parameter.types:
                    for t in node.parameter.types:
                        if t in ("Exception", "Throwable", "RuntimeException"):
                            is_broad = True

                is_empty = not node.block or len(node.block) == 0

                if is_empty:
                    self.findings.append({
                        "title": "Empty Catch Block",
                        "severity": "medium",
                        "line": line,
                        "description": "Empty catch block detected. Exceptions should not be silently swallowed.",
                        "code_snippet": self._get_snippet(line)
                    })
                elif is_broad:
                    self.findings.append({
                        "title": "Broad Exception Handler",
                        "severity": "low",
                        "line": line,
                        "description": f"Broad exception handler catching general exceptions ({', '.join(node.parameter.types)}) was used. "
                        "Consider catching specific exception subclasses instead.",
                        "code_snippet": self._get_snippet(line)
                    })

            # 4. Potential Division by Zero
            for path, node in tree.filter(javalang.tree.BinaryOperation):
                if node.operator in ("/", "%"):
                    if isinstance(node.operandr, javalang.tree.Literal) and node.operandr.value == "0":
                        line = self._get_line(node, path)
                        if wrapped:
                            line = max(1, line - 2)
                        self.findings.append({
                            "title": "Potential Division by Zero",
                            "severity": "high",
                            "line": line,
                            "description": "Potential division by zero detected.",
                            "code_snippet": self._get_snippet(line)
                        })

        except Exception:
            pass


class CodeAnalysisAgent:
    def __init__(self):
        # Broad Exception catcher pattern for non-AST fallback / other languages
        self.patterns = [
            (
                r"\bcatch\s*\(\s*(Exception|Throwable)\b",
                "Broad Exception Handler",
                "low",
                "Broad exception catching detected. Catch specific exception subclasses instead."
            )
        ]

    def _analyze_patterns(self, code: str, language: str) -> List[Dict[str, Any]]:
        findings = []
        lines = code.splitlines()
        lang = language.lower()

        # Only run regex patterns for Java, C++, JS, TS if not using AST or if they match general patterns
        if lang in ("java", "cpp", "javascript", "typescript"):
            for index, line in enumerate(lines):
                line_stripped = line.strip()
                # Skip comments
                if line_stripped.startswith("//") or line_stripped.startswith("/*") or line_stripped.startswith("*"):
                    continue
                for regex, title, severity, desc in self.patterns:
                    if re.search(regex, line_stripped):
                        findings.append({
                            "title": title,
                            "severity": severity,
                            "line": index + 1,
                            "description": desc,
                            "code_snippet": line_stripped
                        })
        return findings

    def analyze_code(self, code: str, language: str) -> List[Finding]:
        raw_findings = []
        lang = language.lower()

        if lang == "python":
            try:
                tree = ast.parse(code)
                analyzer = PythonCodeQualityAnalyzer(code)
                analyzer.visit(tree)
                raw_findings.extend(analyzer.findings)
            except Exception as e:
                # If AST fails, add a syntax failure finding
                raw_findings.append({
                    "title": "Static Analysis Skipped",
                    "severity": "high",
                    "line": 1,
                    "description": f"Python parsing failed, quality checks skipped: {str(e)}",
                    "code_snippet": ""
                })

        elif lang == "java":
            try:
                analyzer = JavaCodeQualityAnalyzer(code)
                analyzer.analyze()
                raw_findings.extend(analyzer.findings)
            except Exception as e:
                raw_findings.append({
                    "title": "Static Analysis Skipped",
                    "severity": "high",
                    "line": 1,
                    "description": f"Java parsing failed, quality checks skipped: {str(e)}",
                    "code_snippet": ""
                })

        # Add pattern checks as fallback or for other languages
        pattern_findings = self._analyze_patterns(code, lang)
        
        # Deduplicate findings on the same line and same title
        existing_keys = {(f["line"], f["title"]) for f in raw_findings}
        for pf in pattern_findings:
            key = (pf["line"], pf["title"])
            if key not in existing_keys:
                raw_findings.append(pf)
                existing_keys.add(key)

        # Convert raw findings to Pydantic Finding models with RAG remediation
        findings = []
        for rf in raw_findings:
            remediation = rag_service.get_remediation(
                rf["title"],
                rf["description"],
                lang
            )
            findings.append(
                Finding(
                    type="code_smell",
                    title=rf["title"],
                    severity=rf["severity"],
                    line=rf["line"],
                    description=rf["description"],
                    recommendation=remediation,
                    code_snippet=rf["code_snippet"]
                )
            )

        return findings
