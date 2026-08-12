# RAG Knowledge Base - OWASP Top 10 & Secure Coding Guidelines

SECURE_CODING_DOCUMENTS = [
    {
        "title": "SQL Injection (SQLi) Prevention",
        "category": "Security",
        "tags": ["sql injection", "sqli", "database", "python", "java", "javascript", "go", "cpp"],
        "content": """
OWASP Top 10: A03:2021-Injection. SQL Injection occurs when untrusted user input is directly concatenated or interpolated into SQL command strings. This allows attackers to manipulate SQL queries.

Prevention & Remediation Guidelines:
1. Always use parameterized queries (prepared statements) with placeholder variables instead of string concatenation.
2. For Python: Use DB-API parameter placeholders (e.g. `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`). Never use `+`, `%`, or f-strings for SQL query inputs.
3. For Java: Use `PreparedStatement` with placeholders (e.g. `PreparedStatement pstmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?"); pstmt.setInt(1, userId);`).
4. For JavaScript/TypeScript: Use query parameterized placeholders (e.g. `connection.query('SELECT * FROM users WHERE id = ?', [userId])`).
5. For Go: Use placeholders in database driver queries (e.g. `db.Query("SELECT * FROM users WHERE id = ?", userId)`).
6. For C++: Use bind variables with database client libraries.
"""
    },
    {
        "title": "Unsafe Dynamic Code Execution Prevention",
        "category": "Security",
        "tags": ["eval", "exec", "dynamic execution", "python", "javascript", "typescript"],
        "content": """
OWASP Top 10: A06:2021-Vulnerable and Outdated Components / A03:2021-Injection. Unsafe execution of arbitrary strings as code via functions like `eval()` or `exec()` is extremely dangerous. It allows remote attackers to run system commands or access server memory if user inputs reach these functions.

Prevention & Remediation Guidelines:
1. Avoid `eval()`, `exec()`, `compile()`, and `Function()` constructors at all costs.
2. If dynamic lookup is needed, use static dictionary mappings, attribute lookups (`getattr`), or parsing safe formats like JSON.
3. If code execution is unavoidable, run it in an isolated, sandboxed container with restricted permissions.
"""
    },
    {
        "title": "Command Injection Prevention",
        "category": "Security",
        "tags": ["command injection", "subprocess", "os.system", "shell", "python", "java", "javascript", "go", "cpp"],
        "content": """
OWASP Top 10: A03:2021-Injection. Command Injection occurs when untrusted input is passed to system shell executables (like `/bin/sh` or `cmd.exe`). Using `shell=True` or `os.system` creates a shell process that executes arbitrary commands.

Prevention & Remediation Guidelines:
1. Avoid executing system shell processes whenever possible. Use programming APIs instead of shell commands.
2. If execution is necessary, set `shell=False` to pass inputs as a safe argument vector list instead of string commands.
3. For Python: Use `subprocess.run(args_list, shell=False)` rather than `os.system()` or `subprocess.run(cmd_string, shell=True)`.
4. For Java: Pass string arrays directly to `ProcessBuilder` or `Runtime.getRuntime().exec(String[] cmdarray)`.
5. For JavaScript/TypeScript: Use `execFile` or `spawn` rather than `exec` with string concatenation.
6. For Go: Use `exec.Command(name, arg...)` where arguments are passed as discrete parameters.
"""
    },
    {
        "title": "Hardcoded Secrets & Credentials Prevention",
        "category": "Security",
        "tags": ["hardcoded secrets", "credentials", "passwords", "api keys", "tokens", "python", "java", "javascript", "go", "cpp"],
        "content": """
OWASP Top 10: A02:2021-Cryptographic Failures. Hardcoding API keys, database passwords, private keys, or credentials inside source code makes them visible to anyone with code repository access, leading to credential leaks.

Prevention & Remediation Guidelines:
1. Retrieve credentials from environment variables (`os.environ` / `System.getenv()` / `process.env`) or securely managed vault services (AWS Secrets Manager, HashiCorp Vault).
2. Store environment configuration in a `.env` file and read it using standard library helpers (e.g. `dotenv` packages), ensuring `.env` is excluded in `.gitignore`.
3. Use secret scanner tools in CI/CD pipelines to block commits containing sensitive strings.
"""
    },
    {
        "title": "Insecure Deserialization Prevention",
        "category": "Security",
        "tags": ["deserialization", "pickle", "yaml", "python", "java", "javascript"],
        "content": """
OWASP Top 10: A08:2021-Software and Data Integrity Failures. Deserializing untrusted data without validation can allow attackers to instantiate arbitrary classes and execute remote commands on the host.

Prevention & Remediation Guidelines:
1. For Python: Avoid using `pickle` for loading untrusted network payloads. Use safe serialization formats like JSON or Protocol Buffers.
2. For YAML: Avoid using `yaml.load()` with the default parser. Use `yaml.safe_load()` or explicitly set `Loader=yaml.SafeLoader` to prevent arbitrary instantiation.
3. For Java: Avoid standard Java serialization for untrusted inputs. Use secure JSON/XML parsers with disabled external entity mapping.
"""
    },
    {
        "title": "Weak Hashing & Cryptography Prevention",
        "category": "Security",
        "tags": ["weak hashing", "cryptography", "md5", "sha1", "python", "java", "javascript", "go", "cpp"],
        "content": """
OWASP Top 10: A02:2021-Cryptographic Failures. Hashing algorithms like MD5 and SHA-1 have known collision vulnerabilities. They are no longer safe for cryptographic uses like password hashing, digital signatures, or integrity checks.

Prevention & Remediation Guidelines:
1. Use strong cryptographic hashing algorithms like SHA-256, SHA-3, or BLAKE2.
2. For password hashing: Use modern key derivation functions like Argon2id, bcrypt, or PBKDF2 with high iteration counts and unique salts.
3. Update outdated dependencies and legacy cryptographic algorithms.
"""
    },
    {
        "title": "Mutable Default Arguments in Python",
        "category": "Code Quality",
        "tags": ["mutable default", "python"],
        "content": """
Python Code Quality: Mutable default arguments like `y=[]` or `x={}` are evaluated only once when the function is defined. If modified, the changes persist across subsequent calls to the function.

Prevention & Remediation Guidelines:
1. Use `None` as the default value and instantiate the mutable object inside the function.
Example:
```python
# Bad
def append_to(element, target=[]):
    target.append(element)
    return target

# Good
def append_to(element, target=None):
    if target is None:
        target = []
    target.append(element)
    return target
```
"""
    },
    {
        "title": "Exception Handling Best Practices",
        "category": "Code Quality",
        "tags": ["exception handling", "bare except", "broad exception", "python", "java", "javascript", "go", "cpp"],
        "content": """
Code Quality & Maintainability: Catching general exception classes (like `except:`, `except Exception:`, or `catch (Exception e)`) masks hidden bugs, blocks system control signals (e.g. KeyboardInterrupt), and makes debugging complex.

Prevention & Remediation Guidelines:
1. Catch specific exceptions that you expect and know how to handle (e.g. `KeyError`, `IOException`, `ValueError`).
2. If broad exception handling is necessary for logging/crashes, ensure the exception is re-raised (`raise` / `throw`) or logged with full tracebacks.
3. Avoid swallowing exceptions quietly.
"""
    },
    {
        "title": "Cognitive Complexity & Deep Nesting",
        "category": "Code Quality",
        "tags": ["nesting", "complexity", "cognitive complexity", "python", "java", "javascript", "go", "cpp"],
        "content": """
Code Quality & Maintainability: Functions with deeply nested structures (if/for/while loops inside other control flows) are highly complex, difficult to read, hard to unit-test, and prone to regressions.

Prevention & Remediation Guidelines:
1. Keep the nesting depth below 3 levels.
2. Apply the "guard clauses" pattern: check error conditions first and return early, keeping the happy path flat.
3. Extract inner loop blocks or nested branches into smaller, single-responsibility functions.
"""
    },
    {
        "title": "Buffer Overflow Prevention in C++",
        "category": "Security",
        "tags": ["buffer overflow", "strcpy", "gets", "sprintf", "cpp"],
        "content": """
OWASP Top 10: A06:2021-Vulnerable and Outdated Components / Memory Safety. C/C++ lacks bounds checking on array indexing and pointer arithmetic. Using functions like `strcpy`, `strcat`, `gets`, or `sprintf` without size bounds causes buffer overflows, crashing apps and allowing malicious exploit execution.

Prevention & Remediation Guidelines:
1. Avoid `gets()`; use `fgets()` instead.
2. Use modern, bounded functions: replace `strcpy` with `strncpy`, and `strcat` with `strncat`.
3. Use safer standard C++ containers like `std::string` and `std::vector` which manage memory dynamically.
4. Enable compiler security defenses (e.g. address sanitizers, stack protectors).
"""
    },
    {
        "title": "Cross-Site Scripting (XSS) Prevention",
        "category": "Security",
        "tags": ["xss", "innerHTML", "cross-site scripting", "javascript", "typescript", "html"],
        "content": """
OWASP Top 10: A03:2021-Injection. Cross-Site Scripting (XSS) occurs when applications include untrusted data in web pages without proper validation or escaping. If data is injected into attributes like `innerHTML` or evaluated directly, it executes malicious scripts in the user's browser.

Prevention & Remediation Guidelines:
1. Use safe APIs like `textContent` or `innerText` instead of `innerHTML` when assigning text values to HTML nodes.
2. If rendering HTML is necessary, sanitize all input using libraries like DOMPurify before rendering.
3. Always HTML-encode variable values before rendering inside templates.
4. Set up a strong Content Security Policy (CSP) header.
"""
    }
]
