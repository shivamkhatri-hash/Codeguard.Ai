import {
  ArrowRight,
  ShieldCheck,
  Code2,
  Sparkles,
  Bot,
  FileText,
  Terminal,
  Zap,
  CheckCircle2,
  Lock,
  Cpu,
  BarChart3,
  FileCode2,
  Layers,
  Search,
  BookOpen
} from "lucide-react";

export default function LandingPage({ onNavigate }) {
  return (
    <div className="min-h-screen grid-bg overflow-x-hidden">
      {/* ====================================================
          HERO SECTION
      ==================================================== */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28">
        <div className="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 h-[500px] w-[800px] rounded-full bg-cyan-500/10 blur-[120px]" />
        <div className="pointer-events-none absolute top-1/3 -right-40 h-80 w-80 rounded-full bg-indigo-500/10 blur-[100px]" />

        <div className="mx-auto max-w-7xl px-5 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs font-bold text-cyan-200 shadow-glow">
              <Sparkles size={14} className="text-cyan-300" />
              <span>Next-Gen AI Multi-Agent Platform</span>
            </div>

            <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl leading-[1.15]">
              Make Every Line of Code{" "}
              <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
                Safer & Cleaner.
              </span>
            </h1>

            <p className="mt-6 text-base leading-relaxed text-slate-300 sm:text-lg">
              Automated multi-agent platform for Python & Java codebases. Detect OWASP Top 10 vulnerabilities, review code quality, generate side-by-side AI remediations, and export Pull Request review reports in seconds.
            </p>

            <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <button
                type="button"
                onClick={() => onNavigate("analyze")}
                className="group flex w-full items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-cyan-300 via-blue-400 to-indigo-500 px-6 py-3.5 text-sm font-extrabold text-slate-950 shadow-glow transition hover:-translate-y-0.5 hover:shadow-[0_0_35px_rgba(34,211,238,.35)] sm:w-auto"
              >
                <Code2 size={18} />
                <span>Start Code Inspection</span>
                <ArrowRight size={16} className="transition group-hover:translate-x-1" />
              </button>

              <button
                type="button"
                onClick={() => onNavigate("dashboard")}
                className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-950/60 px-6 py-3.5 text-sm font-semibold text-slate-200 transition hover:border-slate-600 hover:bg-slate-900 sm:w-auto"
              >
                <BarChart3 size={17} className="text-cyan-300" />
                <span>View Live Dashboard</span>
              </button>
            </div>

            {/* Quick Metrics */}
            <div className="mt-12 grid grid-cols-2 gap-4 border-t border-slate-800/80 pt-8 sm:grid-cols-4">
              <div>
                <p className="text-2xl font-black text-white">5 Agents</p>
                <p className="mt-1 text-xs text-slate-400">Parallel AI Pipeline</p>
              </div>
              <div>
                <p className="text-2xl font-black text-cyan-300">OWASP Top 10</p>
                <p className="mt-1 text-xs text-slate-400">Security Rule Coverage</p>
              </div>
              <div>
                <p className="text-2xl font-black text-indigo-300">RAG Grounded</p>
                <p className="mt-1 text-xs text-slate-400">Zero-Hallucination Advice</p>
              </div>
              <div>
                <p className="text-2xl font-black text-emerald-300">PDF & PR</p>
                <p className="mt-1 text-xs text-slate-400">Automated Exports</p>
              </div>
            </div>
          </div>

          {/* Interactive Code Preview Showcase */}
          <div className="mt-14 rounded-2xl border border-cyan-400/20 bg-slate-950/80 p-4 sm:p-6 shadow-2xl backdrop-blur-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-rose-500/80" />
                <span className="h-3 w-3 rounded-full bg-amber-500/80" />
                <span className="h-3 w-3 rounded-full bg-emerald-500/80" />
                <span className="ml-2 font-mono text-xs text-slate-400">login_auth.py — Automated Inspection Showcase</span>
              </div>
              <span className="rounded bg-cyan-400/10 px-2.5 py-1 font-mono text-[11px] font-bold text-cyan-300 border border-cyan-400/20">
                Health Score: 92/100
              </span>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
                    <Lock size={13} /> Flagged Vulnerability
                  </span>
                  <span className="rounded bg-rose-500/20 px-2 py-0.5 text-[10px] font-bold text-rose-300 uppercase">HIGH SEVERITY</span>
                </div>
                <p className="text-xs text-slate-300 mb-2">SQL Injection detected on Line 14: Direct string formatting into database query.</p>
                <pre className="overflow-x-auto rounded bg-slate-950/90 p-3 font-mono text-xs text-rose-200 border border-rose-500/20">
                  <code>{`# ❌ Vulnerable Python Code
query = f"SELECT * FROM users WHERE email='{user_input}'"
cursor.execute(query)`}</code>
                </pre>
              </div>

              <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 size={13} /> AI Remediation Agent Corrected Code
                  </span>
                  <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-300 uppercase">REFACTORED</span>
                </div>
                <p className="text-xs text-slate-300 mb-2">Parameterized binding prevents query manipulation.</p>
                <pre className="overflow-x-auto rounded bg-slate-950/90 p-3 font-mono text-xs text-emerald-200 border border-emerald-500/20">
                  <code>{`# ✅ Secure Parameterized Solution
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (user_input,))`}</code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================
          FEATURE GRID: THE 5 MULTI-AGENT SYSTEM
      ==================================================== */}
      <section className="border-t border-slate-800/80 bg-slate-950/50 py-16 lg:py-24">
        <div className="mx-auto max-w-7xl px-5 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400">Multi-Agent Architecture</h2>
            <h3 className="mt-2 text-3xl font-extrabold text-white sm:text-4xl">
              5 Specialized AI Agents Working in Harmony
            </h3>
            <p className="mt-3 text-sm text-slate-400">
              Our backend orchestrator triggers specialized domain agents concurrently via <code>asyncio.gather</code> to inspect, score, and remediate code in parallel.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Agent 1 */}
            <div className="glass rounded-2xl p-6 transition hover:-translate-y-1 hover:border-cyan-400/30">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-cyan-400/10 text-cyan-300 mb-4">
                <Code2 size={22} />
              </div>
              <h4 className="text-base font-bold text-white">1. Code Analysis Agent</h4>
              <p className="mt-2 text-xs leading-relaxed text-slate-400">
                Evaluates code structure, parameter counts, docstring coverage (PEP 257 / Javadoc), wildcard imports, and cyclomatic complexity.
              </p>
            </div>

            {/* Agent 2 */}
            <div className="glass rounded-2xl p-6 transition hover:-translate-y-1 hover:border-rose-400/30">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-rose-400/10 text-rose-300 mb-4">
                <ShieldCheck size={22} />
              </div>
              <h4 className="text-base font-bold text-white">2. Security Vulnerability Agent</h4>
              <p className="mt-2 text-xs leading-relaxed text-slate-400">
                Scans AST trees for OWASP Top 10 risks: SQL Injection, Command Execution, Hardcoded API Secrets, Weak Hashing (MD5/SHA1), and XSS.
              </p>
            </div>

            {/* Agent 3 */}
            <div className="glass rounded-2xl p-6 transition hover:-translate-y-1 hover:border-emerald-400/30">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-emerald-400/10 text-emerald-300 mb-4">
                <Sparkles size={22} />
              </div>
              <h4 className="text-base font-bold text-white">3. Remediation Agent</h4>
              <p className="mt-2 text-xs leading-relaxed text-slate-400">
                Generates side-by-side corrected secure code refactorings, detailed explanations, and "why it works" security principles.
              </p>
            </div>

            {/* Agent 4 */}
            <div className="glass rounded-2xl p-6 transition hover:-translate-y-1 hover:border-indigo-400/30">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-indigo-400/10 text-indigo-300 mb-4">
                <FileText size={22} />
              </div>
              <h4 className="text-base font-bold text-white">4. PR Summary Agent</h4>
              <p className="mt-2 text-xs leading-relaxed text-slate-400">
                Calculates dynamic Code Health Scores (0-100), compiles executive verdicts, prioritized fix checklists, and GitHub markdown comments.
              </p>
            </div>

            {/* Agent 5 */}
            <div className="glass rounded-2xl p-6 transition hover:-translate-y-1 hover:border-amber-400/30">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-amber-400/10 text-amber-300 mb-4">
                <Bot size={22} />
              </div>
              <h4 className="text-base font-bold text-white">5. Conversational Code Assistant</h4>
              <p className="mt-2 text-xs leading-relaxed text-slate-400">
                Interactive slide-out chat mentor grounded in TF-IDF knowledge base search with expandable OWASP citation document badges.
              </p>
            </div>

            {/* Storage & RAG */}
            <div className="glass rounded-2xl p-6 transition hover:-translate-y-1 hover:border-slate-700">
              <div className="grid h-12 w-12 place-items-center rounded-xl bg-slate-800 text-slate-200 mb-4">
                <Layers size={22} />
              </div>
              <h4 className="text-base font-bold text-white">SQLite Storage & RAG Vector KB</h4>
              <p className="mt-2 text-xs leading-relaxed text-slate-400">
                Stores historical inspection reports locally with full CRUD lifecycle and retrieves OWASP guidelines via Cosine Similarity vector indexing.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================
          HOW IT WORKS (3 SIMPLE STEPS)
      ==================================================== */}
      <section className="py-16 lg:py-24">
        <div className="mx-auto max-w-7xl px-5 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-widest text-cyan-400">Simple Workflow</h2>
            <h3 className="mt-2 text-3xl font-extrabold text-white sm:text-4xl">
              From Raw Code to Production Security in 3 Steps
            </h3>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            <div className="glass rounded-2xl p-6 relative">
              <span className="font-mono text-3xl font-black text-cyan-400/40">01</span>
              <h4 className="mt-3 text-lg font-bold text-white">Paste or Upload Code</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Paste Python or Java code directly into the syntax-highlighted editor, or upload source files (e.g. <code>0209.py</code>).
              </p>
            </div>

            <div className="glass rounded-2xl p-6 relative">
              <span className="font-mono text-3xl font-black text-cyan-400/40">02</span>
              <h4 className="mt-3 text-lg font-bold text-white">Multi-Agent Inspection</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                The orchestrator concurrently runs static AST analyzers and vector similarity matchers against OWASP security rules.
              </p>
            </div>

            <div className="glass rounded-2xl p-6 relative">
              <span className="font-mono text-3xl font-black text-cyan-400/40">03</span>
              <h4 className="mt-3 text-lg font-bold text-white">Review, Fix & Export PDF</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Review in-place tabs for Findings, PR Summaries, AI Code Refactorings, and export a formatted PDF report with 1 click.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================
          CALL TO ACTION FOOTER BANNER
      ==================================================== */}
      <section className="mx-auto max-w-7xl px-5 pb-20 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl border border-cyan-400/20 bg-gradient-to-r from-cyan-950/60 via-slate-950 to-indigo-950/60 p-8 sm:p-12 shadow-2xl text-center">
          <div className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 h-64 w-64 rounded-full bg-cyan-400/20 blur-3xl" />

          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            Ready to secure your codebase?
          </h2>
          <p className="mt-3 max-w-xl mx-auto text-sm text-slate-300">
            Start an instant code analysis now or view your historical database inspections.
          </p>

          <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
            <button
              type="button"
              onClick={() => onNavigate("analyze")}
              className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-300 via-blue-400 to-indigo-500 px-6 py-3.5 text-sm font-extrabold text-slate-950 shadow-glow transition hover:-translate-y-0.5"
            >
              <Code2 size={18} />
              <span>Start Code Inspection</span>
            </button>

            <button
              type="button"
              onClick={() => onNavigate("history")}
              className="flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-950/60 px-6 py-3.5 text-sm font-semibold text-slate-200 transition hover:border-slate-600"
            >
              <FileCode2 size={17} className="text-cyan-300" />
              <span>View Saved History</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
