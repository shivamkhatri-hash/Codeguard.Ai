# Smart Code Inspection Platform with Vulnerability Detection System

An AI-powered multi-agent platform for automated code review, security vulnerability scanning (OWASP Top 10), and RAG-driven remediation guidance.

---

## 🚀 Project Status: Milestone 1 Completed

### Features Delivered in Milestone 1:
* **Code Submission Module**: Support for pasting code snippets directly or uploading source files for both Python and Java.
* **Syntax Validation**: Backend validation checks utilizing Python `ast` parsing and Java `javalang` parsing (supporting full class files and raw method snippets).
* **RAG Secure Coding Knowledge Base**: In-memory retrieval system indexing secure coding standards, OWASP guidelines, and prevention recommendations using TF-IDF and Cosine Similarity vector indexing.

---

## 🛠️ Tech Stack
* **Frontend**: React (Vite), Tailwind CSS, Lucide React (Icons), PrismJS, React Simple Code Editor
* **Backend**: FastAPI (Python), Uvicorn (ASGI Web Server), Scikit-Learn (TF-IDF Vectorization), Numpy

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
   pip install fastapi uvicorn pydantic scikit-learn numpy javalang
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