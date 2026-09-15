# Project Guide: Smart Code Inspection Platform with Vulnerability Detection System

This document provides a comprehensive developer guide covering system architecture, directory structure, multi-agent pipeline components, MongoDB Atlas cloud storage, JWT authentication, native PDF report generation, and Docker container orchestration.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Client[React Frontend - Port 5173 / 80] -->|API Request| Backend[FastAPI Backend - Port 8000]
    Backend -->|Auth & JWT| AuthRouter[Auth Router /api/auth]
    Backend -->|Admin SOC| AdminRouter[Admin Router /api/admin]
    Backend -->|1. Submit / Upload| API[FastAPI Router /api/code]
    API -->|2. Orchestrate| Orchestrator[Agent Orchestrator (asyncio.gather)]
    Orchestrator -->|Parallel Quality Scan| CodeAnalysis[1. Code Analysis Agent]
    Orchestrator -->|Parallel Security Scan| SecurityAnalysis[2. Security Vulnerability Agent]
    CodeAnalysis & SecurityAnalysis -->|3. Query Guidelines| RAGService[RAG Service (TF-IDF + Cosine)]
    RAGService -->|Lookup Rules| RAGKB[RAG Knowledge Base]
    Backend -->|4. Remediation Request| RemediationAgent[3. Remediation Agent (Gemini 2.5 Flash)]
    Backend -->|5. PR Summary Request| PRSummaryAgent[4. PR Summary Agent]
    Backend -->|6. Chat Query| AssistantAgent[5. Conversational Assistant Agent]
    AssistantAgent -->|Retrieve Citations| RAGService
    Backend -->|7. PDF Export| PDFService[PDF Report Service ReportLab]
    Backend -->|8. Cloud Storage| MongoDB[(MongoDB Atlas Cloud Cluster)]
    MongoDB -->|Fallback| SQLite[(SQLite Local DB analyses.db)]
