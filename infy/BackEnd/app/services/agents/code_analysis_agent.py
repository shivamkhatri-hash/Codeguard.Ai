import ast
import re
from typing import List, Dict, Any

import javalang

from app.schemas.analysis import Finding
from app.services.rag_service import rag_service


# ============================================================
# PYTHON CODE QUALITY ANALYZER
# ============================================================

class PythonCodeQualityAnalyzer(ast.NodeVisitor):

    def __init__(self, code: str):
        self.code = code
        self.lines = code.splitlines()
        self.findings: List[Dict[str, Any]] = []

    # --------------------------------------------------------
    # Extract complete AST node source
    # --------------------------------------------------------

    def _get_node_source(self, node: ast.AST) -> str:
        """
        Return the complete source code represented by an AST node.

        This is important because remediation needs the affected
        function/class/block, not just the single line where the
        finding was detected.
        """

        start = getattr(node, "lineno", None)
        end = getattr(node, "end_lineno", None)

        if start is None:
            return ""

        if end is None:
            end = start

        start_index = max(0, start - 1)
        end_index = min(len(self.lines), end)

        return "\n".join(
            self.lines[start_index:end_index]
        ).rstrip()

    # --------------------------------------------------------
    # Add finding
    # --------------------------------------------------------

    def add_finding(
        self,
        node: ast.AST,
        title: str,
        severity: str,
        message: str,
    ) -> None:

        line_num = getattr(node, "lineno", 1)

        snippet = self._get_node_source(node)

        self.findings.append(
            {
                "title": title,
                "severity": severity,
                "line": line_num,
                "description": message,
                "code_snippet": snippet,
            }
        )

    # --------------------------------------------------------
    # Function analysis
    # --------------------------------------------------------

    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
    ) -> None:

        self._analyze_function(node)

        self.generic_visit(node)

    # --------------------------------------------------------
    # Async function analysis
    # --------------------------------------------------------

    def visit_AsyncFunctionDef(
        self,
        node: ast.AsyncFunctionDef,
    ) -> None:

        self._analyze_function(node)

        self.generic_visit(node)

    # --------------------------------------------------------
    # Analyze function
    # --------------------------------------------------------

    def _analyze_function(
        self,
        node: ast.AST,
    ) -> None:

        name = getattr(node, "name", "<unknown>")

        args = getattr(node, "args", None)

        # ----------------------------------------------------
        # 1. Mutable default arguments
        # ----------------------------------------------------

        if args and args.defaults:

            for default in args.defaults:

                if isinstance(
                    default,
                    (
                        ast.List,
                        ast.Dict,
                        ast.Set,
                    ),
                ):

                    self.add_finding(
                        node,
                        "Mutable Default Argument",
                        "medium",
                        (
                            "Mutable default argument (list, dict, set) "
                            "used. Default parameters are evaluated "
                            "once and shared across calls."
                        ),
                    )

        # ----------------------------------------------------
        # 2. Function length
        # ----------------------------------------------------

        start_lineno = getattr(
            node,
            "lineno",
            1,
        )

        end_lineno = getattr(
            node,
            "end_lineno",
            None,
        )

        if end_lineno:

            length = (
                end_lineno
                - start_lineno
                + 1
            )

            if length > 50:

                self.add_finding(
                    node,
                    "Excessive Function Length",
                    "low",
                    (
                        f"Function '{name}' is too long "
                        f"({length} lines). Consider refactoring "
                        "it into smaller modules."
                    ),
                )

        # ----------------------------------------------------
        # 3. Missing docstring
        # ----------------------------------------------------

        if not ast.get_docstring(node):

            self.add_finding(
                node,
                "Missing Docstring",
                "low",
                (
                    f"Function '{name}' is missing a docstring."
                ),
            )

        # ----------------------------------------------------
        # 4. Nesting complexity
        # ----------------------------------------------------

        self.check_complexity(node)

        # ----------------------------------------------------
        # 5. Excessive parameters
        # ----------------------------------------------------

        if args:

            parameter_count = len(args.args)

            if parameter_count > 5:

                self.add_finding(
                    node,
                    "Excessive Parameters",
                    "medium",
                    (
                        f"Function '{name}' has "
                        f"{parameter_count} parameters. "
                        "Recommended maximum is 5."
                    ),
                )

    # --------------------------------------------------------
    # Class analysis
    # --------------------------------------------------------

    def visit_ClassDef(
        self,
        node: ast.ClassDef,
    ) -> None:

        if not ast.get_docstring(node):

            self.add_finding(
                node,
                "Missing Docstring",
                "low",
                (
                    f"Class '{node.name}' is missing "
                    "a docstring."
                ),
            )

        self.generic_visit(node)

    # --------------------------------------------------------
    # Exception handling
    # --------------------------------------------------------

    def visit_Try(
        self,
        node: ast.Try,
    ) -> None:

        for handler in node.handlers:

            if handler.type is None:

                self.add_finding(
                    handler,
                    "Bare Except Clause",
                    "medium",
                    (
                        "Bare except clause used. This catches "
                        "all exceptions including SystemExit "
                        "and KeyboardInterrupt."
                    ),
                )

            elif (
                isinstance(
                    handler.type,
                    ast.Name,
                )
                and handler.type.id
                in (
                    "Exception",
                    "BaseException",
                )
            ):

                self.add_finding(
                    handler,
                    "Broad Exception Handler",
                    "low",
                    (
                        f"Broad exception handler "
                        f"'except {handler.type.id}' used. "
                        "Consider catching specific exceptions."
                    ),
                )

        self.generic_visit(node)

    # --------------------------------------------------------
    # Division by zero
    # --------------------------------------------------------

    def visit_BinOp(
        self,
        node: ast.BinOp,
    ) -> None:

        if isinstance(
            node.op,
            (
                ast.Div,
                ast.FloorDiv,
                ast.Mod,
            ),
        ):

            if (
                isinstance(
                    node.right,
                    ast.Constant,
                )
                and node.right.value == 0
            ):

                self.add_finding(
                    node,
                    "Potential Division by Zero",
                    "high",
                    "Potential division by zero detected.",
                )

        self.generic_visit(node)

    # --------------------------------------------------------
    # Complexity
    # --------------------------------------------------------

    def check_complexity(
        self,
        node: ast.AST,
    ) -> None:

        max_depth = [0]

        def traverse(
            current_node: ast.AST,
            current_depth: int,
        ) -> None:

            if isinstance(
                current_node,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.Try,
                ),
            ):

                current_depth += 1

                if current_depth > max_depth[0]:
                    max_depth[0] = current_depth

            for child in ast.iter_child_nodes(
                current_node
            ):
                traverse(
                    child,
                    current_depth,
                )

        traverse(node, 0)

        if max_depth[0] > 3:

            function_name = getattr(
                node,
                "name",
                "<unknown>",
            )

            self.add_finding(
                node,
                "Excessive Nesting Complexity",
                "medium",
                (
                    f"High nesting complexity "
                    f"({max_depth[0]} levels deep) "
                    f"in function '{function_name}'. "
                    "Consider breaking it into smaller functions."
                ),
            )


