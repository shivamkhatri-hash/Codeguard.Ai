# Smart Code Inspection Platform with Vulnerability Detection System
## Complete Code-Accurate System Architecture Specification

---

## 1. SYSTEM OVERVIEW

The Smart Code Inspection Platform is an automated code review and vulnerability detection web application designed for multi-language software security analysis (supporting Python, Java, JavaScript, TypeScript, C++, Go, and HTML). The system features a modern **React/Vite single-page frontend** and a high-performance **FastAPI backend**. Code submissions undergo static syntax validation via AST parsers (`ast` and `javalang`) followed by parallel multi-agent analysis (`CodeAnalysisAgent` and `SecurityVulnerabilityAgent`) coordinated by an asynchronous orchestrator (`AgentOrchestrator`). Findings are matched against an in-memory TF-IDF + Cosine Similarity RAG knowledge base grounded in OWASP Top 10 standards to supply context-aware remediations via Google Gemini 2.5 Flash (with deterministic offline rule-engine fallbacks). Results are persisted across MongoDB Atlas and SQLite dual-storage, presented interactively on a developer dashboard, streamed as enterprise ReportLab PDF reports, and analyzed via an admin governance panel.

---

## 2. ENTRY POINT

### User Interaction
1. **Interactive Code Editor**: Developers paste source code directly into the browser editor and select the language.
2. **File Upload**: Developers drag and drop single source files (`.py`, `.java`, `.js`, `.ts`, `.cpp`, `.go`, `.html`).
3. **Conversational AI Assistant**: Developers query an interactive RAG-powered chatbot for explanation and refactoring help.
4. **Admin Dashboard**: System administrators log in to manage user roles/status and view platform security analytics.

### Entry Points & Endpoints
* **Frontend Entry Point**: [`infy/FrontEnd/src/main.jsx`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/main.jsx) rendering [`App.jsx`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/App.jsx).
* **Main Frontend Views/Pages**:
  * [`LandingPage.jsx`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/pages/LandingPage.jsx): Product showcase and features.
  * [`CodeReview.jsx`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/pages/CodeReview.jsx): Interactive code editor, progress indicator, finding cards, and AI chat.
  * [`Dashboard.jsx`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/pages/Dashboard.jsx): Developer overview of recent submissions, metrics, and health scores.
  * [`AdminDashboard.jsx`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/pages/AdminDashboard.jsx): User management, audit logs, and threat breakdown graphs.
* **Backend Entry Point**: [`infy/BackEnd/app/main.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/main.py) (FastAPI app listening on port 8000).
* **Main API Endpoints**:
  * `POST /api/code/submit`: Submits code snippet JSON payload.
  * `POST /api/code/upload`: Uploads a single source code file via multipart Form-Data.
  * `GET /api/analysis/{analysis_id}`: Retrieves analysis status and findings.
  * `GET /api/analysis`: Retrieves analysis submission history.
  * `POST /api/remediation/{analysis_id}`: Triggers or fetches AI/deterministic code remediation.
  * `GET /api/summary/{analysis_id}`: Generates Pull Request review summary, Health Score, and fix checklist.
  * `POST /api/assistant/chat`: RAG-grounded conversational Q&A assistant.
  * `GET /api/report/pdf/{analysis_id}`: Downloads native PDF security report.
  * `POST /api/auth/login` & `POST /api/auth/signup`: Authenticates users and issues JWTs.
  * `GET /api/admin/stats` & `GET /api/admin/users`: Admin analytics and management.

### Submission Lifecycle
When a user submits code:
1. Frontend calls `submitCode` or `uploadCodeFile` REST endpoint in [`app/api/code.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/api/code.py).
2. Backend validates metadata and runs language syntax parsing via `code_validator_service` in [`app/services/code_validator.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/code_validator.py).
3. If valid, `agent_orchestrator` in [`app/services/agent_orchestrator.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agent_orchestrator.py) executes `CodeAnalysisAgent` and `SecurityVulnerabilityAgent` concurrently using `asyncio.gather()`.
4. Analysis findings are enriched with RAG recommendations, stored in the active database (MongoDB Atlas or SQLite), and returned synchronously to the frontend to render the inspection report.

---

## 3. FRONTEND ARCHITECTURE

* **Framework**: React 18 with Vite 6.
* **Styling**: TailwindCSS 3 with custom glassmorphism utilities and dark theme (`#050b14`).
* **API Communication**: Asynchronous HTTP `fetch` client encapsulated in [`infy/FrontEnd/src/services/api.js`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/services/api.js).
* **Realtime Mechanism**: Standard synchronous HTTP REST polling / page updates (No WebSockets present).
* **File Upload**: HTML `<input type="file">` handled via `FormData` in [`FileUpload.jsx`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/components/FileUpload.jsx).
* **Dashboard / Inspection Interaction**: Tabs for Severity Breakdown, AI Remediation side-by-side diffs, PR Summary markdown, PDF download link, and slide-over AI Chat assistant.

