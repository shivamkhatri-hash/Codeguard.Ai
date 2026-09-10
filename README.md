# Smart Code Inspection Platform with Vulnerability Detection System

An enterprise-grade, AI-powered multi-agent platform for automated code review, OWASP Top 10 security vulnerability detection, RAG-driven remediation guidance, and native PDF compliance report generation.

---

## 🚀 Project Status: Milestone 4 (Week 7-8) 100% Completed

### 🌟 All Core Capabilities & Deliverables Across Milestones 1, 2, 3 & 4:

* 📄 **Native PDF Report Export Engine**: Programmatic multi-page PDF inspection report service (`pdf_report_service.py` & `GET /api/report/pdf/{id}`) generating exportable PDF reports complete with health score gauges, executive verdicts, severity breakdown tables, prioritized fix roadmaps, and AI-refactored secure code diffs.
* 🍃 **MongoDB Atlas Cloud Database**: Primary cloud database integration (`smartcodeinspection` cluster) with multi-collection document storage (`users`, `analyses`, `remediations`) and resilient SQLite local fallback.
* 🔒 **JWT Authentication & User Roles**: Developer & Admin JWT authentication (`security.py`, `auth.py`) with enforced Developer public sign-up and secure password hashing.
* 🛡️ **Admin Security Operations Center (SOC) Dashboard**: `AdminDashboard.jsx` providing user management (block/activate user accounts), platform-wide vulnerability threat breakdown charts, average health score benchmarks, and global inspection audit logs.
* 🏠 **High-Converting Landing Page**: Modern hero section (`LandingPage.jsx`), live vulnerability vs refactored code showcase, 5-agent architecture breakdown, and 3-step workflow.
* 🎯 **In-Place Zero-Scroll UX**: Segmented tab view switcher (`ResultCard.jsx`) allowing seamless navigation between *Findings & Issues*, *PR Review Summary*, and *AI Remediation Roadmap* without page scrolling.
* 🤖 **5-Agent Parallel Engine**: Concurrently executes Code Analysis Agent, Security Vulnerability Agent (OWASP Top 10), AI Remediation Agent, PR Summary Agent, and RAG Conversational Code Assistant using `asyncio.gather`.
* 📚 **RAG Secure Coding Knowledge Base**: In-memory and vector search retrieval engine (`rag_service.py`) grounding recommendations in OWASP guidelines using TF-IDF and Cosine Similarity.
* 📊 **Live Interactive Dashboard**: `Dashboard.jsx` computing real-time aggregate metrics directly from the cloud database with 1-click **Open & Review**.
* 🧪 **Comprehensive Test Suites**: `test_milestone2.py`, `test_milestone3.py`, `test_milestone4.py`, `test_auth_admin.py`, and `test_mongodb.py` achieving 100% test pass rates across Python and Java code samples.

---

## 🛠️ Tech Stack

* **Frontend**: React 18 (Vite), Tailwind CSS, Lucide React (Icons), PrismJS, React Simple Code Editor
* **Backend**: FastAPI (Python), Uvicorn (ASGI Web Server), PyMongo (MongoDB Atlas), ReportLab (PDF Engine), Scikit-Learn (TF-IDF Vectorization), SQLite, Google GenAI SDK (`gemini-2.5-flash`)

---

## 💻 Quick Start & Running the Project

### Prerequisites
* **Node.js**: v18.0.0 or higher
* **Python**: v3.9 or higher

---

### Step 1: Run Backend Server

1. Navigate to the backend directory:
   ```bash
   cd infy/BackEnd
   ```

2. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic scikit-learn numpy pymongo reportlab google-genai python-dotenv
   ```

3. Run the backend server:
   ```bash
   python -m uvicorn app.main:app --port 8000 --reload
   ```
   *Interactive API Docs accessible at: `http://localhost:8000/docs`*

---

### Step 2: Run Frontend Application

1. Navigate to the frontend directory:
   ```bash
   cd infy/FrontEnd
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the frontend development server:
   ```bash
   npm run dev
   ```
   *Web application accessible at: `http://localhost:5173/`*

---

## 🧪 Running Automated Test Suites

From `infy/BackEnd`, execute any of the following test suites:

* **Milestone 2 Tests** (OWASP Static Scanning):  
  `python test_milestone2.py`
* **Milestone 3 Tests** (PR Summary, Health Score, RAG Assistant):  
  `python test_milestone3.py`
* **Milestone 4 E2E Tests** (PDF Generation & 3 Python/Java Samples):  
  `python test_milestone4.py`
* **Auth & Admin Tests**:  
  `python test_auth_admin.py`
* **MongoDB Atlas Cloud Tests**:  
  `python test_mongodb.py`

---

## 🔒 Seeded Demo Accounts Out-of-the-Box

* **Admin Account**: Email: `admin@codeguard.ai` | Password: `admin` | Role: `ADMIN`
* **Developer Account**: Email: `sumit@codeguard.ai` | Password: `password123` | Role: `DEVELOPER`