```

---

## 🧩 Architectural Modules Breakdown

### 1. Code Submission & Developer Portal Module
* **Frontend Components**:
  * `LandingPage.jsx`: High-converting landing page with Hero section, live code comparison card, 5-agent breakdown, and 3-step workflow.
  * `Dashboard.jsx`: Live dynamic analytics overview calculating metrics directly from MongoDB Atlas (Total Analyses, Security Risks, Code Smells, Average Score).
  * `AdminDashboard.jsx`: Security Operations Center (SOC) dashboard for user management (block/activate developers), vulnerability distribution charts, and global inspection audit logs.
  * `Navbar.jsx`: Sticky header providing seamless navigation, active user status, and Sign In / Sign Out controls.
  * `AuthModal.jsx`: Segmented modal for Sign In and Sign Up with eye password toggle, developer role enforcement, and demo quick-fill shortcuts.
  * `CodeReview.jsx` & `CodeEditor.jsx`: Code editor supporting copy-pasting, custom theme styling, syntax coloring, and live line numbering.
  * `AnalysisProgress.jsx`: Multi-stage active loading visualizer reporting current agent execution state.
  * `ResultCard.jsx`: In-place tab switcher (*Findings & Issues*, *PR Review Summary*, *AI Remediation Roadmap*), zero-scrolling UX, **Download PDF Report** button, and 1-click Copy GitHub PR comment.
  * `ConversationalAssistant.jsx`: Interactive slide-out chat drawer providing developer Q&A grounded in the RAG Secure Coding knowledge base with citation document previews.

---

### 2. Multi-Agent Analysis & Remediation Pipeline (5 Core Agents)
1. **Code Analysis Agent** (`code_analysis_agent.py`): Evaluates structural metrics (parameters count, function length, docstring coverage) and cognitive code complexity using AST analysis.
2. **Security Vulnerability Agent** (`security_vulnerability_agent.py`): Scans AST syntax trees for OWASP Top 10 vulnerabilities (SQLi, Command Injection, XSS, insecure deserialization, hardcoded secrets, weak hashing).
3. **Remediation Agent** (`remediation_agent.py`): Generates finding-specific security and code quality fixes with side-by-side corrected code snippets, explanations, and refactoring tips (`gemini-2.5-flash` with deterministic offline engine fallback).
4. **PR Summary Agent** (`pr_summary_agent.py`): Compiles all agent findings into a structured, PR-style review summary with executive overview, severity breakdown, Code Health Score (0-100), prioritized fix roadmap, and GitHub-ready markdown.
5. **Conversational Code Assistant Agent** (`assistant_agent.py`): RAG-powered Q&A grounded in secure coding knowledge base for follow-up queries, vulnerability explanations, and deeper guidance.

---

### 3. Native PDF Engine, Cloud Storage & Auth Services
* **Native PDF Engine** (`pdf_report_service.py` & `app/api/report.py`): Programmatic PDF generation engine built using ReportLab. Streams multi-page PDF inspection reports with branding, Health Score gauge, verdict, severity table, fix roadmap, and refactored code.
* **MongoDB Atlas Cloud Database** (`mongodb_storage_service.py`): Primary cloud database integration connecting to MongoDB Atlas cluster (`smartcodeinspection`) with multi-collection document storage (`users`, `analyses`, `remediations`) and SQLite local fallback (`storage_service.py`).
* **JWT Security & Auth** (`security.py`, `auth.py`, `admin.py`): HMAC-SHA256 JWT token generation, SHA-256 password hashing, user registration, and Admin role-based access control (RBAC).

---

## 📁 Repository Directory Structure

```text
├── infy/
│   ├── BackEnd/
│   │   ├── app/
│   │   │   ├── api/          # Routers (/code, /analysis, /remediation, /summary, /assistant, /report, /auth, /admin)
│   │   │   ├── core/         # Settings, config, JWT security, and RAG knowledge documents
│   │   │   ├── schemas/      # Pydantic schemas (code, analysis, remediation, summary, assistant, auth)
│   │   │   ├── services/     # Core services and multi-agent pipeline
│   │   │   │   ├── agents/   # CodeAnalysis, Security, Remediation, PRSummary, Assistant
│   │   │   │   ├── agent_orchestrator.py
│   │   │   │   ├── code_validator.py
│   │   │   │   ├── mongodb_storage_service.py
│   │   │   │   ├── pdf_report_service.py
│   │   │   │   ├── rag_service.py
│   │   │   │   └── storage_service.py
│   │   │   └── main.py       # FastAPI application entrypoint
│   │   ├── data/             # Local SQLite database (analyses.db)
│   │   ├── test_milestone2.py # Automated detection validation suite
│   │   ├── test_milestone3.py # Multi-agent suite validation
│   │   ├── test_milestone4.py # PDF export & 3-sample E2E validation suite
│   │   ├── test_auth_admin.py # Auth & Admin SOC test suite
│   │   ├── test_mongodb.py   # MongoDB Atlas connection test suite
│   │   ├── Dockerfile        # Container build definition for backend
│   │   ├── requirements.txt  # Python package requirements
│   │   └── README.md         # Backend technical documentation
│   └── FrontEnd/
│       ├── src/
│       │   ├── components/   # UI (Editor, Upload, ResultCard, Navbar, AuthModal, Progress, ConversationalAssistant)
│       │   ├── pages/        # Page views (LandingPage, CodeReview, Dashboard, AdminDashboard)
│       │   ├── services/     # API request handlers (api.js)
│       │   └── index.css     # Design tokens and styles
│       ├── Dockerfile        # Container build definition for frontend
│       ├── nginx.conf        # Production Nginx reverse proxy configuration
│       ├── package.json
│       ├── vite.config.js
│       └── README.md         # Frontend technical documentation
├── ARCHITECTURE_SPECIFICATION.md # Complete code-accurate architecture specifications
├── docker-compose.yml        # Multi-container orchestration definition
├── LICENSE                   # Open-source LICENSE
├── README.md                 # Main user instructions
└── projectguide.md           # This developer guide
```

---

## 🔍 Complete API Endpoints Reference

### Code Inspection & PDF Report Endpoints
* **`POST /api/code/submit`**: Submit code snippet as a JSON request body.
* **`POST /api/code/upload`**: Upload code file as form-data (`.py`, `.java`, `.js`, etc.).
* **`GET /api/analysis`**: List historical code analysis records.
* **`GET /api/analysis/{analysis_id}`**: Fetch detailed code analysis report by ID.
* **`DELETE /api/analysis/{analysis_id}`**: Delete an analysis record.
* **`POST /api/remediation/{analysis_id}`**: Generate or retrieve AI-powered remediations with corrected code.
* **`GET /api/summary/{analysis_id}`**: Generate structured Pull Request review summary with Health Score.
* **`POST /api/assistant/chat`**: Conversational Code Assistant Q&A grounded in RAG knowledge base.
* **`GET /api/report/pdf/{analysis_id}`**: Stream binary PDF inspection report file (`application/pdf`).
* **`POST /api/report/pdf/generate`**: Stream binary PDF report from JSON payload.

### Authentication & Admin Endpoints
* **`POST /api/auth/signup`**: Register a developer user account.
* **`POST /api/auth/login`**: Authenticate email/password and receive JWT session token.
* **`GET /api/auth/me`**: Validate active JWT session token.
* **`GET /api/admin/users`**: List all registered user accounts (Admin only).
* **`POST /api/admin/users/{user_id}/status`**: Toggle user active/blocked status (Admin only).
* **`GET /api/admin/stats`**: Retrieve platform-wide security analytics & audit logs (Admin only).

---

## 🐳 Docker Deployment Guide

### Single-Command Start
```bash
docker-compose up --build
```

### Stop Services
```bash
docker-compose down
```