# ============================================================
# JAVA CODE QUALITY ANALYZER
# ============================================================

class JavaCodeQualityAnalyzer:

    def __init__(self, code: str):

        self.code = code
        self.lines = code.splitlines()
        self.findings: List[Dict[str, Any]] = []

    # --------------------------------------------------------
    # Get line number
    # --------------------------------------------------------

    def _get_line(
        self,
        node: Any,
        path: List[Any],
    ) -> int:

        if (
            hasattr(node, "position")
            and node.position is not None
        ):
            return node.position.line

        for item in reversed(path):

            if (
                hasattr(item, "position")
                and item.position is not None
            ):
                return item.position.line

        return 1

    # --------------------------------------------------------
    # Get relevant Java source
    # --------------------------------------------------------

    def _get_node_snippet(
        self,
        node: Any,
        path: List[Any],
    ) -> str:

        start_line = self._get_line(
            node,
            path,
        )

        if start_line < 1:
            start_line = 1

        # Try to determine an ending line from children.
        end_line = start_line

        if isinstance(
            node,
            javalang.tree.MethodDeclaration,
        ):

            for child_path, child in node.filter(
                javalang.tree.Node
            ):

                line = self._get_line(
                    child,
                    child_path,
                )

                if line > end_line:
                    end_line = line

        elif isinstance(
            node,
            javalang.tree.ClassDeclaration,
        ):

            for child_path, child in node.filter(
                javalang.tree.Node
            ):

                line = self._get_line(
                    child,
                    child_path,
                )

                if line > end_line:
                    end_line = line

        # Limit huge snippets.
        end_line = min(
            end_line,
            start_line + 120,
            len(self.lines),
        )

        return "\n".join(
            self.lines[
                start_line - 1:end_line
            ]
        ).rstrip()

    # --------------------------------------------------------
    # Nesting
    # --------------------------------------------------------

    def check_nesting(
        self,
        node: Any,
    ) -> int:

        max_depth = [0]

        def traverse(
            current_node: Any,
            current_depth: int,
        ):

            if isinstance(
                current_node,
                (
                    javalang.tree.IfStatement,
                    javalang.tree.ForStatement,
                    javalang.tree.WhileStatement,
                    javalang.tree.DoStatement,
                    javalang.tree.TryStatement,
                    javalang.tree.SwitchStatement,
                ),
            ):

                current_depth += 1

                if current_depth > max_depth[0]:
                    max_depth[0] = current_depth

            if isinstance(
                current_node,
                javalang.tree.Node,
            ):

                for child in current_node.children:

                    if isinstance(
                        child,
                        list,
                    ):

                        for item in child:

                            if isinstance(
                                item,
                                javalang.tree.Node,
                            ):

                                traverse(
                                    item,
                                    current_depth,
                                )

                    elif isinstance(
                        child,
                        javalang.tree.Node,
                    ):

                        traverse(
                            child,
                            current_depth,
                        )

        traverse(node, 0)

        return max_depth[0]

    # --------------------------------------------------------
    # Analyze Java
    # --------------------------------------------------------

    def analyze(self) -> None:

        try:

            wrapped = False

            parse_code = self.code

            if (
                "class" not in self.code
                and "interface" not in self.code
            ):

                parse_code = (
                    "public class DummySnippetWrapper {\n"
                    "    public void dummyMethod() {\n"
                    f"{self.code}\n"
                    "    }\n"
                    "}"
                )

                wrapped = True

            tree = javalang.parse.parse(
                parse_code
            )

            # ------------------------------------------------
            # Missing Javadoc
            # ------------------------------------------------

            for path, node in tree.filter(
                javalang.tree.ClassDeclaration
            ):

                if (
                    "public" in node.modifiers
                    and not node.documentation
                ):

                    line = self._get_line(
                        node,
                        path,
                    )

                    if wrapped:
                        line = max(
                            1,
                            line - 2,
                        )

                    snippet = (
                        self._get_node_snippet(
                            node,
                            path,
                        )
                    )

                    self.findings.append(
                        {
                            "title": "Missing Docstring",
                            "severity": "low",
                            "line": line,
                            "description": (
                                f"Public class '{node.name}' "
                                "is missing Javadoc documentation."
                            ),
                            "code_snippet": snippet,
                        }
                    )

            # ------------------------------------------------
            # Missing method Javadoc
            # ------------------------------------------------

            for path, node in tree.filter(
                javalang.tree.MethodDeclaration
            ):

                if (
                    "public" in node.modifiers
                    and not node.documentation
                ):

                    if (
                        wrapped
                        and node.name == "dummyMethod"
                    ):
                        continue

                    line = self._get_line(
                        node,
                        path,
                    )

                    if wrapped:
                        line = max(
                            1,
                            line - 2,
                        )

                    snippet = (
                        self._get_node_snippet(
                            node,
                            path,
                        )
                    )

                    self.findings.append(
                        {
                            "title": "Missing Docstring",
                            "severity": "low",
                            "line": line,
                            "description": (
                                f"Public method '{node.name}' "
                                "is missing Javadoc documentation."
                            ),
                            "code_snippet": snippet,
                        }
                    )

            # ------------------------------------------------
            # Method metrics
            # ------------------------------------------------

            for path, node in tree.filter(
                javalang.tree.MethodDeclaration
            ):

                if (
                    wrapped
                    and node.name == "dummyMethod"
                ):
                    continue

                # Excessive parameters
                param_count = len(
                    node.parameters
                )

                if param_count > 5:

                    line = self._get_line(
                        node,
                        path,
                    )

                    snippet = (
                        self._get_node_snippet(
                            node,
                            path,
                        )
                    )

                    self.findings.append(
                        {
                            "title": "Excessive Parameters",
                            "severity": "medium",
                            "line": line,
                            "description": (
                                f"Method '{node.name}' has "
                                f"{param_count} parameters. "
                                "Recommended maximum is 5."
                            ),
                            "code_snippet": snippet,
                        }
                    )

                # Method length
                start_line = self._get_line(
                    node,
                    path,
                )

                max_line = start_line

                for path_c, node_c in node.filter(
                    javalang.tree.Node
                ):

                    line_c = self._get_line(
                        node_c,
                        path_c,
                    )

                    if line_c > max_line:
                        max_line = line_c

                length = (
                    max_line
                    - start_line
                    + 1
                )

                if length > 50:

                    line = start_line

                    snippet = (
                        self._get_node_snippet(
                            node,
                            path,
                        )
                    )

                    self.findings.append(
                        {
                            "title": "Excessive Function Length",
                            "severity": "low",
                            "line": line,
                            "description": (
                                f"Method '{node.name}' is too long "
                                f"({length} lines). Consider "
                                "refactoring it into smaller modules."
                            ),
                            "code_snippet": snippet,
                        }
                    )

                # Nesting
                if node.body:

                    for statement in node.body:

                        max_nesting = (
                            self.check_nesting(
                                statement
                            )
                        )

                        if max_nesting > 3:

                            line = self._get_line(
                                statement,
                                path,
                            )

                            snippet = (
                                self._get_node_snippet(
                                    node,
                                    path,
                                )
                            )

                            self.findings.append(
                                {
                                    "title": (
                                        "Excessive Nesting Complexity"
                                    ),
                                    "severity": "medium",
                                    "line": line,
                                    "description": (
                                        f"High nesting complexity "
                                        f"({max_nesting} levels deep) "
                                        "detected in method block. "
                                        "Consider breaking it into "
                                        "smaller functions."
                                    ),
                                    "code_snippet": snippet,
                                }
                            )

            # ------------------------------------------------
            # Catch blocks
            # ------------------------------------------------

            for path, node in tree.filter(
                javalang.tree.CatchClause
            ):

                line = self._get_line(
                    node,
                    path,
                )

                if wrapped:
                    line = max(
                        1,
                        line - 2,
                    )

                is_broad = False

                if (
                    node.parameter
                    and node.parameter.types
                ):

                    for exception_type in (
                        node.parameter.types
                    ):

                        if exception_type in (
                            "Exception",
                            "Throwable",
                            "RuntimeException",
                        ):
                            is_broad = True

                is_empty = (
                    not node.block
                    or len(node.block) == 0
                )

                snippet = (
                    self._get_node_snippet(
                        node,
                        path,
                    )
                )

                if is_empty:

                    self.findings.append(
                        {
                            "title": "Empty Catch Block",
                            "severity": "medium",
                            "line": line,
                            "description": (
                                "Empty catch block detected. "
                                "Exceptions should not be silently swallowed."
                            ),
                            "code_snippet": snippet,
                        }
                    )

                elif is_broad:

                    self.findings.append(
                        {
                            "title": "Broad Exception Handler",
                            "severity": "low",
                            "line": line,
                            "description": (
                                "Broad exception handler catching "
                                "general exceptions was used. "
                                "Consider catching specific "
                                "exception subclasses instead."
                            ),
                            "code_snippet": snippet,
                        }
                    )

            # ------------------------------------------------
            # Division by zero
            # ------------------------------------------------

            for path, node in tree.filter(
                javalang.tree.BinaryOperation
            ):

                if node.operator in (
                    "/",
                    "%",
                ):

                    if (
                        isinstance(
                            node.operandr,
                            javalang.tree.Literal,
                        )
                        and node.operandr.value == "0"
                    ):

                        line = self._get_line(
                            node,
                            path,
                        )

                        snippet = (
                            self._get_node_snippet(
                                node,
                                path,
                            )
                        )

                        self.findings.append(
                            {
                                "title": (
                                    "Potential Division by Zero"
                                ),
                                "severity": "high",
                                "line": line,
                                "description": (
                                    "Potential division by zero detected."
                                ),
                                "code_snippet": snippet,
                            }
                        )

        except Exception:
            # Parsing errors are handled by the main agent.
            pass


