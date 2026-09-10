# Smart Code Inspection Platform with Vulnerability Detection System

An AI-powered multi-agent platform for automated code review, security vulnerability scanning (OWASP Top 10), and RAG-driven remediation guidance.

---

## 🚀 Project Status: Milestone 3 Completed

### Features Delivered across Milestones 1, 2 & 3:
* **Code Submission Module**: Direct code paste and file upload for Python and Java with syntax validation.
* **Code Analysis Agent**: Reviews code structure, identifying code smells, design anti-patterns, function complexity, and docstring coverage.
* **Security Vulnerability Agent**: Scans for OWASP Top 10 vulnerabilities (SQL Injection, Command Injection, XSS, insecure deserialization, hardcoded secrets, weak hashing).
* **Multi-Agent Orchestrator**: Concurrently executes analysis and security agents using `asyncio.gather` and merges results into a unified prioritized findings list.
* **Remediation Agent**: Generates finding-specific security and code quality remediations, providing before/after corrected code snippets, explanations, and refactoring suggestions. Powered by Gemini LLM with instant deterministic RAG fallbacks.
* **PR Summary Agent**: Compiles all agent findings into a structured, PR-style review summary with executive overview, severity breakdown, Code Health Score (0-100), prioritized fix roadmap, and 1-click GitHub markdown export.
* **Conversational Code Assistant**: Interactive RAG-grounded Q&A interface for follow-up queries, vulnerability explanations, and secure coding guidance with cited source documents.
* **Findings Display & Dashboard**: Modern portal featuring severity scoring, categorization filters (Quality vs. Security), progress animations, and historical inspection tracking.
* **Persistent SQLite Storage**: Local database storing full analysis results, findings history, and generated remediation records with full CRUD lifecycle.
* **RAG Secure Coding Knowledge Base**: In-memory retrieval engine grounding recommendations in OWASP guidelines using TF-IDF and Cosine Similarity vector indexing.

---

## 🛠️ Tech Stack
* **Frontend**: React (Vite), Tailwind CSS, Lucide React (Icons), PrismJS, React Simple Code Editor
* **Backend**: FastAPI (Python), Uvicorn (ASGI Web Server), Scikit-Learn (TF-IDF Vectorization), SQLite, Google GenAI SDK, Numpy

---

## 💻 Installation & Setup Guide

### Prerequisites
* **Node.js**: v18.0.0 or higher
* **Python**: v3.9 or higher

---

### Step 1: Set Up Backend

1. Navigate to the backend directory:
   ```bash
   cd infy/BackEnd
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install fastapi uvicorn pydantic scikit-learn numpy javalang google-genai python-dotenv
   ```

4. Run the backend server:
   ```bash
   python -m uvicorn app.main:app --port 8000
   ```
   *The backend documentation will be accessible at: `http://localhost:8000/docs`*

---

### Step 2: Set Up Frontend

1. Navigate to the frontend directory:
   ```bash
   cd infy/FrontEnd
   ```

2. Create a `.env` file in the root of the `FrontEnd` directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. Install frontend dependencies:
   ```bash
   npm install
   ```

4. Run the frontend development server:
   ```bash
   npm run dev
   ```
   *The developer portal will be accessible at: `http://localhost:5173/`*