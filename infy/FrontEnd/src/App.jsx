import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import CodeReview from "./pages/CodeReview";
import { deleteAnalysis, getAnalysisHistory } from "./services/api";

function HistoryPlaceholder({ onNavigate }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState("");

  useEffect(() => {
    let active = true;

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
  }, []);

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
        <h1 className="mt-5 text-2xl font-extrabold text-white">Analysis History</h1>
        <p className="mt-2 text-sm text-slate-400">Saved analyses from the backend database.</p>

        {loading && <div className="mt-6 glass rounded-2xl p-6 text-sm text-slate-400">Loading history...</div>}
        {error && <div className="mt-6 rounded-2xl border border-rose-400/20 bg-rose-400/5 p-5 text-sm text-rose-200">{error}</div>}
        {!loading && !error && history.length === 0 && (
          <div className="mt-6 glass rounded-2xl p-8 text-center">
            <p className="text-sm text-slate-400">No analyses have been saved yet.</p>
            <button type="button" onClick={() => onNavigate("analyze")} className="mt-5 rounded-xl bg-gradient-to-r from-cyan-300 to-blue-500 px-5 py-3 text-sm font-bold text-slate-950">
              Start an Analysis
            </button>
          </div>
        )}
        {history.length > 0 && (
          <div className="mt-6 space-y-3">
            {history.map((analysis) => (
              <div key={analysis.analysis_id} className="glass flex flex-col gap-3 rounded-2xl p-5 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-mono text-sm text-cyan-300">{analysis.analysis_id}</p>
                  <p className="mt-1 text-sm text-slate-200">{analysis.language} source analysis</p>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-400">
                  <span className={analysis.syntax_valid ? "text-emerald-300" : "text-rose-300"}>{analysis.syntax_valid ? "Valid syntax" : "Syntax errors"}</span>
                  <span className="uppercase">{analysis.status}</span>
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
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const navigate = (page) => setActivePage(page);

  return (
    <div className="min-h-screen bg-[#050b14] text-slate-100">
      <Navbar activePage={activePage} onNavigate={navigate} />
      {activePage === "dashboard" && <Dashboard onNavigate={navigate} />}
      {activePage === "analyze" && <CodeReview onNavigate={navigate} />}
      {activePage === "history" && <HistoryPlaceholder onNavigate={navigate} />}
    </div>
  );
}
