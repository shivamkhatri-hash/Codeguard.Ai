# Smart Code Inspection Platform with Vulnerability Detection System

An enterprise-grade, AI-powered multi-agent platform for automated code review, OWASP Top 10 security vulnerability detection, RAG-driven remediation guidance, and native PDF compliance report generation.

---

## 🌟 Core System Capabilities

* 📄 **Native PDF Compliance Reports**: Programmatic multi-page PDF generation engine (`pdf_report_service.py` & `GET /api/report/pdf/{id}`) rendering health score gauges, executive verdicts, severity tables, prioritized fix roadmaps, and secure code diffs.
* 🤖 **5-Agent Parallel Engine**: Concurrently executes:
  1. **Code Analysis Agent**: AST-based cognitive complexity, parameters, function length, and docstring coverage.
  2. **Security Vulnerability Agent**: Scans for OWASP Top 10 risks (SQLi, Command Injection, XSS, insecure deserialization, hardcoded secrets, weak hashing).
  3. **AI Remediation Agent**: Contextual refactored code snippets with side-by-side diffs powered by Google Gemini 2.5 Flash.
  4. **PR Summary Agent**: Compiles executive PR reviews with Code Health Score (0-100) and 1-click GitHub PR markdown.
  5. **Conversational Assistant Agent**: RAG-grounded interactive Q&A grounded in OWASP knowledge documents.
* 🍃 **Hybrid Storage Layer**: Dual-persistence architecture connecting to **MongoDB Atlas Cloud Database** (`smartcodeinspection` cluster) with an automatic offline **SQLite local database** fallback.
* 🔒 **JWT Authentication & RBAC**: Developer & Admin JWT authentication with password hashing, secure session management, and admin governance.
* 🛡️ **Admin SOC Dashboard**: Security Operations Center (`AdminDashboard.jsx`) providing user management (block/activate developers), vulnerability distribution charts, and global inspection audit logs.
* 🎯 **In-Place Zero-Scroll UX**: Segmented tab switcher (`ResultCard.jsx`) across *Findings & Issues*, *PR Review Summary*, and *AI Remediation Roadmap*.
* 🐳 **Containerized Architecture**: Multi-stage production `Dockerfile`s and `docker-compose.yml` orchestrating FastAPI and Nginx reverse-proxy static frontend.

---

## 🛠️ Tech Stack

* **Frontend**: React 18, Vite 6, Tailwind CSS, Lucide React, PrismJS, React Simple Code Editor
* **Backend**: FastAPI, Uvicorn, PyMongo (MongoDB Atlas), ReportLab (PDF Engine), Scikit-Learn (TF-IDF & Cosine Similarity), SQLite, Google GenAI SDK (`gemini-2.5-flash`)
* **DevOps**: Docker, Docker Compose, Nginx Alpine

---

## 💻 Quick Start & Running the Project

### Prerequisites
* **Node.js**: v18.0.0 or higher
* **Python**: v3.9 or higher
* **Docker & Docker Compose** (optional, for containerized run)

---

### Option A: Running with Docker Compose (Recommended)

Run the entire platform (Frontend + Backend + Nginx + DB layer) with a single command:

```bash
# Start containers
docker-compose up --build

# Run in background (detached)
docker-compose up -d --build

# Stop containers
docker-compose down
```

* **Frontend Web App**: `http://localhost:80` (or `http://localhost:5173`)
* **Backend API Docs**: `http://localhost:8000/docs`

---

### Option B: Running Locally

#### 1. Backend Server Setup
```bash
cd infy/BackEnd

# Install dependencies
pip install -r requirements.txt

# Start backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend API available at `http://localhost:8000` (Docs at `http://localhost:8000/docs`)*

#### 2. Frontend Web App Setup
```bash
cd infy/FrontEnd

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
*Frontend Web App available at `http://localhost:5173/` (or `http://localhost:5174/`)*

---

## 🧪 Running Automated Test Suites

From `infy/BackEnd`, execute any of the following test suites:

```bash
# Milestone 2 Tests (OWASP Static Scanning)
python test_milestone2.py

# Milestone 3 Tests (PR Summary, Health Score, RAG Assistant)
python test_milestone3.py

# Milestone 4 E2E Tests (PDF Generation & Python/Java Samples)
python test_milestone4.py

# Auth & Admin SOC Tests
python test_auth_admin.py

# MongoDB Atlas Cloud Database Tests
python test_mongodb.py
```

---

## 🔑 Seeded Demo Accounts Out-of-the-Box

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@codeguard.ai` | `admin` | User management, threat metrics, platform audit logs |
| **Developer** | `sumit@codeguard.ai` | `password123` | Submit code, view remediations, chat with AI, export PDF |

---

## 📁 Repository Directory Structure

```text
├── infy/
│   ├── BackEnd/
│   │   ├── app/
│   │   │   ├── api/          # Routers (/code, /analysis, /remediation, /summary, /assistant, /report, /auth, /admin)
│   │   │   ├── core/         # Settings, config, JWT security, and RAG knowledge documents
│   │   │   ├── schemas/      # Pydantic validation schemas
│   │   │   ├── services/     # 5 AI agents, RAG, orchestrator, PDF service, storage services
│   │   │   └── main.py       # FastAPI application entrypoint
│   │   ├── data/             # Local SQLite database (analyses.db)
│   │   ├── test_*.py         # Comprehensive automated test suites
│   │   ├── Dockerfile        # Backend container build specification
│   │   ├── requirements.txt  # Python package dependencies
│   │   └── README.md         # Backend guide
│   └── FrontEnd/
│       ├── src/
│       │   ├── components/   # UI components (Editor, Upload, ResultCard, Navbar, Chat, Auth)
│       │   ├── pages/        # Views (LandingPage, CodeReview, Dashboard, AdminDashboard)
│       │   ├── services/     # REST API client & JWT token manager
│       │   └── index.css     # Design system styles & glassmorphism
│       ├── Dockerfile        # Multi-stage Vite + Nginx build specification
│       ├── nginx.conf        # Production Nginx SPA & reverse proxy config
│       ├── package.json
│       └── README.md         # Frontend guide
├── ARCHITECTURE_SPECIFICATION.md # Complete code-accurate system specification
├── docker-compose.yml        # Multi-container orchestration specification
├── projectguide.md           # Comprehensive developer guide & architecture diagrams
└── README.md                 # Project root documentation
```