# ============================================================
# GENERAL PATTERN ANALYZER
# ============================================================

class CodeAnalysisAgent:

    def __init__(self):

        self.patterns = [

            (
                r"\bcatch\s*\(\s*(Exception|Throwable)\b",
                "Broad Exception Handler",
                "low",
                (
                    "Broad exception catching detected. "
                    "Catch specific exception subclasses instead."
                ),
            )
        ]

    # --------------------------------------------------------
    # Get contextual snippet for a line
    # --------------------------------------------------------

    @staticmethod
    def _get_context_snippet(
        lines: List[str],
        line_number: int,
        context_before: int = 3,
        context_after: int = 5,
    ) -> str:

        if not lines:
            return ""

        index = max(
            0,
            line_number - 1,
        )

        start = max(
            0,
            index - context_before,
        )

        end = min(
            len(lines),
            index + context_after + 1,
        )

        return "\n".join(
            lines[start:end]
        ).rstrip()

    # --------------------------------------------------------
    # Pattern checks
    # --------------------------------------------------------

    def _analyze_patterns(
        self,
        code: str,
        language: str,
    ) -> List[Dict[str, Any]]:

        findings = []

        lines = code.splitlines()

        lang = language.lower()

        if lang in (
            "java",
            "cpp",
            "javascript",
            "typescript",
        ):

            for index, line in enumerate(
                lines
            ):

                line_stripped = line.strip()

                # Skip comments
                if (
                    line_stripped.startswith("//")
                    or line_stripped.startswith("/*")
                    or line_stripped.startswith("*")
                ):
                    continue

                for (
                    regex,
                    title,
                    severity,
                    desc,
                ) in self.patterns:

                    if re.search(
                        regex,
                        line_stripped,
                    ):

                        findings.append(
                            {
                                "title": title,
                                "severity": severity,
                                "line": index + 1,
                                "description": desc,
                                "code_snippet": (
                                    self._get_context_snippet(
                                        lines,
                                        index + 1,
                                    )
                                ),
                            }
                        )

        return findings

    # --------------------------------------------------------
    # Main analysis
    # --------------------------------------------------------

    def analyze_code(
        self,
        code: str,
        language: str,
    ) -> List[Finding]:

        raw_findings = []

        lang = language.lower()

        # ----------------------------------------------------
        # Python
        # ----------------------------------------------------

        if lang == "python":

            try:

                tree = ast.parse(code)

                analyzer = PythonCodeQualityAnalyzer(
                    code
                )

                analyzer.visit(tree)

                raw_findings.extend(
                    analyzer.findings
                )

            except Exception as e:

                raw_findings.append(
                    {
                        "title": "Static Analysis Skipped",
                        "severity": "high",
                        "line": 1,
                        "description": (
                            "Python parsing failed, quality checks "
                            f"skipped: {str(e)}"
                        ),
                        "code_snippet": "",
                    }
                )

        # ----------------------------------------------------
        # Java
        # ----------------------------------------------------

        elif lang == "java":

            try:

                analyzer = JavaCodeQualityAnalyzer(
                    code
                )

                analyzer.analyze()

                raw_findings.extend(
                    analyzer.findings
                )

            except Exception as e:

                raw_findings.append(
                    {
                        "title": "Static Analysis Skipped",
                        "severity": "high",
                        "line": 1,
                        "description": (
                            "Java parsing failed, quality checks "
                            f"skipped: {str(e)}"
                        ),
                        "code_snippet": "",
                    }
                )

        # ----------------------------------------------------
        # Regex / general patterns
        # ----------------------------------------------------

        pattern_findings = (
            self._analyze_patterns(
                code,
                lang,
            )
        )

        # ----------------------------------------------------
        # Deduplicate
        # ----------------------------------------------------

        existing_keys = {
            (
                f["line"],
                f["title"],
            )
            for f in raw_findings
        }

        for pf in pattern_findings:

            key = (
                pf["line"],
                pf["title"],
            )

            if key not in existing_keys:

                raw_findings.append(
                    pf
                )

                existing_keys.add(
                    key
                )

        # ----------------------------------------------------
        # Convert to Finding schemas
        # ----------------------------------------------------

        findings = []

        for rf in raw_findings:

            remediation = (
                rag_service.get_remediation(
                    rf["title"],
                    rf["description"],
                    lang,
                )
            )

            findings.append(
                Finding(
                    type="code_smell",
                    title=rf["title"],
                    severity=rf["severity"],
                    line=rf["line"],
                    description=rf["description"],
                    recommendation=remediation,
                    code_snippet=rf.get(
                        "code_snippet",
                        "",
                    ),
                )
            )

        return findings


# ============================================================
# SHARED AGENT INSTANCE
# ============================================================

code_analysis_agent = CodeAnalysisAgent()