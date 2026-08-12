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
        Validates HTML tag structure using Python's HTMLParser.
        """
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

    @classmethod
    def validate_code(cls, code: str, language: str) -> Dict[str, Any]:
        """
        Main entrypoint for syntax validation.
        """
        lang = language.lower()
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
            return {
                "syntax_valid": False,
                "errors": [{"line": 1, "message": f"Unsupported language '{language}' for syntax validation."}]
            }

code_validator_service = CodeValidatorService()