```
FrontEnd
 ├── src
 │    ├── App.jsx                        (Root component & state-based router)
 │    ├── main.jsx                       (Vite entry mount)
 │    ├── index.css                      (Tailwind CSS & custom theme definitions)
 │    ├── pages
 │    │    ├── LandingPage.jsx           (Marketing hero, features, & call-to-action)
 │    │    ├── CodeReview.jsx            (Core inspection workspace)
 │    │    ├── Dashboard.jsx             (Developer dashboard & metrics)
 │    │    └── AdminDashboard.jsx        (Admin analytics & user governance)
 │    ├── components
 │    │    ├── Navbar.jsx                (Header navigation & user status)
 │    │    ├── CodeEditor.jsx            (Syntax-highlighted code editor)
 │    │    ├── FileUpload.jsx            (Drag-and-drop file upload handler)
 │    │    ├── ResultCard.jsx            (Findings list, diff view, & PR summary)
 │    │    ├── ConversationalAssistant.jsx (Floating AI chat drawer)
 │    │    ├── AnalysisProgress.jsx      (Multi-step analysis spinner)
 │    │    ├── LanguageSelector.jsx      (Dropdown for target language)
 │    │    ├── AuthModal.jsx             (Sign up / Login modal)
 │    │    └── ErrorBoundary.jsx        (React error boundary wrapper)
 │    └── services
 │         └── api.js                    (REST API client & auth storage manager)
 ├── package.json
 └── vite.config.js
```

---

## 4. BACKEND ARCHITECTURE

* **Framework**: FastAPI 0.100+ running on Uvicorn ASGI server.
* **API / Router Structure**: Modular APIRouters mounted under the `/api` prefix in [`app/main.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/main.py#L40-L47).
* **Background Workers / Tasks**: In-memory asynchronous concurrency via Python `asyncio.gather()` and `asyncio.to_thread()`. (No external Celery/Redis queue).
* **Database Access**: Hybrid Storage Layer with MongoDB Atlas (`pymongo`) as primary and local SQLite (`sqlite3`) as fallback.
* **Authentication**: JWT token generation/validation (`python-jose`) and password hashing (`passlib` with `bcrypt`).
* **File Handling**: `file_service` utilizing FastAPI `UploadFile` with extension and size checks (5MB cap).
* **Report Generation**: Native binary PDF generation using `reportlab`.
* **External LLM Integration**: Google GenAI SDK (`google-genai` package) accessing `gemini-2.5-flash`.

```
Backend
 ├── app
 │    ├── main.py                        (FastAPI application entrypoint & middleware)
 │    ├── core
 │    │    ├── config.py                 (Pydantic settings & env configurations)
 │    │    ├── security.py               (Bcrypt hashing & JWT utilities)
 │    │    └── rag_kb.py                 (OWASP Top 10 & secure coding document store)
 │    ├── api
 │    │    ├── code.py                   (POST /api/code/submit, POST /api/code/upload)
 │    │    ├── analysis.py               (GET /api/analysis/{id}, DELETE /api/analysis/{id})
 │    │    ├── remediation.py            (POST /api/remediation/{id})
 │    │    ├── summary.py                (GET/POST /api/summary/{id})
 │    │    ├── assistant.py              (POST /api/assistant/chat)
 │    │    ├── report.py                 (GET /api/report/pdf/{id})
 │    │    ├── auth.py                   (POST /api/auth/signup, POST /api/auth/login)
 │    │    └── admin.py                  (GET /api/admin/users, GET /api/admin/stats)
 │    ├── services
 │    │    ├── agent_orchestrator.py     (Concurrent multi-agent execution orchestrator)
 │    │    ├── code_validator.py         (AST Python/Java parsers & HTML syntax checkers)
 │    │    ├── file_service.py           (File upload decoding & size validation)
 │    │    ├── rag_service.py            (TF-IDF Vectorizer & Cosine Similarity search)
 │    │    ├── storage_service.py        (SQLite persistence & fallback manager)
 │    │    ├── mongodb_storage_service.py(MongoDB Atlas cloud database driver)
 │    │    ├── pdf_report_service.py     (ReportLab PDF layout builder)
 │    │    └── agents
 │    │         ├── code_analysis_agent.py         (Quality & Code Smell Agent)
 │    │         ├── security_vulnerability_agent.py(OWASP Vulnerability Agent)
 │    │         ├── remediation_agent.py           (AI/Deterministic Remediation Agent)
 │    │         ├── pr_summary_agent.py            (Health Score & PR Summary Agent)
 │    │         └── assistant_agent.py             (Conversational Q&A Assistant Agent)
 │    └── schemas
 │         ├── code.py                   (Code submission Pydantic models)
 │         ├── analysis.py               (Finding & Analysis Pydantic models)
 │         ├── remediation.py            (Remediation Pydantic models)
 │         ├── summary.py                (PR Summary & Checklist Pydantic models)
 │         ├── assistant.py              (Chat message & RAG source Pydantic models)
 │         └── auth.py                   (Auth & Admin statistics Pydantic models)
 ├── data
 │    └── analyses.db                    (SQLite local database)
 ├── Dockerfile
 └── requirements.txt
```

---

## 5. MULTI-AGENT ARCHITECTURE

The repository implements **5 distinct agents** and **1 orchestrator**:

```
                              AgentOrchestrator
                             (agent_orchestrator.py)
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼ (Parallel / asyncio.gather)                  ▼ (Parallel / asyncio.gather)
        CodeAnalysisAgent                            SecurityVulnerabilityAgent
    (code_analysis_agent.py)                     (security_vulnerability_agent.py)
                 │                                             │
                 └──────────────────────┬──────────────────────┘
                                        ▼
                               Stored Findings
                                        │
      ┌─────────────────────────────────┼─────────────────────────────────┐
      ▼ (On Demand / Post-Analysis)     ▼ (On Demand / Post-Analysis)     ▼ (Interactive Q&A)
  RemediationAgent                   PRSummaryAgent                 ConversationalAssistantAgent
(remediation_agent.py)            (pr_summary_agent.py)                (assistant_agent.py)
```

---

### Agent Specifications

#### 1. CodeAnalysisAgent
* **File/Module**: [`app/services/agents/code_analysis_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/code_analysis_agent.py)
* **Purpose**: Analyzes source code for structural code smells, maintainability issues, nesting complexity, missing documentation, and anti-patterns.
* **Input**: Source code string (`code`), programming language string (`language`).
* **Processing**:
  * For Python: Executes AST visitor `PythonCodeQualityAnalyzer` checking mutable default arguments, excessive function length (>50 lines), missing docstrings, broad exception handlers, and nesting depth (>3 levels).
  * For Java: Executes `javalang` AST visitor `JavaCodeQualityAnalyzer` checking public class/method Javadocs, parameter counts (>5), method lengths, deep nesting, and empty catch blocks.
  * For JS/TS/C++/Go: Runs regex pattern checks (`_analyze_patterns`).
  * Consults `rag_service.get_remediation()` for standard quality recommendations.
