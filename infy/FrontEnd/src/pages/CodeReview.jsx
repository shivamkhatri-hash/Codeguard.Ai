import { useState } from "react";
import { ArrowRight, Check, CircleAlert, FileCode2, RotateCcw, Send, Sparkles, TerminalSquare } from "lucide-react";
import CodeEditor from "../components/CodeEditor";
import FileUpload from "../components/FileUpload";
import LanguageSelector from "../components/LanguageSelector";
import ResultCard from "../components/ResultCard";
import { DEFAULT_CODE } from "../types/analysis";
import { submitCode } from "../services/api";

export default function CodeReview() {
  const [language, setLanguage] = useState("");
  const [code, setCode] = useState("");
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const changeLanguage = (value) => {
    setLanguage(value);
    setError("");
  };

  const clearAll = () => {
    setCode("");
    setLanguage("");
    setFileName("");
    setResult(null);
    setError("");
  };

  const validate = () => {
    if (!language) return "Please select a programming language.";
    if (!code.trim()) return "Code cannot be empty. Paste code or upload a source file.";
    return "";
  };

  const handleSubmit = async () => {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      setResult(null);
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await submitCode({ language, code });
      setResult(data);
    } catch (err) {
      setError(err.message || "Unable to submit code. Please check your backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid-bg">
      <header className="border-b border-slate-800/70 bg-[#050b14]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-cyan-300 to-blue-600 text-slate-950 shadow-glow">
              <TerminalSquare size={21} />
            </div>
            <div>
              <p className="text-sm font-extrabold tracking-tight text-white">CodeGuard AI</p>
              <p className="text-[11px] text-slate-500">Smart Code Inspection & Vulnerability Detection Platform</p>
            </div>
          </div>

          <div className="hidden items-center gap-2 rounded-full border border-cyan-400/15 bg-cyan-400/5 px-3 py-1.5 text-xs text-cyan-200 sm:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Backend Connected (FastAPI)
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-8 lg:px-8 lg:py-10">
        <section className="mb-8 max-w-3xl">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-indigo-400/15 bg-indigo-400/5 px-3 py-1.5 text-xs font-medium text-indigo-200">
            <Sparkles size={14} />
            AI-Powered Code Inspection & Security Vulnerability Scanner
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            Review your code before it reaches production.
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
            Submit Python, Java, JavaScript, TypeScript, C++, Go, or HTML source code by pasting it into the editor or uploading a file.
            The FastAPI backend validates syntax and scans for security vulnerabilities with AI RAG recommendations.
          </p>
        </section>

        <div className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
          <aside className="glass h-fit rounded-2xl p-5">
            <div className="mb-5 flex items-center gap-2">
              <div className="grid h-8 w-8 place-items-center rounded-lg bg-cyan-400/10">
                <FileCode2 size={16} className="text-cyan-300" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-white">Submission setup</h2>
                <p className="text-xs text-slate-500">Choose your source</p>
              </div>
            </div>

            <div className="space-y-5">
              <LanguageSelector language={language} onChange={changeLanguage} />

              <div className="h-px bg-slate-800" />

              <FileUpload
                disabled={loading}
                onCodeLoaded={setCode}
                onFileNameChange={setFileName}
                onLanguageDetected={changeLanguage}
              />

              <div className="rounded-xl border border-slate-800 bg-slate-950/45 p-3">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Input source</p>
                <p className="mt-1 truncate text-sm text-slate-300">
                  {fileName || (code ? "Pasted code" : "No source selected")}
                </p>
              </div>
            </div>
          </aside>

          <section className="min-w-0">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-sm font-bold text-white">Code editor</h2>
                <p className="mt-0.5 text-xs text-slate-500">Paste code directly or load it from a source file.</p>
              </div>
              <button
                type="button"
                onClick={clearAll}
                disabled={loading}
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold text-slate-400 transition hover:bg-slate-800 hover:text-white disabled:opacity-40"
              >
                <RotateCcw size={14} /> Clear
              </button>
            </div>

            <CodeEditor
              code={code}
              language={language || "python"}
              onChange={(value) => {
                setCode(value);
                setResult(null);
                setError("");
              }}
              disabled={loading}
            />

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                {error ? <CircleAlert size={15} className="text-rose-300" /> : <Check size={15} className="text-emerald-300" />}
                <span>{error || "Ready to validate your submission."}</span>
              </div>

              <button
                type="button"
                onClick={handleSubmit}
                disabled={loading}
                className="group flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-300 to-blue-500 px-5 py-3 text-sm font-bold text-slate-950 shadow-glow transition hover:-translate-y-0.5 hover:shadow-[0_0_35px_rgba(34,211,238,.25)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
              >
                {loading ? (
                  <>
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950/30 border-t-slate-950" />
                    Submitting...
                  </>
                ) : (
                  <>
                    Analyze / Submit <Send size={16} className="transition group-hover:translate-x-0.5" />
                  </>
                )}
              </button>
            </div>

            <div className="mt-6">
              <ResultCard result={result} error={result ? "" : error && loading === false && code.trim() && language ? error : ""} />
            </div>

            {!result && !error && (
              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                {[
                  ["01", "Select language", "Python or Java"],
                  ["02", "Add source", "Paste or upload"],
                  ["03", "Submit", "Backend validates"]
                ].map(([number, title, desc]) => (
                  <div key={number} className="rounded-xl border border-slate-800 bg-slate-950/30 p-4">
                    <span className="font-mono text-xs text-cyan-300">{number}</span>
                    <p className="mt-2 text-sm font-semibold text-slate-200">{title}</p>
                    <p className="mt-1 text-xs text-slate-500">{desc}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        <footer className="mt-10 border-t border-slate-800/70 pt-5 text-xs text-slate-600">
          Initial milestone scope: code submission and syntax validation only. AI agents, vulnerability analysis,
          RAG, reports, authentication, GitHub integration and dashboards are intentionally excluded from this phase.
        </footer>
      </main>
    </div>
  );
}