import {
  AlertTriangle,
  CheckCircle2,
  CircleAlert,
  Hash,
  HelpCircle,
  Languages,
  Lightbulb,
  ShieldAlert,
  ShieldCheck
} from "lucide-react";

export default function ResultCard({ result, error }) {
  if (error) {
    return (
      <div className="rounded-2xl border border-rose-400/20 bg-rose-400/5 p-5">
        <div className="flex items-start gap-3">
          <CircleAlert className="mt-0.5 text-rose-400 shrink-0" size={20} />
          <div>
            <h3 className="font-semibold text-rose-100">Submission failed</h3>
            <p className="mt-1 text-sm text-rose-200/70">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const analysisId = result.analysis_id || result.analysisId || result.id || "—";
  const language = result.language || "—";
  const isSyntaxValid = result.syntax_valid ?? result.syntaxValid ?? true;
  const status = result.status || (isSyntaxValid ? "completed" : "failed");
  const message = result.message || (isSyntaxValid ? "Code analyzed successfully." : "Syntax errors found.");
  const errors = result.errors || [];
  const findings = result.findings || [];

  return (
    <div className="space-y-6">
      {/* Overview Card */}
      <div className={`rounded-2xl border p-5 shadow-glow transition ${
        isSyntaxValid
          ? "border-emerald-400/20 bg-gradient-to-br from-emerald-950/30 to-slate-900/60"
          : "border-rose-400/20 bg-gradient-to-br from-rose-950/30 to-slate-900/60"
      }`}>
        <div className="mb-4 flex items-start gap-3">
          <div className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl ${
            isSyntaxValid ? "bg-emerald-400/15 text-emerald-300" : "bg-rose-400/15 text-rose-300"
          }`}>
            {isSyntaxValid ? <CheckCircle2 size={20} /> : <CircleAlert size={20} />}
          </div>
          <div className="min-w-0 flex-1">
            <h3 className={`font-bold ${isSyntaxValid ? "text-emerald-100" : "text-rose-100"}`}>
              {message}
            </h3>
            <p className="mt-0.5 text-xs text-slate-400">Backend validation report</p>
          </div>
        </div>

        <div className="grid gap-2.5 sm:grid-cols-4">
          <Info icon={Hash} label="Analysis ID" value={analysisId} mono />
          <Info icon={Languages} label="Language" value={String(language).replace(/^./, (c) => c.toUpperCase())} />
          <Info
            icon={isSyntaxValid ? ShieldCheck : ShieldAlert}
            label="Syntax State"
            value={isSyntaxValid ? "Valid" : "Syntax Error"}
            highlight={isSyntaxValid ? "emerald" : "rose"}
          />
          <Info
            icon={CheckCircle2}
            label="Status"
            value={String(status).toUpperCase()}
            highlight={status === "completed" ? "cyan" : "amber"}
          />
        </div>
      </div>

      {/* Syntax Errors Section */}
      {errors.length > 0 && (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-5">
          <div className="mb-3 flex items-center gap-2 text-rose-300 font-semibold text-sm">
            <AlertTriangle size={18} />
            <span>Syntax Errors ({errors.length})</span>
          </div>
          <div className="space-y-2">
            {errors.map((err, idx) => (
              <div key={idx} className="rounded-xl border border-rose-500/20 bg-slate-950/60 p-3 text-xs">
                <div className="flex items-center gap-2 font-mono text-rose-400 font-bold mb-1">
                  <span>Line {err.line ?? "—"}</span>
                </div>
                <p className="text-slate-300">{err.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Security & Vulnerability Analysis Findings Section */}
      {findings.length > 0 && (
        <div className="rounded-2xl border border-slate-700/80 bg-slate-900/50 p-5">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2 text-cyan-300 font-bold text-sm">
              <ShieldAlert size={18} />
              <span>Security & Vulnerability Analysis ({findings.length})</span>
            </div>
            <span className="text-xs text-slate-500 font-mono">AI RAG Recommendations Active</span>
          </div>

          <div className="space-y-4">
            {findings.map((item, idx) => {
              const sev = (item.severity || "low").toLowerCase();
              const sevBadge =
                sev === "high"
                  ? "border-rose-400/30 bg-rose-400/10 text-rose-300"
                  : sev === "medium"
                  ? "border-amber-400/30 bg-amber-400/10 text-amber-300"
                  : "border-cyan-400/30 bg-cyan-400/10 text-cyan-300";

              return (
                <div key={idx} className="rounded-xl border border-slate-700/70 bg-slate-950/60 p-4 transition hover:border-slate-600">
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`rounded-md border px-2 py-0.5 text-[11px] font-bold uppercase ${sevBadge}`}>
                        {item.severity}
                      </span>
                      <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                        {item.type?.replace("_", " ") || "Issue"}
                      </span>
                    </div>
                    {item.line && (
                      <span className="font-mono text-xs text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded">
                        Line {item.line}
                      </span>
                    )}
                  </div>

                  <h4 className="font-bold text-slate-100 text-sm mb-1">{item.title}</h4>
                  <p className="text-xs leading-relaxed text-slate-300 mb-3">{item.description}</p>

                  {item.code_snippet && (
                    <div className="mb-3 rounded-lg border border-slate-800 bg-[#050b14] p-2.5 font-mono text-xs text-slate-300 overflow-x-auto">
                      <code>{item.code_snippet}</code>
                    </div>
                  )}

                  {item.recommendation && (
                    <div className="rounded-lg border border-indigo-500/20 bg-indigo-500/5 p-3">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-300 mb-1">
                        <Lightbulb size={14} className="text-indigo-400" />
                        <span>RAG Recommendation</span>
                      </div>
                      <p className="text-xs leading-relaxed text-indigo-200/90">{item.recommendation}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {isSyntaxValid && findings.length === 0 && (
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-center">
          <p className="text-xs text-emerald-300 font-semibold">
            ✓ No security vulnerabilities or severe code smells detected in this snippet.
          </p>
        </div>
      )}
    </div>
  );
}

function Info({ icon: Icon, label, value, mono, highlight }) {
  const textColor =
    highlight === "emerald"
      ? "text-emerald-300"
      : highlight === "rose"
      ? "text-rose-300"
      : highlight === "cyan"
      ? "text-cyan-300"
      : highlight === "amber"
      ? "text-amber-300"
      : "text-slate-200";

  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-950/45 px-3 py-2.5">
      <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-slate-400">
        <Icon size={12} /> {label}
      </div>
      <p className={`mt-0.5 text-xs font-bold ${textColor} ${mono ? "font-mono" : ""}`}>{value}</p>
    </div>
  );
}