* **Output**: `List[Finding]` (type: `"code_smell"`).
* **Who Calls It**: Called by `AgentOrchestrator._run_quality_agent()`.
* **What It Calls Next**: `rag_service.get_remediation()`.
* **Execution Mode**: **Parallel** (runs concurrently alongside `SecurityVulnerabilityAgent`).

#### 2. SecurityVulnerabilityAgent
* **File/Module**: [`app/services/agents/security_vulnerability_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/security_vulnerability_agent.py)
* **Purpose**: Detects security vulnerabilities matching OWASP Top 10 categories.
* **Input**: Source code string (`code`), programming language string (`language`).
* **Processing**:
  * For Python: AST visitor `PythonSecurityAnalyzer` detecting `eval()`/`exec()`, command injection (`os.system`, `subprocess` with `shell=True`), insecure deserialization (`pickle.loads`, `yaml.load`), weak hashing (`md5`, `sha1`), SQL injection via `.format()`, f-strings, or string concatenation, and hardcoded secrets.
  * For Java: `javalang` AST visitor `JavaSecurityAnalyzer` detecting JDBC/JPA SQL injection, `Runtime.exec()`, `ProcessBuilder`, hardcoded secrets in fields/variables, weak `MessageDigest`, Servlet XSS, and unauthenticated endpoints.
  * Multi-Language Fallback: Multi-language regex engines for JS/TS, C++ (buffer overflows `strcpy`/`gets`), Go, and HTML.
  * Queries `rag_service.get_remediation()` for standard security fix recommendations.
* **Output**: `List[Finding]` (type: `"security_vulnerability"`).
* **Who Calls It**: Called by `AgentOrchestrator._run_security_agent()`.
* **What It Calls Next**: `rag_service.get_remediation()`.
* **Execution Mode**: **Parallel** (runs concurrently alongside `CodeAnalysisAgent`).

#### 3. AgentOrchestrator
* **File/Module**: [`app/services/agent_orchestrator.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agent_orchestrator.py)
* **Purpose**: Coordinates concurrent execution of quality and security agents, deduplicates findings, calculates software architecture metrics (LOC, function count, class count, cyclomatic complexity index), and attaches summary findings.
* **Input**: `code`, `language`.
* **Processing**: Triggers `asyncio.gather(_run_quality_agent(), _run_security_agent())`, deduplicates findings by `(type, title, line)`, sorts findings by line number, computes cyclomatic complexity metrics via regex, and inserts a `"Software Architecture Metrics"` finding at index 0.
* **Output**: Combined `List[Finding]`.
* **Who Calls It**: `submit_code()` or `upload_code()` in [`app/api/code.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/api/code.py).
* **What It Calls Next**: Returns findings to the API router to be saved in `storage_service`.
* **Execution Mode**: Asynchronous Orchestrator.

#### 4. RemediationAgent
* **File/Module**: [`app/services/agents/remediation_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/remediation_agent.py)
* **Purpose**: Generates side-by-side corrected code snippets, explanations, and safety rationale for detected vulnerabilities.
* **Input**: `Finding` object, source `code`, `language`.
* **Processing**:
  * Step 1: Checks SQLite/MongoDB cache for previously generated remediations.
  * Step 2: If uncached, retrieves RAG context from `rag_service`.
  * Step 3: Invokes Google Gemini 2.5 Flash LLM API via `google.genai.Client`.
  * Step 4: If LLM is unavailable or fails (e.g. quota limit, network error), executes `_fallback_remediation()`, a deterministic rule-engine implementing language-specific transformations for SQLi, XSS, Hardcoded Secrets, Debug Mode, Docstrings, and Nesting Complexity without hallucinating code.
