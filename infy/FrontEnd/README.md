# Smart Code Inspection Platform — Frontend Client

Modern, responsive single-page web application built with **React 18**, **Vite 6**, and **Tailwind CSS** for automated multi-agent code inspection, vulnerability visualization, AI remediation, and report generation.

---

## 🌟 Key Features

* 🚀 **Interactive Code Review Workspace** (`CodeReview.jsx`): Multi-language syntax editor supporting Python, Java, JavaScript, TypeScript, C++, Go, and HTML with file upload / drag-and-drop.
* 🎯 **In-Place Segmented Results Hub** (`ResultCard.jsx`): Zero-scrolling UX switching across:
  * **Findings & Issues**: Severity-badged vulnerability list with OWASP classification and AST code references.
  * **PR Review Summary**: Executive verdict, Code Health Score (0-100), and 1-click Copy GitHub PR Markdown.
  * **AI Remediation Roadmap**: Side-by-side original vs. secure refactored code diffs and guidance.
* 📄 **1-Click PDF Report Export**: Programmatically downloads branded, multi-page security compliance PDF reports.
* 🤖 **RAG Conversational Assistant** (`ConversationalAssistant.jsx`): Floating slide-out chat drawer providing context-aware explanations and OWASP guideline citations.
* 📊 **Developer Dashboard** (`Dashboard.jsx`): Real-time metrics overview (Total Analyses, Security Risks, Code Smells, Average Score) with quick navigation to historical reviews.
* 🛡️ **Admin SOC Panel** (`AdminDashboard.jsx`): Role-based Security Operations Center for user account management (block/activate) and threat breakdown distribution charts.
* 🔒 **JWT Authentication Modal** (`AuthModal.jsx`): Quick sign-in and developer registration with seeded quick-fill credentials.

---

## 🛠️ Tech Stack

* **Core Framework**: React 18
* **Build Tool**: Vite 6
* **Styling**: Tailwind CSS 3 (custom glassmorphism dark theme)
* **Code Editor**: React Simple Code Editor & PrismJS syntax highlighter
* **Icons**: Lucide React
* **Deployment**: Nginx Alpine Docker container

---

## 📁 Directory Structure

```text
FrontEnd/
├── src/
│   ├── components/
│   │   ├── AnalysisProgress.jsx        # Multi-agent analysis progress visualizer
│   │   ├── AuthModal.jsx               # Segmented Sign In & Sign Up modal
│   │   ├── CodeEditor.jsx              # Code editor with syntax styling
│   │   ├── ConversationalAssistant.jsx # Slide-out RAG AI chat assistant
│   │   ├── ErrorBoundary.jsx           # React error boundary wrapper
│   │   ├── FileUpload.jsx              # File drag-and-drop handler
│   │   ├── LanguageSelector.jsx        # Multi-language selector dropdown
│   │   ├── Navbar.jsx                  # Navigation header with user session
│   │   └── ResultCard.jsx              # Tabbed findings, PR summary & AI diffs
│   ├── pages/
│   │   ├── AdminDashboard.jsx          # Admin SOC security & user management
│   │   ├── CodeReview.jsx              # Main code submission & review view
│   │   ├── Dashboard.jsx               # Developer analytics & inspection history
│   │   └── LandingPage.jsx             # High-converting product showcase
│   ├── services/
│   │   └── api.js                      # REST API client & JWT token manager
│   ├── App.jsx                         # Main app routing & state container
│   ├── index.css                       # Tailwind directives & design system tokens
│   └── main.jsx                        # React root entry point
├── Dockerfile                          # Multi-stage Vite build + Nginx static serve
├── nginx.conf                          # Production Nginx SPA & reverse proxy config
├── package.json
├── tailwind.config.js
├── vite.config.js
└── README.md
```

---

## ⚡ Quick Start

### 1. Installation
```bash
cd infy/FrontEnd
npm install
```

### 2. Configure Environment (`.env`)
Create `.env` or `.env.local` in `infy/FrontEnd/`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Run Development Server
```bash
npm run dev
```

* Frontend application accessible at: `http://localhost:5173/` (or `http://localhost:5174/`)

### 4. Production Build
```bash
npm run build
npm run preview
```

---

## 🐳 Docker Deployment

Build and run using the optimized multi-stage Nginx container:

```bash
docker build -t smart-code-frontend .
docker run -p 80:80 smart-code-frontend
```
