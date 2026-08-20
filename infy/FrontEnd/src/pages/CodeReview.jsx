import { useState } from "react";
import { Check, CircleAlert, FileCode2, RotateCcw, Send, ShieldCheck, Sparkles } from "lucide-react";
import CodeEditor from "../components/CodeEditor";
import FileUpload from "../components/FileUpload";
import LanguageSelector from "../components/LanguageSelector";
import AnalysisProgress from "../components/AnalysisProgress";
import ResultCard from "../components/ResultCard";
import { DEFAULT_CODE } from "../types/analysis";
import { submitCode } from "../services/api";


export default function CodeReview({ onNavigate }) {
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


      <main className="mx-auto max-w-7xl px-5 py-8 lg:px-8 lg:py-10">
        <section className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-indigo-400/15 bg-indigo-400/5 px-3 py-1.5 text-xs font-medium text-indigo-200">
              <Sparkles size={14} />
             AI-Powered Code Quality & Security Analysis
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Review your code before it reaches production.
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
              Analyze your source code for quality issues and OWASP security vulnerabilities. CodeGuard runs specialized agents in parallel and combines their findings into one unified report.
            </p>
          </div>
          <div className="hidden shrink-0 items-center gap-2 rounded-xl border border-emerald-400/15 bg-emerald-400/5 px-3 py-2 text-xs text-emerald-200 lg:flex">
            <ShieldCheck size={15} />
            AI Analysis Pipeline Ready
          </div>
        </section>

        <div className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
          <aside className="glass h-fit rounded-2xl p-5">
            <div className="mb-5 flex items-center gap-2">
              <div className="grid h-8 w-8 place-items-center rounded-lg bg-cyan-400/10">
                <FileCode2 size={16} className="text-cyan-300" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-white">Analysis configuration</h2>
                <p className="text-xs text-slate-500">Choose language and source</p>
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
                <span>{error || "Ready to analyze your source code."}</span>
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
                    Analyzing...
                  </>
                ) : (
                  <>
                    Analyze Code <Send size={16} className="transition group-hover:translate-x-0.5" />
                  </>
                )}
              </button>
            </div>

            <div className="mt-6">
  {loading && (
    <AnalysisProgress language={language} />
  )}

  {!loading && (
    <ResultCard
      result={result}
      error={
        result
          ? ""
          : error && loading === false && code.trim() && language
            ? error
            : ""
      }
    />
  )}
</div>

            {!result && !error && (
              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                {[
                 ["01", "Select language", "Choose a language"],
                  ["02", "Add source", "Paste or upload"],
                 ["03", "Analyze", "Run quality + security agents"]
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

        <footer className="mt-10 flex flex-col gap-2 border-t border-slate-800/70 pt-5 text-xs text-slate-600 sm:flex-row sm:items-center sm:justify-between">
          <span>Milestone 2 workspace • Code quality + security analysis</span>
          <button type="button" onClick={() => onNavigate("dashboard")} className="text-slate-500 transition hover:text-cyan-300">
            Back to dashboard
          </button>
        </footer>
      </main>
    </div>
  );
}