* **Output**: Remediation dictionary containing `original_code`, `corrected_code`, `explanation`, `why_it_works`, `benefits`, and `refactoring_suggestions`.
* **Who Calls It**: Endpoint `POST /api/remediation/{analysis_id}` in [`app/api/remediation.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/api/remediation.py) and PDF generator [`app/api/report.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/api/report.py).
* **What It Calls Next**: `rag_service.query()` and `google.genai.Client.models.generate_content()`.
* **Execution Mode**: Sequential per finding batch.

#### 5. PRSummaryAgent
* **File/Module**: [`app/services/agents/pr_summary_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/pr_summary_agent.py)
* **Purpose**: Compiles all analysis findings into a structured Pull Request style review summary with an executive overview, mathematical Code Health Score (0-100), merge verdict, and prioritized fix roadmap.
* **Input**: `analysis_id`, `findings`, `code`, `language`.
* **Processing**:
  * Calculates `health_score = max(0, min(100, 100 - (High*15) - (Med*8) - (Low*3)))`.
  * Determines verdict: `"Approved (Safe to Merge)"`, `"Needs Attention"`, or `"Blocked (Critical Security Risks Detected)"`.
  * Builds ranked `PrioritizedFix` checklist with exact line numbers and concise recommendations.
  * Optionally refines executive overview using Gemini 2.5 Flash if available.
  * Formats a complete Markdown PR comment.
* **Output**: `PRSummaryResponse`.
* **Who Calls It**: Endpoint `GET /api/summary/{analysis_id}` and `pdf_report_service.py`.
* **What It Calls Next**: `google.genai.Client` (optional enhancement).
* **Execution Mode**: Sequential.

#### 6. ConversationalAssistantAgent
* **File/Module**: [`app/services/agents/assistant_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/assistant_agent.py)
* **Purpose**: Provides an interactive chat interface for developers to ask follow-up questions about flagged vulnerabilities or general secure coding practices.
* **Input**: User `query`, `analysis_id`, `language`, conversation `history`.
* **Processing**:
  * Step 0: Handles greetings ("hi", "hello") with a domain-specific menu.
  * Step 1: Queries `rag_service.query()` retrieving top-3 grounded knowledge base passages.
  * Step 2: Retrieves past submission code and findings from `storage_service` if `analysis_id` is supplied.
  * Step 3: Passes prompt with system instructions, RAG context, and history to Gemini 2.5 Flash (`gemini-2.5-flash`).
  * Step 4: If LLM is offline or query is off-topic (e.g., weather, sports), enforces guardrails and provides grounded RAG fallback answers.
