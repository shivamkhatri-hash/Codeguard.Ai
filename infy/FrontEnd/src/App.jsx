import { useEffect, useState } from "react";
import { Trash2, FileCode2, ExternalLink, ShieldCheck, AlertTriangle, ArrowRight } from "lucide-react";
import Navbar from "./components/Navbar";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import CodeReview from "./pages/CodeReview";
import { deleteAnalysis, getAnalysisHistory } from "./services/api";

function calculateHealthScore(findings) {
  if (!findings || findings.length === 0) return 100;
  let score = 100;
  for (const f of findings) {
    if (f.title === "Software Architecture Metrics") continue;
    const sev = (f.severity || "").toLowerCase();
    if (sev === "high") score -= 15;
    else if (sev === "medium") score -= 8;
    else if (sev === "low") score -= 3;
  }
  return Math.max(0, Math.min(100, score));
}

function formatDate(dateStr) {
  if (!dateStr) return "Just now";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch {
    return dateStr;
  }
}

function HistoryView({ onNavigate, onSelectAnalysis, authUser, onOpenAuth }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(!!authUser);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState("");

  useEffect(() => {
    if (!authUser) {
      setHistory([]);
      setLoading(false);
      return;
    }

    let active = true;
    setLoading(true);
    getAnalysisHistory()
      .then((data) => {
        if (active) setHistory(Array.isArray(data) ? data : []);
      })
      .catch((requestError) => {
        if (active) setError(requestError.message || "Could not load analysis history.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [authUser]);

  const handleDelete = async (analysisId) => {
    if (!window.confirm(`Delete analysis ${analysisId}?`)) return;

    setDeletingId(analysisId);
    setError("");
    try {
      await deleteAnalysis(analysisId);
      setHistory((items) => items.filter((item) => item.analysis_id !== analysisId));
    } catch (requestError) {
      setError(requestError.message || "Could not delete this analysis.");
    } finally {
      setDeletingId("");
    }
  };

  return (
    <main className="min-h-[calc(100vh-72px)] grid-bg px-5 py-12 lg:px-8">
      <div className="mx-auto max-w-5xl">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-extrabold text-white">Analysis History</h1>
            <p className="mt-1 text-sm text-slate-400">All saved code inspection reports from the local database.</p>
          </div>
          <button
            type="button"
            onClick={() => onNavigate("analyze")}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-300 to-blue-500 px-4 py-2.5 text-xs font-bold text-slate-950 shadow-glow"
          >
            <span>Start New Analysis</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {loading && <div className="mt-6 glass rounded-2xl p-6 text-sm text-slate-400">Loading history...</div>}
        {error && <div className="mt-6 rounded-2xl border border-rose-400/20 bg-rose-400/5 p-5 text-sm text-rose-200">{error}</div>}
        {!loading && !error && history.length === 0 && (
          <div className="mt-6 glass rounded-2xl p-8 text-center max-w-xl mx-auto">
            <p className="text-sm text-slate-300">
              {authUser
                ? "No analyses have been saved yet."
                : "You are currently exploring in Guest mode. Sign in to save, sync, and track your code inspection history across sessions."}
            </p>
            <div className="mt-6 flex items-center justify-center gap-3">
              {!authUser && onOpenAuth && (
                <button
                  type="button"
                  onClick={onOpenAuth}
                  className="rounded-xl bg-gradient-to-r from-cyan-300 to-blue-500 px-5 py-3 text-sm font-bold text-slate-950 shadow-glow hover:brightness-110 transition"
                >
                  Sign In / Sign Up
                </button>
              )}
              <button
                type="button"
                onClick={() => onNavigate("analyze")}
                className="rounded-xl border border-slate-700 bg-slate-900/60 px-5 py-3 text-sm font-semibold text-slate-300 hover:text-white transition"
              >
                Start an Analysis
              </button>
            </div>
          </div>
        )}
        {history.length > 0 && (
          <div className="mt-6 space-y-3">
            {history.map((analysis) => {
              const findings = analysis.findings || [];
              const issuesCount = findings.filter((f) => f.title !== "Software Architecture Metrics").length;
              const score = calculateHealthScore(findings);
              const displayFileName = analysis.filename || (analysis.language === "python" ? "script.py" : "Main.java");

              return (
                <div key={analysis.analysis_id} className="glass flex flex-col gap-4 rounded-2xl p-5 sm:flex-row sm:items-center sm:justify-between transition hover:border-slate-700/80">
                  <div className="flex min-w-0 items-center gap-3.5">
                    <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-slate-800/80 text-cyan-300">
                      <FileCode2 size={20} />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="truncate text-base font-bold text-white">{displayFileName}</p>
                        <span className="font-mono text-[11px] text-cyan-400/80 bg-cyan-400/10 px-2 py-0.5 rounded-md">{analysis.analysis_id}</span>
                      </div>
                      <p className="mt-1 text-xs text-slate-400 uppercase font-mono tracking-wider">
                        {analysis.language} • <span className="text-slate-400 normal-case">{formatDate(analysis.created_at)}</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-xs sm:justify-end">
                    <div className="text-right">
                      <p className="text-xs font-semibold text-slate-300">{issuesCount} issues</p>
                      <p className={`text-[11px] font-bold ${score >= 80 ? "text-emerald-400" : score >= 60 ? "text-amber-400" : "text-rose-400"}`}>
                        {score}/100 score
                      </p>
                    </div>

                    <span className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold ${analysis.syntax_valid ? "bg-emerald-500/10 text-emerald-300" : "bg-rose-500/10 text-rose-300"}`}>
                      {analysis.syntax_valid ? "Valid Syntax" : "Syntax Error"}
                    </span>

                    {onSelectAnalysis && (
                      <button
                        type="button"
                        onClick={() => onSelectAnalysis(analysis)}
                        className="flex items-center gap-1.5 rounded-xl border border-cyan-400/30 bg-cyan-400/10 px-3 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-400/20 transition"
                      >
                        <span>Open & Review</span>
                        <ExternalLink size={13} />
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={() => handleDelete(analysis.analysis_id)}
                      disabled={deletingId === analysis.analysis_id}
                      className="rounded-lg border border-rose-400/20 p-2 text-rose-300 transition hover:bg-rose-400/10 disabled:cursor-not-allowed disabled:opacity-50"
                      title="Delete analysis"
                      aria-label={`Delete analysis ${analysis.analysis_id}`}
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}

import AdminDashboard from "./pages/AdminDashboard";
import AuthModal from "./components/AuthModal";
import { getAuthUser, clearAuth } from "./services/api";

export default function App() {
  const [activePage, setActivePage] = useState("landing");
  const [activeAnalysis, setActiveAnalysis] = useState(null);
  const [authUser, setAuthUser] = useState(() => getAuthUser());
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  const navigate = (page) => {
    setActiveAnalysis(null);
    setActivePage(page);
  };

  const handleSelectAnalysis = (analysis) => {
    setActiveAnalysis(analysis);
    setActivePage("analyze");
  };

  const handleAuthSuccess = (userData) => {
    setAuthUser(userData);
    if (userData.role === "admin") {
      setActivePage("admin");
    }
  };

  const handleLogout = () => {
    clearAuth();
    setAuthUser(null);
    if (activePage === "admin") {
      setActivePage("landing");
    }
  };

  return (
    <div className="min-h-screen bg-[#050b14] text-slate-100">
      <Navbar
        activePage={activePage}
        onNavigate={navigate}
        authUser={authUser}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
      />
      {activePage === "landing" && <LandingPage onNavigate={navigate} />}
      {activePage === "dashboard" && (
        <Dashboard
          onNavigate={navigate}
          onSelectAnalysis={handleSelectAnalysis}
          authUser={authUser}
          onOpenAuth={() => setIsAuthOpen(true)}
        />
      )}
      {activePage === "analyze" && (
        <CodeReview
          key={activeAnalysis ? (activeAnalysis.analysis_id || activeAnalysis.id || "existing") : "new-inspection"}
          onNavigate={navigate}
          initialAnalysis={activeAnalysis}
          authUser={authUser}
          onOpenAuth={() => setIsAuthOpen(true)}
        />
      )}
      {activePage === "history" && (
        <HistoryView
          onNavigate={navigate}
          onSelectAnalysis={handleSelectAnalysis}
          authUser={authUser}
          onOpenAuth={() => setIsAuthOpen(true)}
        />
      )}
      {activePage === "admin" && <AdminDashboard />}

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />
    </div>
  );
}
