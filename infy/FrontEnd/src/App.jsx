import { useState } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import CodeReview from "./pages/CodeReview";

function HistoryPlaceholder({ onNavigate }) {
  return (
    <main className="min-h-[calc(100vh-72px)] grid-bg px-5 py-12 lg:px-8">
      <div className="mx-auto max-w-3xl glass rounded-3xl p-8 text-center sm:p-12">
        <div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-cyan-400/10 text-cyan-300">03</div>
        <h1 className="mt-5 text-2xl font-extrabold text-white">Analysis History</h1>
        <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-400">
          The history page will be connected to persisted analysis records after the Milestone 2 backend is ready.
        </p>
        <button
          type="button"
          onClick={() => onNavigate("analyze")}
          className="mt-6 rounded-xl bg-gradient-to-r from-cyan-300 to-blue-500 px-5 py-3 text-sm font-bold text-slate-950"
        >
          Start an Analysis
        </button>
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