* **Output**: `ChatResponse` containing answer text and cited RAG sources.
* **Who Calls It**: Endpoint `POST /api/assistant/chat` in [`app/api/assistant.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/api/assistant.py).
* **What It Calls Next**: `rag_service.query()`, `storage_service.get_analysis()`, and `google.genai.Client`.
* **Execution Mode**: Sequential.

---

## 6. RAG / KNOWLEDGE BASE

* **Implementation File**: [`app/services/rag_service.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/rag_service.py)
* **Knowledge Document Store**: [`app/core/rag_kb.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/core/rag_kb.py) (`SECURE_CODING_DOCUMENTS` array containing 14 detailed OWASP Top 10 & code quality documents).
* **Ingestion Process**: Loaded on startup in `RAGService._initialize_index()`. Converts document title, content, and tags into normalized text.
* **Chunking**: Dual-level chunking:
  1. Full document text chunking.
  2. Paragraph-level chunking (splits content by double newlines `\n\n`).
* **Embedding / Vectorization**: Custom in-memory TF-IDF Vectorizer using `scikit-learn`: `TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True)`.
* **Vector Database**: **None (No external vector DB like Pinecone/Chroma is used)**. The TF-IDF sparse matrix is stored in memory as `self.matrix`.
* **Retrieval Method**: Cosine similarity algorithm via `sklearn.metrics.pairwise.cosine_similarity(query_vec, self.matrix)`.
* **Similarity Thresholding & Keyword Pre-filtering**:
  * Minimum score filter: `score >= 0.15` for chat, `score >= 0.20` for remediation.
  * Targeted topic matching (`_get_topic_keywords`): Matches finding titles (e.g. SQL Injection, XSS, Hardcoded Secrets) directly to tags before similarity scoring to prevent false-positive context retrieval.
* **Which Agents Use RAG**:
  1. `CodeAnalysisAgent`: Calls `rag_service.get_remediation()` for code smell remediation text.
  2. `SecurityVulnerabilityAgent`: Calls `rag_service.get_remediation()` for security vulnerability recommendations.
  3. `RemediationAgent`: Queries RAG knowledge base for LLM context prompting.
  4. `ConversationalAssistantAgent`: Queries RAG knowledge base for context-grounded developer Q&A.

### Complete RAG Flow Trace

```
Finding / Developer Query
          │
          ▼
   rag_service.get_remediation() / query()
          │
   (Topic Keyword Matching: "sql injection" -> ["sql injection", "parameterized query"])
          │
          ▼
   TfidfVectorizer.transform([cleaned_query + language])
          │
          ▼
   cosine_similarity(query_vector, in_memory_tfidf_matrix)
          │
          ▼
   Filter top-k results by score (> 0.15 / 0.20 threshold)
          │
          ▼
   Return grounded RAG documents (Title, Content, Score, Category)
          │
          ▼
   Inject into Agent Prompt / Return to User UI
```

---

## 7. DATABASE / STORAGE

### Database Technologies
* **Primary Database**: **MongoDB Atlas Cloud Database** (`pymongo.MongoClient`), connecting to database `smartcodeinspection`.
* **Fallback Database**: **SQLite** local database (`data/analyses.db`), managed by `SQLiteStorageService`.
* **Connection Lifecycle**: On startup, [`app/services/storage_service.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/storage_service.py#L386-L392) attempts to initialize `MongoDBStorageService`. If network/MongoDB credentials fail, it seamlessly falls back to `SQLiteStorageService`.

### Database Schemas & Collections

#### MongoDB Collections / SQLite Tables:
1. `analyses`:
   * `analysis_id` (String, Primary Key / Unique Index)
   * `filename` (String)
   * `status` (String: `"completed"` | `"failed"`)
   * `language` (String)
   * `code` (String, full source text)
   * `syntax_valid` (Boolean)
   * `errors` (JSON array of syntax error objects)
   * `findings` (JSON array of finding objects)
   * `created_at` (ISO Timestamp string)
2. `remediations`:
   * `analysis_id` (String)
   * `finding_key` (String, format: `title|line`)
   * `remediation` (JSON object storing code fix, explanation, why it works)
   * `created_at` (ISO Timestamp string)
3. `users`:
   * `user_id` (String, Unique Key)
   * `email` (String, Unique Index)
   * `hashed_password` (String, Bcrypt hash)
   * `full_name` (String)
   * `role` (String: `"developer"` | `"admin"`)
   * `is_active` (Boolean / Integer flag)
   * `created_at` (ISO Timestamp string)

### Storage Interaction Diagram

```
Application (FastAPI API Routers)
    ↓
Storage Abstraction Layer (app/services/storage_service.py)
    ↓
┌───────────────────────────────────────┬───────────────────────────────────────┐
│ Primary: MongoDB Atlas Cloud         │ Fallback: Local SQLite Database       │
│ Collections:                          │ Tables:                               │
│  • analyses                           │  • analyses                           │
│  • remediations                       │  • remediations                       │
│  • users                              │  • users                              │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

---

## 8. COMPLETE END-TO-END DATA FLOW

Below is the step-by-step trace of a developer submitting a source file (`vulnerable.py`) through the system:

```
Developer
   │ (Submits file / pastes snippet in UI)
   ▼
React / Vite Frontend (CodeReview.jsx)
   │
   │ POST /api/code/submit or POST /api/code/upload
   ▼
