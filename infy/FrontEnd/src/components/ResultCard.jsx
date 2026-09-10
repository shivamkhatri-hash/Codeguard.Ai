import { useState } from "react";
import { generateRemediation, getPRSummary } from "../services/api";
import ConversationalAssistant from "./ConversationalAssistant";

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
  Sparkles,
  FileText,
  Copy,
  Check,
  Bot,
  Activity,
  ListOrdered,
} from "lucide-react";

export default function ResultCard({ result, error }) {
  const [activeFilter, setActiveFilter] = useState("all");
  const [remediationLoading, setRemediationLoading] = useState(false);
  const [remediationResult, setRemediationResult] = useState(null);
  const [remediationError, setRemediationError] = useState("");

  const [prSummaryLoading, setPrSummaryLoading] = useState(false);
  const [prSummaryResult, setPrSummaryResult] = useState(null);
  const [prSummaryError, setPrSummaryError] = useState("");
  const [prSummaryCopied, setPrSummaryCopied] = useState(false);

  const [isAssistantOpen, setIsAssistantOpen] = useState(false);

  

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

    const handleGenerateRemediation = async () => {
      if (!analysisId || analysisId === "—") {
        setRemediationError("Analysis ID is not available.");
        return;
      }
    
      setRemediationLoading(true);
      setRemediationError("");
    
      try {
        const data = await generateRemediation(analysisId);
        setRemediationResult(data);
      } catch (err) {
        setRemediationError(
          err.message || "Unable to generate remediation."
        );
      } finally {
        setRemediationLoading(false);
      }
    };

    const handleGeneratePRSummary = async () => {
      if (!analysisId || analysisId === "—") {
        setPrSummaryError("Analysis ID is not available.");
        return;
      }

      setPrSummaryLoading(true);
      setPrSummaryError("");

      try {
        const data = await getPRSummary(analysisId);
        setPrSummaryResult(data);
      } catch (err) {
        setPrSummaryError(
          err.message || "Unable to compile PR summary."
        );
      } finally {
        setPrSummaryLoading(false);
      }
    };

    const handleCopyPRMarkdown = () => {
      if (!prSummaryResult?.markdown_pr_comment) return;
      navigator.clipboard.writeText(prSummaryResult.markdown_pr_comment);
      setPrSummaryCopied(true);
      setTimeout(() => setPrSummaryCopied(false), 2500);
    };

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
  // Severity counts & Health Score
  // --------------------------------------------------

  const actionableFindings = findings.filter(
    (item) => item.title !== "Software Architecture Metrics"
  );

  const highCount = actionableFindings.filter(
    (item) =>
      String(item.severity).toLowerCase() === "high"
  ).length;

  const mediumCount = actionableFindings.filter(
    (item) =>
      String(item.severity).toLowerCase() === "medium"
  ).length;

  const lowCount = actionableFindings.filter(
    (item) =>
      String(item.severity).toLowerCase() === "low"
  ).length;

  const healthScore = Math.max(
    0,
    Math.min(
      100,
      100 - highCount * 15 - mediumCount * 8 - lowCount * 3
    )
  );

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
            FINDINGS SUMMARY & HEALTH SCORE
        =========================================== */}

        <div className="grid gap-3 sm:grid-cols-5">

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

          <SummaryCard
            label="Health Score"
            value={`${healthScore}/100`}
            tone={healthScore >= 80 ? "emerald" : healthScore >= 50 ? "amber" : "rose"}
            icon={Activity}
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

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={handleGeneratePRSummary}
                disabled={prSummaryLoading}
                className="inline-flex items-center gap-2 rounded-lg border border-indigo-400/30 bg-indigo-500/10 px-3 py-2 text-xs font-semibold text-indigo-200 transition hover:bg-indigo-500/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <FileText size={14} />
                {prSummaryLoading ? "Compiling PR Summary..." : "Compile PR Summary"}
              </button>

              <button
                type="button"
                onClick={handleGenerateRemediation}
                disabled={remediationLoading}
                className="inline-flex items-center gap-2 rounded-lg border border-cyan-400/30 bg-cyan-400/10 px-3 py-2 text-xs font-semibold text-cyan-200 transition hover:bg-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Sparkles size={14} />
                {remediationLoading ? "Generating Remediation..." : "Generate AI Remediation"}
              </button>

              <button
                type="button"
                onClick={() => setIsAssistantOpen(true)}
                className="inline-flex items-center gap-2 rounded-lg border border-emerald-400/30 bg-emerald-500/10 px-3 py-2 text-xs font-semibold text-emerald-200 transition hover:bg-emerald-500/20"
              >
                <Bot size={14} />
                Ask Code Assistant
              </button>
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
          REMEDIATION RESULTS
      =============================================== */}
            {remediationLoading && (
        <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-5">
          <div className="flex items-center gap-3">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-cyan-300/30 border-t-cyan-300" />

            <div>
              <h3 className="text-sm font-bold text-cyan-200">
                Generating AI Remediation
              </h3>

              <p className="mt-1 text-xs text-slate-400">
                The Remediation Agent is analyzing the findings and generating
                secure fixes.
              </p>
            </div>
          </div>
        </div>
      )}

      {remediationError && !remediationLoading && (
        <div className="rounded-2xl border border-rose-400/20 bg-rose-400/5 p-5">
          <div className="flex items-start gap-3">
            <CircleAlert
              size={18}
              className="mt-0.5 shrink-0 text-rose-300"
            />

            <div>
              <h3 className="text-sm font-bold text-rose-200">
                Remediation Failed
              </h3>

              <p className="mt-1 text-xs leading-relaxed text-rose-200/80">
                {remediationError}
              </p>
            </div>
          </div>
        </div>
      )}

      {remediationResult && !remediationLoading && (
        <div className="rounded-2xl border border-cyan-400/20 bg-slate-900/60 p-5 shadow-glow">

          {/* Remediation Header */}
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-cyan-400/10">
                <Sparkles size={18} className="text-cyan-300" />
              </div>

              <div>
                <h3 className="text-sm font-bold text-cyan-200">
                  AI Remediation Results
                </h3>

                <p className="mt-0.5 text-xs text-slate-500">
                  Secure fixes generated by the Remediation Agent
                </p>
              </div>
            </div>

            <span className="rounded-lg border border-emerald-400/20 bg-emerald-400/5 px-2.5 py-1.5 text-[11px] font-semibold text-emerald-300">
              {remediationResult.remediation_count ?? 0} remediation(s)
            </span>
          </div>

          {/* Remediation Items */}
          <div className="space-y-5">
            {(remediationResult.remediations || []).map(
              (remediation, index) => (
                <div
                  key={index}
                  className="rounded-xl border border-slate-700/70 bg-slate-950/60 p-4"
                >

                  {/* Finding Information */}
                  <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-wider text-cyan-400">
                        Finding {index + 1}
                      </p>

                      <h4 className="mt-1 text-sm font-bold text-slate-100">
                        {remediation.finding_title || "Remediation"}
                      </h4>
                    </div>

                    {remediation.severity && (
                      <span className="rounded-md border border-slate-700 bg-slate-800/70 px-2 py-1 text-[10px] font-bold uppercase text-slate-300">
                        {remediation.severity}
                      </span>
                    )}
                  </div>

                  {/* Recommendation */}
                  {remediation.recommendation && (
                    <div className="mb-4 rounded-lg border border-indigo-500/20 bg-indigo-500/5 p-3">
                      <div className="mb-1 flex items-center gap-1.5 text-xs font-bold text-indigo-300">
                        <Lightbulb size={14} />
                        Recommendation
                      </div>

                      <p className="text-xs leading-relaxed text-indigo-200/90">
                        {remediation.recommendation}
                      </p>
                    </div>
                  )}

                  {/* Original Code */}
                  {remediation.original_code && (
                    <div className="mb-4">
                      <div className="mb-2 flex items-center gap-2">
                        <Code2 size={14} className="text-rose-300" />

                        <span className="text-xs font-bold text-slate-300">
                          Original Code
                        </span>
                      </div>

                      <pre className="overflow-x-auto rounded-lg border border-rose-400/10 bg-[#050b14] p-3 font-mono text-xs leading-relaxed text-slate-300">
                        <code>{remediation.original_code}</code>
                      </pre>
                    </div>
                  )}

                  {/* Corrected Code */}
                  {remediation.corrected_code && (
                    <div className="mb-4">
                      <div className="mb-2 flex items-center gap-2">
                        <CheckCircle2
                          size={14}
                          className="text-emerald-300"
                        />

                        <span className="text-xs font-bold text-emerald-300">
                          Corrected Secure Code
                        </span>
                      </div>

                      <pre className="overflow-x-auto rounded-lg border border-emerald-400/20 bg-[#050b14] p-3 font-mono text-xs leading-relaxed text-slate-300">
                        <code>{remediation.corrected_code}</code>
                      </pre>
                    </div>
                  )}

                  {/* Explanation */}
                  {remediation.explanation && (
                    <div className="mb-4 rounded-lg border border-slate-700/60 bg-slate-900/50 p-3">
                      <p className="mb-1 text-xs font-bold text-slate-200">
                        Explanation
                      </p>

                      <p className="text-xs leading-relaxed text-slate-400">
                        {remediation.explanation}
                      </p>
                    </div>
                  )}

                  {/* Why It Works */}
                  {remediation.why_it_works && (
                    <div className="mb-4 rounded-lg border border-emerald-400/15 bg-emerald-400/5 p-3">
                      <div className="mb-1 flex items-center gap-1.5 text-xs font-bold text-emerald-300">
                        <ShieldCheck size={14} />
                        Why It Works
                      </div>

                      <p className="text-xs leading-relaxed text-emerald-200/80">
                        {remediation.why_it_works}
                      </p>
                    </div>
                  )}

                  {/* Secure Guidance */}
                  {remediation.secure_guidance && (
                    <div className="mb-4 rounded-lg border border-cyan-400/15 bg-cyan-400/5 p-3">
                      <div className="mb-1 flex items-center gap-1.5 text-xs font-bold text-cyan-300">
                        <ShieldCheck size={14} />
                        Secure Coding Guidance
                      </div>

                      <p className="text-xs leading-relaxed text-cyan-200/80">
                        {remediation.secure_guidance}
                      </p>
                    </div>
                  )}

                  {/* Benefits */}
                  {Array.isArray(remediation.benefits) &&
                    remediation.benefits.length > 0 && (
                      <div className="mb-4">
                        <p className="mb-2 text-xs font-bold text-slate-200">
                          Benefits
                        </p>

                        <ul className="space-y-1.5">
                          {remediation.benefits.map((benefit, benefitIndex) => (
                            <li
                              key={benefitIndex}
                              className="flex items-start gap-2 text-xs text-slate-400"
                            >
                              <CheckCircle2
                                size={13}
                                className="mt-0.5 shrink-0 text-emerald-300"
                              />

                              <span>{benefit}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {/* Refactoring Suggestions */}
                  {Array.isArray(remediation.refactoring_suggestions) &&
                    remediation.refactoring_suggestions.length > 0 && (
                      <div>
                        <p className="mb-2 text-xs font-bold text-slate-200">
                          Refactoring Suggestions
                        </p>

                        <ul className="space-y-1.5">
                          {remediation.refactoring_suggestions.map(
                            (suggestion, suggestionIndex) => (
                              <li
                                key={suggestionIndex}
                                className="flex items-start gap-2 text-xs text-slate-400"
                              >
                                <Sparkles
                                  size={13}
                                  className="mt-0.5 shrink-0 text-cyan-300"
                                />

                                <span>{suggestion}</span>
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    )}

                </div>
              )
            )}
          </div>

        </div>
      )}



      {/* ==============================================
          PR REVIEW SUMMARY (AGENT RESULT)
      =============================================== */}
      {prSummaryLoading && (
        <div className="rounded-2xl border border-indigo-400/20 bg-indigo-500/5 p-5">
          <div className="flex items-center gap-3">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-300/30 border-t-indigo-300" />
            <div>
              <h3 className="text-sm font-bold text-indigo-200">
                Compiling PR Review Summary
              </h3>
              <p className="mt-1 text-xs text-slate-400">
                The PR Summary Agent is assembling the executive overview, severity breakdown, and prioritized fix roadmap.
              </p>
            </div>
          </div>
        </div>
      )}

      {prSummaryError && !prSummaryLoading && (
        <div className="rounded-2xl border border-rose-400/20 bg-rose-400/5 p-5">
          <div className="flex items-start gap-3">
            <CircleAlert size={18} className="mt-0.5 shrink-0 text-rose-300" />
            <div>
              <h3 className="text-sm font-bold text-rose-200">PR Summary Failed</h3>
              <p className="mt-1 text-xs text-rose-200/80">{prSummaryError}</p>
            </div>
          </div>
        </div>
      )}

      {prSummaryResult && !prSummaryLoading && (
        <div className="rounded-2xl border border-indigo-400/30 bg-slate-900/80 p-5 shadow-2xl">
          {/* Header */}
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-500/20 border border-indigo-400/30 text-indigo-300">
                <FileText size={20} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold text-indigo-100">PR Review Summary</h3>
                  <span
                    className={`rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase ${
                      prSummaryResult.verdict.includes("Blocked")
                        ? "border-rose-400/30 bg-rose-500/10 text-rose-300"
                        : prSummaryResult.verdict.includes("Needs Attention")
                        ? "border-amber-400/30 bg-amber-500/10 text-amber-300"
                        : "border-emerald-400/30 bg-emerald-500/10 text-emerald-300"
                    }`}
                  >
                    {prSummaryResult.verdict}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Health Score: <strong className="text-indigo-300">{prSummaryResult.health_score}/100</strong>
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={handleCopyPRMarkdown}
              className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-400/40 bg-indigo-500/20 px-3 py-1.5 text-xs font-semibold text-indigo-200 hover:bg-indigo-500/30 transition"
            >
              {prSummaryCopied ? <Check size={14} className="text-emerald-300" /> : <Copy size={14} />}
              {prSummaryCopied ? "Copied Markdown!" : "Copy PR Markdown"}
            </button>
          </div>

          {/* Executive Overview */}
          <div className="mb-4 rounded-xl border border-indigo-500/20 bg-indigo-950/20 p-4">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-indigo-400 mb-1">
              Executive Overview
            </p>
            <p className="text-xs leading-relaxed text-slate-200">
              {prSummaryResult.executive_overview}
            </p>
          </div>

          {/* Prioritized Fix List Table */}
          {prSummaryResult.prioritized_fixes && prSummaryResult.prioritized_fixes.length > 0 && (
            <div>
              <div className="mb-2 flex items-center gap-1.5 text-xs font-bold text-slate-300">
                <ListOrdered size={15} className="text-cyan-400" />
                <span>Prioritized Fix Checklist ({prSummaryResult.prioritized_fixes.length})</span>
              </div>

              <div className="overflow-x-auto rounded-xl border border-slate-800">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-slate-800 bg-slate-950/60 text-[10px] uppercase text-slate-400 font-semibold tracking-wider">
                    <tr>
                      <th className="px-3 py-2">Rank</th>
                      <th className="px-3 py-2">Issue</th>
                      <th className="px-3 py-2">Line</th>
                      <th className="px-3 py-2">Severity</th>
                      <th className="px-3 py-2">Recommended Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                    {prSummaryResult.prioritized_fixes.map((fix) => (
                      <tr key={fix.priority} className="hover:bg-slate-900/50 transition">
                        <td className="px-3 py-2.5 font-mono text-cyan-300">#{fix.priority}</td>
                        <td className="px-3 py-2.5 font-semibold text-slate-200">{fix.title}</td>
                        <td className="px-3 py-2.5 font-mono text-slate-400">L{fix.line}</td>
                        <td className="px-3 py-2.5">
                          <span
                            className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${
                              fix.severity.toLowerCase() === "high"
                                ? "bg-rose-500/20 text-rose-300"
                                : fix.severity.toLowerCase() === "medium"
                                ? "bg-amber-500/20 text-amber-300"
                                : "bg-cyan-500/20 text-cyan-300"
                            }`}
                          >
                            {fix.severity}
                          </span>
                        </td>
                        <td className="px-3 py-2.5 text-slate-300">{fix.action_required}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
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

      {/* ==============================================
          CONVERSATIONAL ASSISTANT DRAWER
      =============================================== */}
      <ConversationalAssistant
        analysisId={analysisId}
        language={language}
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
      />

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

    emerald: {
      border: "border-emerald-400/20",
      bg: "bg-emerald-400/5",
      text: "text-emerald-300",
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