import { useState } from "react";

import {
  AlertTriangle,
  CheckCircle2,
  CircleAlert,
  Hash,
  Languages,
  Lightbulb,
  ShieldAlert,
  ShieldCheck,
  Code2,
} from "lucide-react";

export default function ResultCard({ result, error }) {
  const [activeFilter, setActiveFilter] = useState("all");

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-400/20 bg-rose-400/5 p-5">
        <div className="flex items-start gap-3">
          <CircleAlert
            className="mt-0.5 shrink-0 text-rose-400"
            size={20}
          />

          <div>
            <h3 className="font-semibold text-rose-100">
              Submission failed
            </h3>

            <p className="mt-1 text-sm text-rose-200/70">
              {error}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const analysisId =
    result.analysis_id ||
    result.analysisId ||
    result.id ||
    "—";

  const language = result.language || "—";

  const isSyntaxValid =
    result.syntax_valid ??
    result.syntaxValid ??
    true;

  const status =
    result.status ||
    (isSyntaxValid ? "completed" : "failed");

  const message =
    result.message ||
    (isSyntaxValid
      ? "Code analyzed successfully."
      : "Syntax errors found.");

  const errors = result.errors || [];
  const findings = result.findings || [];

  // --------------------------------------------------
  // Severity counts
  // --------------------------------------------------

  const highCount = findings.filter(
    (item) =>
      String(item.severity).toLowerCase() === "high"
  ).length;

  const mediumCount = findings.filter(
    (item) =>
      String(item.severity).toLowerCase() === "medium"
  ).length;

  const lowCount = findings.filter(
    (item) =>
      String(item.severity).toLowerCase() === "low"
  ).length;

  // --------------------------------------------------
  // Finding classification
  // --------------------------------------------------

  const getFindingCategory = (item) => {
    const type = String(item.type || "").toLowerCase();
    const title = String(item.title || "").toLowerCase();

    const securityKeywords = [
      "security",
      "vulnerability",
      "injection",
      "xss",
      "csrf",
      "secret",
      "hash",
      "command",
      "authentication",
      "authorization",
    ];

    const isSecurity = securityKeywords.some(
      (keyword) =>
        type.includes(keyword) ||
        title.includes(keyword)
    );

    return isSecurity ? "security" : "quality";
  };

  // --------------------------------------------------
  // Apply active filter
  // --------------------------------------------------

  const filteredFindings = findings.filter((item) => {
    if (activeFilter === "all") {
      return true;
    }

    return (
      getFindingCategory(item) === activeFilter
    );
  });

  return (
    <div className="space-y-6">

      {/* ==============================================
          OVERVIEW CARD
      =============================================== */}

      <div
        className={`rounded-2xl border p-5 shadow-glow transition ${
          isSyntaxValid
            ? "border-emerald-400/20 bg-gradient-to-br from-emerald-950/30 to-slate-900/60"
            : "border-rose-400/20 bg-gradient-to-br from-rose-950/30 to-slate-900/60"
        }`}
      >
        <div className="mb-4 flex items-start gap-3">

          <div
            className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl ${
              isSyntaxValid
                ? "bg-emerald-400/15 text-emerald-300"
                : "bg-rose-400/15 text-rose-300"
            }`}
          >
            {isSyntaxValid ? (
              <CheckCircle2 size={20} />
            ) : (
              <CircleAlert size={20} />
            )}
          </div>

          <div className="min-w-0 flex-1">

            <h3
              className={`font-bold ${
                isSyntaxValid
                  ? "text-emerald-100"
                  : "text-rose-100"
              }`}
            >
              {message}
            </h3>

            <p className="mt-0.5 text-xs text-slate-400">
              Backend validation report
            </p>

          </div>
        </div>


        {/* ==========================================
            FINDINGS SUMMARY
        =========================================== */}

        <div className="grid gap-3 sm:grid-cols-4">

          <SummaryCard
            label="Total Findings"
            value={findings.length}
            icon={ShieldAlert}
          />

          <SummaryCard
            label="High"
            value={highCount}
            tone="rose"
          />

          <SummaryCard
            label="Medium"
            value={mediumCount}
            tone="amber"
          />

          <SummaryCard
            label="Low"
            value={lowCount}
            tone="cyan"
          />

        </div>


        {/* ==========================================
            ANALYSIS INFORMATION
        =========================================== */}

        <div className="mt-3 grid gap-2.5 sm:grid-cols-4">

          <Info
            icon={Hash}
            label="Analysis ID"
            value={analysisId}
            mono
          />

          <Info
            icon={Languages}
            label="Language"
            value={String(language).replace(
              /^./,
              (c) => c.toUpperCase()
            )}
          />

          <Info
            icon={
              isSyntaxValid
                ? ShieldCheck
                : ShieldAlert
            }
            label="Syntax State"
            value={
              isSyntaxValid
                ? "Valid"
                : "Syntax Error"
            }
            highlight={
              isSyntaxValid
                ? "emerald"
                : "rose"
            }
          />

          <Info
            icon={CheckCircle2}
            label="Status"
            value={String(status).toUpperCase()}
            highlight={
              status === "completed"
                ? "cyan"
                : "amber"
            }
          />

        </div>

      </div>


      {/* ==============================================
          SYNTAX ERRORS
      =============================================== */}

      {errors.length > 0 && (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-5">

          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-rose-300">

            <AlertTriangle size={18} />

            <span>
              Syntax Errors ({errors.length})
            </span>

          </div>


          <div className="space-y-2">

            {errors.map((err, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-rose-500/20 bg-slate-950/60 p-3 text-xs"
              >

                <div className="mb-1 flex items-center gap-2 font-mono font-bold text-rose-400">

                  <span>
                    Line {err.line ?? "—"}
                  </span>

                </div>

                <p className="text-slate-300">
                  {err.message}
                </p>

              </div>
            ))}

          </div>

        </div>
      )}


      {/* ==============================================
          UNIFIED FINDINGS
      =============================================== */}

      {findings.length > 0 && (
        <div className="rounded-2xl border border-slate-700/80 bg-slate-900/50 p-5">

          {/* Header */}

          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">

            <div className="flex items-center gap-2 text-sm font-bold text-cyan-300">

              <ShieldAlert size={18} />

              <span>
                Unified Analysis Findings
              </span>

            </div>

            <span className="font-mono text-xs text-slate-500">
              {filteredFindings.length} shown
            </span>

          </div>


          {/* ==========================================
              FILTER BUTTONS
          =========================================== */}

          <div className="mb-5 flex flex-wrap gap-2">

            {/* ALL */}

            <FilterButton
              active={activeFilter === "all"}
              onClick={() => setActiveFilter("all")}
            >
              All
              <span className="ml-1.5 opacity-60">
                {findings.length}
              </span>
            </FilterButton>


            {/* CODE QUALITY */}

            <FilterButton
              active={activeFilter === "quality"}
              onClick={() =>
                setActiveFilter("quality")
              }
            >
              <Code2 size={14} />
              Code Quality
              <span className="ml-1 opacity-60">
                {
                  findings.filter(
                    (item) =>
                      getFindingCategory(item) ===
                      "quality"
                  ).length
                }
              </span>
            </FilterButton>


            {/* SECURITY */}

            <FilterButton
              active={activeFilter === "security"}
              onClick={() =>
                setActiveFilter("security")
              }
            >
              <ShieldAlert size={14} />
              Security
              <span className="ml-1 opacity-60">
                {
                  findings.filter(
                    (item) =>
                      getFindingCategory(item) ===
                      "security"
                  ).length
                }
              </span>
            </FilterButton>

          </div>


          {/* ==========================================
              FILTERED FINDINGS
          =========================================== */}

          {filteredFindings.length > 0 ? (

            <div className="space-y-4">

              {filteredFindings.map((item, idx) => {

                const sev = (
                  item.severity || "low"
                ).toLowerCase();

                const category =
                  getFindingCategory(item);

                const sevBadge =
                  sev === "high"
                    ? "border-rose-400/30 bg-rose-400/10 text-rose-300"
                    : sev === "medium"
                    ? "border-amber-400/30 bg-amber-400/10 text-amber-300"
                    : "border-cyan-400/30 bg-cyan-400/10 text-cyan-300";


                return (
                  <div
                    key={idx}
                    className="rounded-xl border border-slate-700/70 bg-slate-950/60 p-4 transition hover:border-slate-600"
                  >

                    {/* Finding Header */}

                    <div className="mb-2 flex flex-wrap items-center justify-between gap-2">

                      <div className="flex flex-wrap items-center gap-2">

                        {/* Severity */}

                        <span
                          className={`rounded-md border px-2 py-0.5 text-[11px] font-bold uppercase ${sevBadge}`}
                        >
                          {item.severity || "low"}
                        </span>


                        {/* Category */}

                        <span className="flex items-center gap-1 text-xs font-mono uppercase tracking-wider text-slate-400">

                          {category === "security" ? (
                            <ShieldAlert
                              size={12}
                              className="text-rose-400"
                            />
                          ) : (
                            <Code2
                              size={12}
                              className="text-cyan-400"
                            />
                          )}

                          {category === "security"
                            ? "Security"
                            : "Code Quality"}

                        </span>


                        {/* Finding Type */}

                        <span className="text-xs font-mono uppercase tracking-wider text-slate-500">
                          {item.type
                            ?.replace(/_/g, " ") ||
                            "Issue"}
                        </span>

                      </div>


                      {/* Line */}

                      {item.line && (
                        <span className="rounded bg-slate-800/80 px-2 py-0.5 font-mono text-xs text-slate-400">
                          Line {item.line}
                        </span>
                      )}

                    </div>


                    {/* Title */}

                    <h4 className="mb-1 text-sm font-bold text-slate-100">
                      {item.title || "Untitled Finding"}
                    </h4>


                    {/* Description */}

                    <p className="mb-3 text-xs leading-relaxed text-slate-300">
                      {item.description}
                    </p>


                    {/* Code Snippet */}

                    {item.code_snippet && (
                      <div className="mb-3 overflow-x-auto rounded-lg border border-slate-800 bg-[#050b14] p-2.5 font-mono text-xs text-slate-300">
                        <code>
                          {item.code_snippet}
                        </code>
                      </div>
                    )}


                    {/* Recommendation */}

                    {item.recommendation && (
                      <div className="rounded-lg border border-indigo-500/20 bg-indigo-500/5 p-3">

                        <div className="mb-1 flex items-center gap-1.5 text-xs font-bold text-indigo-300">

                          <Lightbulb
                            size={14}
                            className="text-indigo-400"
                          />

                          <span>
                            RAG Recommendation
                          </span>

                        </div>

                        <p className="text-xs leading-relaxed text-indigo-200/90">
                          {item.recommendation}
                        </p>

                      </div>
                    )}

                  </div>
                );
              })}

            </div>

          ) : (

            /* Empty filter state */

            <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-6 text-center">

              <div className="mx-auto mb-2 grid h-9 w-9 place-items-center rounded-lg bg-slate-800/60">

                {activeFilter === "security" ? (
                  <ShieldAlert
                    size={17}
                    className="text-slate-500"
                  />
                ) : (
                  <Code2
                    size={17}
                    className="text-slate-500"
                  />
                )}

              </div>

              <p className="text-sm font-semibold text-slate-300">
                No{" "}
                {activeFilter === "security"
                  ? "security"
                  : "code quality"}{" "}
                findings detected.
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Try selecting another filter.
              </p>

            </div>

          )}

        </div>
      )}


      {/* ==============================================
          NO FINDINGS
      =============================================== */}

      {isSyntaxValid &&
        findings.length === 0 && (
          <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-center">

            <p className="text-xs font-semibold text-emerald-300">
              ✓ No security vulnerabilities or severe
              code smells detected in this snippet.
            </p>

          </div>
        )}

    </div>
  );
}


/* ====================================================
   INFO COMPONENT
==================================================== */

function Info({
  icon: Icon,
  label,
  value,
  mono,
  highlight,
}) {
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

        <Icon size={12} />

        {label}

      </div>

      <p
        className={`mt-0.5 text-xs font-bold ${textColor} ${
          mono ? "font-mono" : ""
        }`}
      >
        {value}
      </p>

    </div>
  );
}


/* ====================================================
   SUMMARY CARD
==================================================== */

function SummaryCard({
  label,
  value,
  icon: Icon,
  tone = "slate",
}) {
  const styles = {
    slate: {
      border: "border-slate-700/60",
      bg: "bg-slate-950/45",
      text: "text-slate-200",
    },

    rose: {
      border: "border-rose-400/20",
      bg: "bg-rose-400/5",
      text: "text-rose-300",
    },

    amber: {
      border: "border-amber-400/20",
      bg: "bg-amber-400/5",
      text: "text-amber-300",
    },

    cyan: {
      border: "border-cyan-400/20",
      bg: "bg-cyan-400/5",
      text: "text-cyan-300",
    },
  };

  const style = styles[tone];

  return (
    <div
      className={`rounded-xl border ${style.border} ${style.bg} p-4`}
    >

      <div className="flex items-center justify-between">

        <span className="text-[10px] uppercase tracking-wider text-slate-500">
          {label}
        </span>

        {Icon && (
          <Icon
            size={15}
            className={style.text}
          />
        )}

      </div>

      <p
        className={`mt-2 text-2xl font-bold ${style.text}`}
      >
        {value}
      </p>

    </div>
  );
}


/* ====================================================
   FILTER BUTTON
==================================================== */

function FilterButton({
  active,
  onClick,
  children,
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center rounded-lg border px-3 py-2 text-xs font-semibold transition ${
        active
          ? "border-cyan-400/30 bg-cyan-400/10 text-cyan-200"
          : "border-slate-700/70 bg-slate-950/40 text-slate-400 hover:border-slate-600 hover:text-slate-200"
      }`}
    >
      {children}
    </button>
  );
}