FastAPI API Layer (app/api/code.py)
   │
   ├──► CodeValidatorService (app/services/code_validator.py)
   │     - Validates extension, size limits (<5MB), non-empty
   │     - Parses Python AST (ast.parse) -> syntax_valid: True
   │
   ├──► AgentOrchestrator (app/services/agent_orchestrator.py)
   │     │
   │     ├─► asyncio.gather()
   │     │    ├──► CodeAnalysisAgent (app/services/agents/code_analysis_agent.py)
   │     │    │     - AST scan & regex scan for code smells
   │     │    │     - Queries rag_service for standard recommendations
   │     │    │
   │     │    └──► SecurityVulnerabilityAgent (app/services/agents/security_vulnerability_agent.py)
   │     │          - AST scan & regex scan for OWASP vulnerabilities (e.g. SQLi, Hardcoded Secrets)
   │     │          - Queries rag_service for standard recommendations
   │     │
   │     ├──► Deduplicates & sorts findings by line number
   │     └──► Computes Cyclomatic Complexity & LOC metrics -> appends Metrics Finding
   │
   ├──► Storage Layer (app/services/storage_service.py)
   │     - Saves analysis record to MongoDB Atlas / SQLite database
   │
   ▼
React Frontend UI (ResultCard.jsx)
   │ Displays Findings, Severity Badges, & Metrics
   │
   ├──► User Clicks "Generate AI Remediation"
   │     │ POST /api/remediation/{analysis_id}
   │     ▼
   │    RemediationAgent (app/services/agents/remediation_agent.py)
   │     - Checks DB cache -> If uncached, queries RAG context
   │     - Calls Gemini 2.5 Flash LLM API -> (Fallback: Deterministic Rule Engine)
   │     - Saves remediation to DB & returns side-by-side corrected diff to UI
   │
   ├──► User Clicks "PR Summary" / "Download PDF"
   │     │ GET /api/summary/{analysis_id}  |  GET /api/report/pdf/{analysis_id}
   │     ▼
   │    PRSummaryAgent & PDFReportService
   │     - Calculates Health Score (e.g. 70/100) & Verdict ("Blocked")
   │     - Renders Markdown PR Comment / Streams ReportLab PDF download
   │
   └──► User Opens Assistant Drawer
         │ POST /api/assistant/chat
         ▼
        ConversationalAssistantAgent (app/services/agents/assistant_agent.py)
         - Retrieves top-3 RAG docs + past submission context
         - Queries Gemini 2.5 Flash -> Returns grounded chat response
