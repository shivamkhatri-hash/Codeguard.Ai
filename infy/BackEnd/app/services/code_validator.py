import ast
import javalang
import subprocess
import re
from typing import Dict, Any, List, Tuple
from html.parser import HTMLParser
from app.core.config import settings

class HTMLTagBalancer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.self_closing = {
            'img', 'input', 'br', 'hr', 'meta', 'link', 'col', 
            'base', 'area', 'param', 'source', 'track', 'wbr'
        }

    def handle_starttag(self, tag, attrs):
        if tag not in self.self_closing:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.self_closing:
            return
        if not self.stack:
            self.errors.append({"line": self.getpos()[0], "message": f"Unexpected closing tag </{tag}> without opening tag."})
            return
        top_tag, pos = self.stack.pop()
        if top_tag != tag:
            self.errors.append({"line": pos[0], "message": f"Mismatched HTML tags: opened <{top_tag}> on line {pos[0]} but closed with </{tag}> on line {self.getpos()[0]}."})

class CodeValidatorService:
    @staticmethod
    def validate_metadata(code: str, language: str) -> Tuple[bool, str]:
        """
        Validates basic metadata: language support, size limits, and non-empty criteria.
        """
        if not code or not code.strip():
            return False, "Code content cannot be empty"
            
        if language.lower() not in settings.ALLOWED_LANGUAGES:
            return False, f"Unsupported language. Allowed languages: {', '.join(settings.ALLOWED_LANGUAGES)}"
            
        if len(code.encode("utf-8")) > settings.MAX_FILE_SIZE_BYTES:
            limit_mb = settings.MAX_FILE_SIZE_BYTES / (1024 * 1024)
            return False, f"Code size exceeds the limit of {limit_mb:.1f} MB"
            
        return True, ""

    @staticmethod
    def validate_python_syntax(code: str) -> Dict[str, Any]:
        """
        Checks Python syntax using the standard ast library.
        """
        try:
            ast.parse(code)
            return {"syntax_valid": True, "errors": []}
        except SyntaxError as e:
            return {
                "syntax_valid": False,
                "errors": [
                    {
                        "line": e.lineno if e.lineno is not None else 1,
                        "message": e.msg or "Syntax error"
                    }
                ]
            }
        except Exception as e:
            return {
                "syntax_valid": False,
                "errors": [
                    {
                        "line": 1,
                        "message": f"Python parser error: {str(e)}"
                    }
                ]
            }

    @classmethod
    def validate_java_syntax(cls, code: str) -> Dict[str, Any]:
        """
        Checks Java syntax using javalang. Fallbacks to wrapping the code inside a
        dummy class/method structure if it looks like a snippet rather than a full source file.
        """
        try:
            javalang.parse.parse(code)
            return {"syntax_valid": True, "errors": []}
        except javalang.parser.JavaSyntaxError as e:
            if "class" not in code and "interface" not in code:
                return cls._validate_java_snippet(code, original_error=e)
            
            line_no = 1
            if e.at and hasattr(e.at, 'position') and e.at.position:
                line_no = e.at.position.line
            elif e.at and hasattr(e.at, 'line'):
                line_no = e.at.line
            elif e.at and isinstance(e.at, tuple) and len(e.at) > 0:
                line_no = e.at[0]
                
            return {
                "syntax_valid": False,
                "errors": [
                    {
                        "line": line_no,
                        "message": e.description or str(e) or "Syntax error"
                    }
                ]
            }
        except javalang.tokenizer.LexerError as e:
            msg = str(e)
            line_no = 1
            match = re.search(r"line (\d+)", msg)
            if match:
                line_no = int(match.group(1))
            return {
                "syntax_valid": False,
                "errors": [
                    {
                        "line": line_no,
                        "message": msg or "Lexical error"
                    }
                ]
            }
        except Exception as e:
            msg = str(e)
            line_no = 1
            match = re.search(r"line (\d+)", msg)
            if match:
                line_no = int(match.group(1))
            return {
                "syntax_valid": False,
                "errors": [
                    {
                        "line": line_no,
                        "message": f"Java parser error: {msg}"
                    }
                ]
            }

    @staticmethod
    def _validate_java_snippet(code: str, original_error: Exception) -> Dict[str, Any]:
        """
        Wraps a Java code snippet in a dummy class to check internal statement syntax.
        """
        wrapped_code = (
            "public class DummySnippetWrapper {\n"
            "    public void dummyMethod() {\n"
            f"{code}\n"
            "    }\n"
            "}"
        )
        try:
            javalang.parse.parse(wrapped_code)
            return {"syntax_valid": True, "errors": []}
        except javalang.parser.JavaSyntaxError as wrap_e:
            wrap_line_no = 1
            if wrap_e.at and hasattr(wrap_e.at, 'position') and wrap_e.at.position:
                wrap_line_no = wrap_e.at.position.line
            elif wrap_e.at and hasattr(wrap_e.at, 'line'):
                wrap_line_no = wrap_e.at.line
            elif wrap_e.at and isinstance(wrap_e.at, tuple) and len(wrap_e.at) > 0:
                wrap_line_no = wrap_e.at[0]
            
            # Subtraction offset: 2 header lines are prepended
            original_line = max(1, wrap_line_no - 2)
            wrap_message = wrap_e.description if wrap_e.description else str(wrap_e)
            return {
                "syntax_valid": False,
                "errors": [
                    {
                        "line": original_line,
                        "message": wrap_message
                    }
                ]
            }
        except Exception:
            orig_msg = getattr(original_error, 'description', str(original_error))
            orig_line = 1
            if hasattr(original_error, 'at') and original_error.at and hasattr(original_error.at, 'line'):
                orig_line = original_error.at.line
            return {
                "syntax_valid": False,
                "errors": [
                    {
                        "line": orig_line,
                        "message": orig_msg
                    }
                ]
            }

    def _validate_brackets_and_quotes(self, code: str) -> dict:
        """
        Generic syntax checker that verifies brackets, braces, parentheses, and quotes balance.
        """
        stack = []
        lines = code.splitlines()
        open_chars = {'(': ')', '[': ']', '{': '}'}
        close_chars = {')', ']', '}'}
        quotes = {"'", '"', '`'}
        
        in_quote = None
        quote_start_line = 0
        
        for idx, line in enumerate(lines):
            line_num = idx + 1
            i = 0
            while i < len(line):
                char = line[i]
                
                # Skip comments
                if in_quote is None and i < len(line) - 1 and line[i:i+2] == '//':
                    break
                
                if char in quotes:
                    if in_quote == char:
                        in_quote = None
                    elif in_quote is None:
                        in_quote = char
                        quote_start_line = line_num
                elif in_quote is None:
                    if char in open_chars:
                        stack.append((char, line_num))
                    elif char in close_chars:
                        if not stack:
                            return {"syntax_valid": False, "errors": [{"line": line_num, "message": f"Unexpected closing bracket '{char}'"}]}
                        top, start_line = stack.pop()
                        if open_chars[top] != char:
                            return {"syntax_valid": False, "errors": [{"line": line_num, "message": f"Mismatched brackets: expected '{open_chars[top]}', found '{char}'"}]}
                
                if char == '\\':
                    i += 1
                i += 1
                
        if in_quote:
            return {"syntax_valid": False, "errors": [{"line": quote_start_line, "message": f"Unterminated string literal starting on line {quote_start_line}"}]}
        if stack:
            top, start_line = stack.pop()
            return {"syntax_valid": False, "errors": [{"line": start_line, "message": f"Unclosed bracket '{top}'"}]}
            
        return {"syntax_valid": True, "errors": []}

    def _validate_js_node(self, code: str) -> dict:
        """
        Validates JavaScript syntax using Node.js syntax-check mode.
        """
        try:
            res = subprocess.run(
                ["node", "-c", "-"],
                input=code.encode("utf-8"),
                capture_output=True,
                timeout=2
            )
            if res.returncode == 0:
                return {"syntax_valid": True, "errors": []}
            else:
                stderr = res.stderr.decode("utf-8")
                line = 1
                match = re.search(r'\[stdin\]:(\d+)', stderr)
                if match:
                    line = int(match.group(1))
                
                msg = "JavaScript syntax error"
                for line_str in stderr.splitlines():
                    if "SyntaxError:" in line_str:
                        msg = line_str
                        break
                return {"syntax_valid": False, "errors": [{"line": line, "message": msg}]}
        except Exception:
            return self._validate_brackets_and_quotes(code)

    def _validate_html(self, code: str) -> dict:
        """
        Validates HTML tag structure using Python's HTMLParser and checks for language mismatches.
        """
        stripped = code.strip()

        # 1. Detect non-HTML programming language keywords
        non_html_patterns = [
            (r"^\s*package\s+\w+", "Go / Java package declaration"),
            (r"^\s*func\s+\w+", "Go function definition"),
            (r"^\s*def\s+\w+\s*\(", "Python function definition"),
            (r"^\s*#include\s*<", "C/C++ include header"),
            (r"^\s*public\s+class\s+\w+", "Java class declaration"),
            (r"^\s*using\s+namespace\s+", "C++ namespace statement"),
        ]

        for pattern, desc in non_html_patterns:
            if re.search(pattern, stripped, re.MULTILINE):
                return {
                    "syntax_valid": False,
                    "errors": [
                        {
                            "line": 1,
                            "message": f"Language Mismatch: Selected language is HTML, but submitted code contains {desc}."
                        }
                    ]
                }

        # 2. Require presence of HTML tags or doctype
        if not re.search(r"<[a-zA-Z!/][^>]*>", stripped):
            return {
                "syntax_valid": False,
                "errors": [
                    {
                        "line": 1,
                        "message": "Syntax Error: HTML source must contain valid HTML tags (e.g., <html>, <div>, <p>)."
                    }
                ]
            }

        # 3. Verify HTML tag balance
        parser = HTMLTagBalancer()
        try:
            parser.feed(code)
            if parser.errors:
                return {"syntax_valid": False, "errors": [parser.errors[0]]}
            if parser.stack:
                tag, pos = parser.stack.pop()
                return {"syntax_valid": False, "errors": [{"line": pos[0], "message": f"Unclosed HTML tag <{tag}>."}]}
            return {"syntax_valid": True, "errors": []}
        except Exception as e:
            return {"syntax_valid": False, "errors": [{"line": 1, "message": f"HTML parser exception: {str(e)}"}]}

    @staticmethod
    def validate_metadata(code: str, language: str) -> Tuple[bool, str]:
        """
        Validates basic metadata: language support, size limits, and non-empty criteria.
        """
        if not code or not code.strip():
            return False, "Code content cannot be empty"
            
        if language.lower() not in settings.ALLOWED_LANGUAGES:
            lang_display = language.capitalize() if language else "This language"
            return False, f"{lang_display} is currently not supported by CodeGuard AI, but support will be added soon!"
            
        if len(code.encode("utf-8")) > settings.MAX_FILE_SIZE_BYTES:
            limit_mb = settings.MAX_FILE_SIZE_BYTES / (1024 * 1024)
            return False, f"Code size exceeds the limit of {limit_mb:.1f} MB"
            
        return True, ""

    @classmethod
    def validate_code(cls, code: str, language: str) -> Dict[str, Any]:
        """
        Main entrypoint for syntax validation and language mismatch verification.
        """
        lang = language.lower()
        stripped = code.strip()

        # 1. Guard against Unsupported Languages (Rust, C#, PHP, Ruby, Swift, Kotlin, etc.)
        unsupported_signatures = [
            (r"^\s*fn\s+main\s*\(", "Rust"),
            (r"println!\s*\(", "Rust"),
            (r"^\s*let\s+mut\s+", "Rust"),
            (r"^\s*use\s+std::", "Rust"),
            (r"^\s*pub\s+fn\s+", "Rust"),
            (r"^\s*using\s+System;", "C#"),
            (r"^\s*namespace\s+[A-Za-z0-9_.]+", "C#"),
            (r"Console\.WriteLine\(", "C#"),
            (r"^\s*<\?php", "PHP"),
            (r"^\s*echo\s+\$", "PHP"),
            (r"^\s*require\s+['\"]", "Ruby"),
            (r"^\s*attr_accessor\s+", "Ruby"),
            (r"^\s*fun\s+main\s*\(", "Kotlin"),
            (r"^\s*import\s+Foundation", "Swift"),
            (r"^\s*import\s+UIKit", "Swift"),
            (r"^\s*object\s+\w+\s*\{\s*def\s+main", "Scala"),
            (r"^#!/(bin|usr/bin)/(bash|sh|zsh)", "Shell"),
            (r"^\s*library\([a-zA-Z0-9._]+\)", "R"),
            (r"^\s*import\s+'package:", "Dart"),
            (r"^\s*defmodule\s+", "Elixir"),
            (r"^\s*main\s*::\s*IO\s*\(\)", "Haskell"),
        ]
        for pattern, detected_lang in unsupported_signatures:
            if re.search(pattern, stripped, re.MULTILINE):
                return {
                    "syntax_valid": False,
                    "errors": [
                        {
                            "line": 1,
                            "message": f"{detected_lang} is currently not supported by CodeGuard AI, but support will be added soon!"
                        }
                    ]
                }

        # 2. Guard against raw HTML pasted into non-HTML languages
        if lang in ("go", "cpp", "python", "java", "javascript", "typescript") and re.search(r"^\s*<(!DOCTYPE|html|body|div|p|h1|h2|script)", stripped, re.IGNORECASE):
            return {
                "syntax_valid": False,
                "errors": [
                    {
                        "line": 1,
                        "message": f"Language Mismatch: Selected language is {lang.upper()}, but submitted code appears to be HTML markup."
                    }
                ]
            }

        # 2. Guard against language construct mismatch for Go
        if lang == "go":
            mismatches = [
                (r"^\s*def\s+\w+\s*\(", "Python function definition"),
                (r"^\s*public\s+class\s+\w+", "Java class declaration"),
                (r"^\s*#include\s*<", "C/C++ include header"),
            ]
            for pattern, desc in mismatches:
                if re.search(pattern, stripped, re.MULTILINE):
                    return {
                        "syntax_valid": False,
                        "errors": [{"line": 1, "message": f"Language Mismatch: Selected language is GO, but code contains {desc}."}]
                    }

        # 3. Guard against language construct mismatch for C++
        if lang == "cpp":
            mismatches = [
                (r"^\s*package\s+main", "Go package declaration"),
                (r"^\s*func\s+main", "Go function definition"),
                (r"^\s*def\s+\w+\s*\(", "Python function definition"),
                (r"^\s*public\s+class\s+\w+", "Java class declaration"),
            ]
            for pattern, desc in mismatches:
                if re.search(pattern, stripped, re.MULTILINE):
                    return {
                        "syntax_valid": False,
                        "errors": [{"line": 1, "message": f"Language Mismatch: Selected language is CPP, but code contains {desc}."}]
                    }

        # 4. Guard against language construct mismatch for TypeScript
        if lang == "typescript":
            mismatches = [
                (r"^\s*package\s+main", "Go package declaration"),
                (r"^\s*func\s+main", "Go function definition"),
                (r"^\s*#include\s*<", "C/C++ include header"),
                (r"^\s*def\s+\w+\s*\(", "Python function definition"),
                (r"^\s*public\s+class\s+\w+", "Java class declaration"),
            ]
            for pattern, desc in mismatches:
                if re.search(pattern, stripped, re.MULTILINE):
                    return {
                        "syntax_valid": False,
                        "errors": [{"line": 1, "message": f"Language Mismatch: Selected language is TYPESCRIPT, but code contains {desc}."}]
                    }

        if lang == "python":
            return cls.validate_python_syntax(code)
        elif lang == "java":
            return cls.validate_java_syntax(code)
        elif lang == "javascript":
            return cls()._validate_js_node(code)
        elif lang in ("typescript", "cpp", "go"):
            return cls()._validate_brackets_and_quotes(code)
        elif lang == "html":
            return cls()._validate_html(code)
        else:
            lang_display = language.capitalize() if language else "This language"
            return {
                "syntax_valid": False,
                "errors": [{"line": 1, "message": f"{lang_display} is currently not supported by CodeGuard AI, but support will be added soon!"}]
            }

code_validator_service = CodeValidatorService()
