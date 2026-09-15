# Smart Code Inspection Platform — Backend API Service

High-performance, asynchronous multi-agent backend engine built with **FastAPI**, **ReportLab**, **MongoDB Atlas / SQLite**, **Scikit-learn (TF-IDF & Cosine Similarity)**, and **Google Gemini 2.5 Flash**.

---

## 🚀 Overview

The backend orchestrates automated static code analysis, OWASP Top 10 vulnerability detection, AI-driven remediation generation, PR-style review summary calculation, interactive RAG conversational Q&A, and native binary PDF report generation.

---

## 🛠️ Architecture & Multi-Agent Engine

```mermaid
graph TD
    Client[REST Clients / React Frontend] -->|API Requests| FastAPIRoot[FastAPI App (app/main.py)]
    FastAPIRoot --> AuthRouter[Auth & JWT Router /api/auth]
    FastAPIRoot --> AdminRouter[Admin SOC Router /api/admin]
    FastAPIRoot --> CodeRouter[Code Inspection Router /api/code]
    FastAPIRoot --> ReportRouter[PDF Engine /api/report]
    FastAPIRoot --> AssistantRouter[RAG Assistant /api/assistant]
    
    CodeRouter --> Orchestrator[Agent Orchestrator (asyncio.gather)]
    Orchestrator --> CodeAgent[1. Code Analysis Agent]
    Orchestrator --> SecAgent[2. Security Vulnerability Agent (OWASP Top 10)]
    Orchestrator --> RemAgent[3. AI Remediation Agent (Gemini 2.5 Flash)]
    Orchestrator --> PRSummaryAgent[4. PR Review Summary Agent]
    
    AssistantRouter --> RAG[5. RAG Retrieval Engine (TF-IDF Vector Space)]
    RAG --> OWASP_KB[OWASP Knowledge Documents]
    
    CodeRouter --> Storage[Hybrid Storage Layer]
    Storage --> MongoDB[(MongoDB Atlas Primary)]
    Storage --> SQLite[(SQLite Local Fallback analyses.db)]
    
    ReportRouter --> PDFEngine[ReportLab PDF Engine]
```

### Core Agents:
1. **Code Analysis Agent** (`app/services/agents/code_analysis_agent.py`): Parses AST trees to compute cognitive complexity, function length, parameter bloat, and docstring coverage.
2. **Security Vulnerability Agent** (`app/services/agents/security_vulnerability_agent.py`): Performs pattern and syntax scanning for OWASP Top 10 risks (SQLi, Command Injection, XSS, insecure deserialization, hardcoded secrets, weak hashing).
3. **AI Remediation Agent** (`app/services/agents/remediation_agent.py`): Produces finding-specific code fixes with side-by-side corrected diffs and explanations via Google Gemini 2.5 Flash (with deterministic offline rule-engine fallbacks).
4. **PR Summary Agent** (`app/services/agents/pr_summary_agent.py`): Compiles findings into an executive PR review with Health Score (0–100), risk verdict, severity breakdown, and prioritized fix roadmaps.
5. **Conversational Assistant Agent** (`app/services/agents/assistant_agent.py`): RAG-grounded conversational Q&A service with citation document retrieval.

---

## 📁 Directory Structure

```text
BackEnd/
├── app/
│   ├── api/                  # API routers (code, analysis, remediation, summary, assistant, report, auth, admin)
│   ├── core/                 # App configuration, JWT security, and RAG knowledge documents
│   ├── schemas/              # Pydantic models & validation schemas
│   ├── services/
│   │   ├── agents/           # 5 Core analysis & assistant agents
│   │   ├── agent_orchestrator.py
│   │   ├── code_validator.py
│   │   ├── mongodb_storage_service.py
│   │   ├── pdf_report_service.py
│   │   ├── rag_service.py
│   │   └── storage_service.py
│   └── main.py               # FastAPI application entrypoint
├── data/                     # Local SQLite fallback database (analyses.db)
├── test_milestone2.py        # OWASP static vulnerability test suite
├── test_milestone3.py        # Multi-agent orchestrator test suite
├── test_milestone4.py        # PDF generation & E2E inspection test suite
├── test_auth_admin.py        # JWT auth & Admin SOC test suite
├── test_mongodb.py           # MongoDB Atlas integration test suite
├── Dockerfile                # Production container specification
├── requirements.txt          # Python dependencies
└── README.md
```

---

## ⚡ Quick Start

### 1. Installation
```bash
cd infy/BackEnd
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a `.env` file in `infy/BackEnd/`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=Smartcodeinspection
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:80,http://127.0.0.1:5173,http://localhost:3000,*
```

### 3. Run Development Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

* Swagger Interactive UI: `http://localhost:8000/docs`
* ReDoc UI: `http://localhost:8000/redoc`

---

## 📡 REST API Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/code/submit` | Submit code snippet for static & security analysis | Optional |
| `POST` | `/api/code/upload` | Upload source code file (`.py`, `.java`, `.js`, etc.) | Optional |
| `GET` | `/api/analysis` | List historical code analyses | Optional |
| `GET` | `/api/analysis/{id}` | Get detailed inspection findings by ID | Optional |
| `DELETE` | `/api/analysis/{id}` | Delete analysis record | Optional |
| `POST` | `/api/remediation/{id}` | Generate/retrieve AI refactored code fixes | Optional |
| `GET` | `/api/summary/{id}` | Get Pull Request review summary & Health Score | Optional |
| `POST` | `/api/assistant/chat` | RAG-grounded conversational Q&A assistant | Optional |
| `GET` | `/api/report/pdf/{id}` | Download binary PDF compliance inspection report | Optional |
| `POST` | `/api/report/pdf/generate` | Generate PDF report from arbitrary JSON payload | Optional |
| `POST` | `/api/auth/signup` | Register developer account | Public |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT bearer token | Public |
| `GET` | `/api/auth/me` | Validate session token & get active user profile | Bearer JWT |
| `GET` | `/api/admin/users` | List all users and account statuses | Admin JWT |
| `POST` | `/api/admin/users/{id}/status` | Toggle user active/blocked status | Admin JWT |
| `GET` | `/api/admin/stats` | Platform-wide security analytics & audit logs | Admin JWT |

---

## 🧪 Automated Testing

Execute the test suites directly from `infy/BackEnd`:

```bash
# Test OWASP vulnerability detection
python test_milestone2.py

# Test Multi-Agent Orchestrator & RAG Assistant
python test_milestone3.py

# Test PDF Generation & End-to-End Analysis
python test_milestone4.py

# Test Authentication & Admin SOC
python test_auth_admin.py

# Test MongoDB Atlas Cloud Connection
python test_mongodb.py
```

---

## 🐳 Docker Deployment

```bash
docker build -t smart-code-backend .
docker run -p 8000:8000 --env-file .env smart-code-backend
```