```

---

## 9. EXTERNAL DEPENDENCIES

### A. Required at Runtime

#### Python (Backend)
* `fastapi` (v0.100+): Web framework for API endpoints.
* `uvicorn[standard]` (v0.22+): ASGI server.
* `pydantic` (v2.0+): Request/response schema validation.
* `pymongo` (v4.5+): MongoDB Atlas cloud database client.
* `scikit-learn` (v1.3+): TF-IDF vectorization & Cosine Similarity for RAG.
* `numpy` (v1.24+): Vector arrays for similarity calculation.
* `javalang` (v0.13+): Java AST parser for Java static code analysis.
* `reportlab` (v4.0+): PDF report generation library.
* `python-jose[cryptography]`: JWT authentication.
* `passlib[bcrypt]`: Password hashing.
* `python-multipart`: File upload processing.
* `python-dotenv`: Environment variable management.

#### JavaScript / React (Frontend)
* `react` & `react-dom` (v18.3+): UI component library.
* `lucide-react`: Modern icons.
* `prismjs`: Code syntax highlighting.
* `react-simple-code-editor`: Interactive browser code editor.

---

### B. Development-Only

* `vite` (v6.0+): Frontend build tool and development server.
* `@vitejs/plugin-react`: React plugin for Vite.
* `tailwindcss` (v3.4+), `autoprefixer`, `postcss`: CSS styling framework.

---

### C. Optional / Fallback Services

* `google-genai` (v0.1+): Google Gemini 2.5 Flash LLM API SDK.
  * *Status*: Used when `GEMINI_API_KEY` is present. If missing or rate-limited (HTTP 429), system gracefully falls back to deterministic rule engines and local RAG context without crashing.
* `MongoDB Atlas`: Cloud Database instance.
  * *Status*: Used when online network connection succeeds. If unavailable, system automatically falls back to local SQLite database ([`data/analyses.db`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/data/analyses.db)).
* `Node.js` runtime CLI (`node -c`):
  * *Status*: Optional subprocess syntax validator for JavaScript files. If Node CLI is not installed on host machine, falls back to `_validate_brackets_and_quotes()`.

---

## 10. ACTUAL FILE-TO-COMPONENT MAPPING

| Architecture Component | Actual File/Folder | Responsibility |
|---|---|---|
| **Frontend Workspace** | [`infy/FrontEnd/src/App.jsx`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/App.jsx) | Root state container, tab router, and auth modal trigger |
| **API Client** | [`infy/FrontEnd/src/services/api.js`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/services/api.js) | Asynchronous REST HTTP client & local token storage |
| **Frontend UI Components** | [`infy/FrontEnd/src/components/`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/FrontEnd/src/components/) | `CodeEditor`, `FileUpload`, `ResultCard`, `ConversationalAssistant` |
| **Backend Main API** | [`infy/BackEnd/app/main.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/main.py) | FastAPI instantiation, CORS middleware, & router registrations |
| **API Endpoints Layer** | [`infy/BackEnd/app/api/`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/api/) | Routes for `code`, `analysis`, `remediation`, `summary`, `assistant`, `report`, `auth`, `admin` |
| **Syntax Validator** | [`infy/BackEnd/app/services/code_validator.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/code_validator.py) | AST Python/Java syntax checking & HTML balancer |
| **Multi-Agent Orchestrator** | [`infy/BackEnd/app/services/agent_orchestrator.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agent_orchestrator.py) | Concurrent agent gather, deduplication, & metrics calculation |
| **Code Analysis Agent** | [`infy/BackEnd/app/services/agents/code_analysis_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/code_analysis_agent.py) | AST & Regex static code smell and quality analyzer |
| **Security Agent** | [`infy/BackEnd/app/services/agents/security_vulnerability_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/security_vulnerability_agent.py) | AST & Regex OWASP Top 10 vulnerability detector |
| **Remediation Agent** | [`infy/BackEnd/app/services/agents/remediation_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/remediation_agent.py) | Gemini LLM & deterministic rule-engine code fix generator |
| **PR Summary Agent** | [`infy/BackEnd/app/services/agents/pr_summary_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/pr_summary_agent.py) | Code Health Score math, verdict, & Markdown PR comment builder |
| **Assistant Chat Agent** | [`infy/BackEnd/app/services/agents/assistant_agent.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/agents/assistant_agent.py) | RAG-grounded conversational Q&A assistant |
| **RAG Knowledge Base** | [`infy/BackEnd/app/core/rag_kb.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/core/rag_kb.py) | OWASP standards & secure coding guidelines document store |
| **RAG Vector Engine** | [`infy/BackEnd/app/services/rag_service.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/rag_service.py) | TF-IDF vectorizer, chunking, & Cosine Similarity search |
| **Database Access Layer** | [`infy/BackEnd/app/services/storage_service.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/storage_service.py) | Dual-storage controller (MongoDB Atlas + SQLite fallback) |
| **PDF Report Generator** | [`infy/BackEnd/app/services/pdf_report_service.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/services/pdf_report_service.py) | ReportLab PDF layout builder & streamer |
| **Auth & Security Core** | [`infy/BackEnd/app/core/security.py`](file:///e:/-Development-of-Smart-Code-Inspection-Platform-with-Vulnerability-Detection-System-main/infy/BackEnd/app/core/security.py) | JWT token creation/decoding & Bcrypt password hashing |

---

## 11. ARCHITECTURE DIAGRAM SPECIFICATION

For a major-project college presentation slide, use this 8-block clean specification:

```
┌─────────────────┐       HTTP / REST (JSON)        ┌─────────────────┐
│ 1. USER / DEV   ├────────────────────────────────►│ 2. REACT / VITE │
│   (Web Browser) │◄────────────────────────────────┤   FRONTEND UI   │
└─────────────────┘      Synchronous Response       └────────┬────────┘
                                                             │
                                                   HTTP REST │ JSON / Form-Data
                                                             ▼
                                                    ┌─────────────────┐
                                                    │ 3. FASTAPI API  │
                                                    │     GATEWAY     │
                                                    └────────┬────────┘
                                                             │
                                               Async Call    │ (Synchronous)
                                                             ▼
                                                    ┌─────────────────┐
                                                    │ 4. MULTI-AGENT  │
                                                    │   ORCHESTRATOR  │
                                                    └────────┬────────┘
                                                             │
                                          Parallel asyncio   │ gather()
                                     ┌───────────────────────┴───────────────────────┐
                                     ▼                                               ▼
                           ┌──────────────────┐                            ┌──────────────────┐
                           │ 5. CODE ANALYSIS │                            │ 6. SECURITY      │
                           │      AGENT       │                            │   VULNERABILITY  │
                           │ (Quality Smells) │                            │      AGENT       │
                           └────────┬─────────┘                            └────────┬─────────┘
                                    │                                               │
                                    └───────────────────────┬───────────────────────┘
                                                            │ Exact Topic Query / TF-IDF Vector
                                                            ▼
                                                   ┌─────────────────┐
                                                   │ 7. RAG ENGINE & │
                                                   │   KNOWLEDGE BASE│
                                                   │ (OWASP Top 10)  │
                                                   └────────┬────────┘
                                                            │
                                         Save / Read        │ Data Models
                                                            ▼
                                                   ┌─────────────────┐
                                                   │ 8. DUAL-STORAGE │
                                                   │ (MongoDB Atlas  │
                                                   │   / SQLite)     │
                                                   └─────────────────┘
```

### Presentation Block Details Table

| Block # | Block Name | Content Inside Block | Arrow Direction & Target | Arrow Label | Connection Type |
|---|---|---|---|---|---|
| **1** | **User / Developer** | Web Browser, Code Inputs | `1 → 2` | Submits Code / View Reports | Synchronous |
| **2** | **React / Vite Frontend** | `CodeEditor`, `ResultCard`, `ConversationalAssistant` | `2 → 3` | REST API Requests (`/api/code/submit`, `/api/remediation`) | Synchronous HTTP |
| **3** | **FastAPI Backend Gateway** | API Routers, `CodeValidator`, `PDFReportService` | `3 → 4` | Invokes Code Analysis Job | Synchronous |
| **4** | **Multi-Agent Orchestrator** | `AgentOrchestrator` (`asyncio.gather`) | `4 → 5` & `4 → 6` | Triggers Analysis Agents | **Parallel (Concurrent)** |
| **5** | **Code Analysis Agent** | Python `ast` & Java `javalang` Quality Parsers | `5 → 7` | Queries RAG Recommendations | Synchronous |
| **6** | **Security Vulnerability Agent**| Python/Java AST & Multi-language OWASP Scanners | `6 → 7` | Queries RAG Recommendations | Synchronous |
| **7** | **RAG Engine & Knowledge Base**| TF-IDF Vectorizer, Cosine Similarity, OWASP Docs | `7 → 8` | Returns Grounded Context & Saves Analysis | Synchronous |
| **8** | **Dual-Storage Engine** | MongoDB Atlas Cloud + Local SQLite Database | `8 → 2` | Returns Findings & Health Score to UI | Synchronous |

---

## 12. ARCHITECTURE ACCURACY CHECK

### 1. Which components are definitely implemented?
* React 18 / Vite 6 Single Page Application with interactive code editor, drag-and-drop file upload, diff views, and slide-over AI assistant.
* FastAPI backend with full CORS, exception handlers, and modular API routers (`code`, `analysis`, `remediation`, `summary`, `assistant`, `report`, `auth`, `admin`).
* AST static code analysis engines for Python (`ast`) and Java (`javalang`) alongside multi-language regex engines for JS/TS, C++, Go, and HTML.
* Asynchronous `AgentOrchestrator` executing `CodeAnalysisAgent` and `SecurityVulnerabilityAgent` concurrently via `asyncio.gather()`.
* In-memory TF-IDF Vectorizer + Cosine Similarity RAG knowledge base grounded in 14 OWASP Top 10 & code quality documents.
* AI Remediation Generator via Google Gemini 2.5 Flash with deterministic offline rule-engine fallbacks.
* PR Summary Agent with mathematical Health Score (0-100), verdict decision logic, prioritized fix roadmap, and Markdown PR comment generation.
* Enterprise ReportLab PDF report generation and streaming module.
* MongoDB Atlas Cloud Database primary storage with automatic local SQLite fallback.
* JWT Authentication, Bcrypt password hashing, Role-Based Access Control (Developer vs Admin), and Admin Security Analytics.

### 2. Which components are partially implemented?
* **TypeScript, C++, Go, and HTML AST Parsing**: Python and Java use full AST syntax trees (`ast` and `javalang`). TypeScript, C++, Go, and HTML currently use regex pattern matching and structural bracket/quote/tag validation.

### 3. Which components are planned but not connected?
* **GitHub Repository Cloning / Webhook Scanner**: The system inspects uploaded single files or pasted code snippets. GitHub repository URLs or GitHub Webhook integrations are planned future features and not present in the code.
* **External Vector Database (Pinecone / Chroma)**: Vector search is performed via in-memory TF-IDF sparse matrix and Cosine Similarity in `scikit-learn`.

### 4. Which components should NOT be shown on a presentation architecture diagram?
* Do **NOT** show WebSockets or Realtime Sockets (the application relies on standard HTTP REST).
* Do **NOT** show Redis / Celery Background Queues (concurrency is handled in-process via Python `asyncio`).
* Do **NOT** show GitHub OAuth or Git Clone services (code is uploaded directly).
* Do **NOT** show Pinecone / Chroma Vector DBs (RAG uses TF-IDF with `scikit-learn` in memory).

### 5. What is the simplest accurate architecture diagram for this project?
The simplest accurate presentation architecture consists of **6 Core Blocks**:
`Developer Browser (React UI)` ➔ `FastAPI Backend Gateway` ➔ `Multi-Agent Orchestrator (Parallel Quality & Security Agents)` ➔ `TF-IDF / Cosine RAG Engine (OWASP KB)` ➔ `Gemini 2.5 Flash / Deterministic Remediation Engine` ➔ `Dual Database (MongoDB Atlas / SQLite)`.
