import { ArrowRight, CheckCircle2, Code2, FileCode2, ShieldAlert, Sparkles, TrendingUp } from "lucide-react";

const recentAnalyses = [
  { file: "login.py", language: "Python", issues: 6, score: 72, status: "Needs attention", time: "Today" },
  { file: "Main.java", language: "Java", issues: 3, score: 84, status: "Good", time: "Yesterday" },
  { file: "app.py", language: "Python", issues: 0, score: 96, status: "Excellent", time: "Aug 14" }
];

const stats = [
  { label: "Total analyses", value: "-", hint: "+6 this week", icon: Code2 },
  { label: "Security findings", value: "-", hint: "3 high severity", icon: ShieldAlert },
  { label: "Code smells", value: "-", hint: "Across 18 files", icon: FileCode2 },
  { label: "Average score", value: "-", hint: "+8% improvement", icon: TrendingUp }
];

export default function Dashboard({ onNavigate }) {
  return (
    <div className="min-h-[calc(100vh-72px)] grid-bg">
      <main className="mx-auto max-w-7xl px-5 py-8 lg:px-8 lg:py-10">
        <section className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-400/[0.08] via-slate-950/60 to-indigo-500/[0.08] p-6 shadow-2xl sm:p-8">
          <div className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-32 right-1/3 h-72 w-72 rounded-full bg-indigo-500/10 blur-3xl" />

          <div className="relative max-w-3xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/15 bg-cyan-400/5 px-3 py-1.5 text-xs font-medium text-cyan-200">
              <Sparkles size={14} />
              Milestone 2 • Multi-Agent Code Intelligence
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Make every line of code safer.
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
              Analyze code quality and OWASP security risks with dedicated agents, then review everything in one unified report.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                onClick={() => onNavigate("analyze")}
                className="group flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-300 to-blue-500 px-5 py-3 text-sm font-bold text-slate-950 shadow-glow transition hover:-translate-y-0.5"
              >
                <Code2 size={17} />
                Start New Analysis
                <ArrowRight size={16} className="transition group-hover:translate-x-0.5" />
              </button>
              <button
                type="button"
                onClick={() => onNavigate("history")}
                className="rounded-xl border border-slate-700 bg-slate-950/50 px-5 py-3 text-sm font-semibold text-slate-300 transition hover:border-slate-600 hover:text-white"
              >
                View Analysis History
              </button>
            </div>
          </div>
        </section>

        <section className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map(({ label, value, hint, icon: Icon }) => (
            <div key={label} className="glass rounded-2xl p-5 transition hover:-translate-y-0.5 hover:border-slate-700/80">
              <div className="flex items-center justify-between">
                <div className="grid h-9 w-9 place-items-center rounded-xl bg-slate-800/80 text-cyan-300">
                  <Icon size={17} />
                </div>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-600">Live</span>
              </div>
              <p className="mt-5 text-2xl font-extrabold tracking-tight text-white">{value}</p>
              <p className="mt-1 text-xs font-medium text-slate-300">{label}</p>
              <p className="mt-2 text-[11px] text-slate-500">{hint}</p>
            </div>
          ))}
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div className="glass overflow-hidden rounded-2xl">
            <div className="flex items-center justify-between border-b border-slate-800/80 px-5 py-4">
              <div>
                <h2 className="text-sm font-bold text-white">Recent analyses</h2>
                <p className="mt-1 text-xs text-slate-500">Your latest code inspection activity</p>
              </div>
              <button type="button" onClick={() => onNavigate("history")} className="text-xs font-semibold text-cyan-300 hover:text-cyan-200">
                View all
              </button>
            </div>

            <div className="divide-y divide-slate-800/70">
              {recentAnalyses.map((item) => (
                <div key={item.file} className="flex flex-col gap-4 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-slate-800/80 text-cyan-300">
                      <FileCode2 size={17} />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-slate-200">{item.file}</p>
                      <p className="mt-1 text-xs text-slate-500">{item.language} • {item.time}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-5 sm:justify-end">
                    <div>
                      <p className="text-xs font-semibold text-slate-300">{item.issues} issues</p>
                      <p className="mt-1 text-[11px] text-slate-500">{item.status}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-extrabold text-white">{item.score}</p>
                      <p className="text-[10px] uppercase tracking-wider text-slate-600">score</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="glass rounded-2xl p-5">
            <div className="flex items-center gap-3">
              <div className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-400/10 text-emerald-300">
                <CheckCircle2 size={18} />
              </div>
              <div>
                <h2 className="text-sm font-bold text-white">Analysis pipeline</h2>
                <p className="mt-1 text-xs text-slate-500">Milestone 2 architecture</p>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              {["Syntax validation", "Code Analysis Agent", "Security Vulnerability Agent", "Parallel orchestration", "Unified findings"] .map((step, index) => (
                <div key={step} className="flex items-center gap-3 rounded-xl border border-slate-800/80 bg-slate-950/30 px-3 py-2.5">
                  <span className="grid h-6 w-6 place-items-center rounded-full bg-emerald-400/10 text-[10px] font-bold text-emerald-300">{index + 1}</span>
                  <span className="text-xs font-medium text-slate-300">{step}</span>
                  <CheckCircle2 className="ml-auto text-emerald-400/70" size={14} />
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
