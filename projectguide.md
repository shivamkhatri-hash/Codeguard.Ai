# Project Guide: Smart Code Inspection Platform with Vulnerability Detection System

This document provides a comprehensive overview of the system architecture, directory structures, functional modules, and installation guidelines for developers working on this project.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Client[React Frontend - Port 5173] -->|API Request| Backend[FastAPI Backend - Port 8000]
    Backend -->|1. Code Submission| CodeValidator[Code Validator Service]
    Backend -->|2. RAG Context| RAGService[RAG Service]
    RAGService -->|Retrieve Guidelines| RAGKB[RAG Knowledge Base]
```

### 1. Code Submission Module
* **Frontend Components**:
  * `CodeEditor.jsx`: Integrated simple code editor supporting raw copy-pasting, custom theme styles, syntax coloring options, and line numbering.
  * `FileUpload.jsx`: Implemented drag-and-drop file selector supporting custom code extensions (`.py`, `.java`, `.js`, `.ts`, `.cpp`, `.go`, `.html`).
  * `LanguageSelector.jsx`: Dropdown control specifying the code context for validation.
* **API Connection**:
  * Calls `POST /api/code/submit` for direct submissions.
  * Calls `POST /api/code/upload` for file uploads.

### 2. Syntax Validation Engine
* Located at `BackEnd/app/services/code_validator.py`.
* **Python**: Parses code to Abstract Syntax Tree (AST) node representations using python standard `ast.parse`.
* **Java**: Utilizes tokenizing and parsing library `javalang`. Features a robust snippet wrapper (`_validate_java_snippet`) allowing developers to test partial blocks or single Java methods without requiring full class structures.
* **Brackets / Quotes Balancer**: Fallback parser validating matched bracket pairs `()`, `[]`, `{}`, and checking for unterminated string literals in dynamically typed languages.

### 3. RAG Knowledge Base & Context Pipeline
* **Knowledge Index**: Contained within `BackEnd/app/core/rag_kb.py`, indexing detailed secure coding practices mapped to OWASP categories (SQLi, Command Injection, XSS, CSRF, Cryptographic Failures, etc.).
* **Search Mechanics**: Configured in `BackEnd/app/services/rag_service.py`. Standardizes text inputs, breaks documents down into paragraph-sized chunks, and uses `scikit-learn`'s `TfidfVectorizer` alongside `cosine_similarity` to retrieve context recommendations.

---

## 📁 Repository Directory Structure

```text
├── infy/
│   ├── BackEnd/
│   │   ├── app/
│   │   │   ├── api/          # API routers (endpoints)
│   │   │   ├── core/         # Settings, config, and RAG knowledge documents
│   │   │   ├── schemas/      # Pydantic data schemas
│   │   │   ├── services/     # Validator, RAG, analysis, and storage services
│   │   │   └── main.py       # FastAPI application entrypoint
│   │   └── README.md
│   └── FrontEnd/
│       ├── src/
│       │   ├── components/   # Shared UI components (Editor, Upload, ResultCard)
│       │   ├── pages/        # Core page views (CodeReview)
│       │   ├── services/     # API request handlers
│       │   └── types/        # Type configurations and defaults
│       ├── package.json
│       ├── vite.config.js
│       └── README.md
├── README.md                 # Main user instructions
└── projectguide.md           # This developer guide
```

---

## 🛠️ Installation & Setup Commands

To set up the platform on your local machine, run the following command sequence:

### 1. Backend Server Setup
```bash
# Navigate to Backend folder
cd infy/BackEnd

# Install required dependencies
pip install fastapi uvicorn pydantic scikit-learn numpy javalang

# Start the server
python -m uvicorn app.main:app --port 8000
```
*API Swagger interactive documentation is available at `http://127.0.0.1:8000/docs`.*

### 2. Frontend Portal Setup
```bash
# Navigate to Frontend folder
cd infy/FrontEnd

# Install package dependencies
npm install

# Start development site
npm run dev
```
*The web interface will be accessible at: `http://localhost:5173/`.*

---

## 🔍 API Endpoints Reference

### Code Validation Endpoints
* **`POST /api/code/submit`**: Submit code snippet as a JSON request body.
* **`POST /api/code/upload`**: Upload code file as form-data.
* **`GET /api/analysis/{analysis_id}`**: Fetch historical code analysis reports by unique ID.
