import { useState, useEffect } from "react";
import { generateRemediation, getPRSummary, downloadPDFReportUrl } from "../services/api";
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
  Download,
  FileCode2,
  ArrowRight
} from "lucide-react";

export default function ResultCard({ result, error }) {
  const [activeTab, setActiveTab] = useState("findings"); // 'findings' | 'summary' | 'remediation'
  const [activeFilter, setActiveFilter] = useState("all");

  const [remediationLoading, setRemediationLoading] = useState(false);
  const [remediationResult, setRemediationResult] = useState(null);
  const [remediationError, setRemediationError] = useState("");

  const [prSummaryLoading, setPrSummaryLoading] = useState(false);
  const [prSummaryResult, setPrSummaryResult] = useState(null);
  const [prSummaryError, setPrSummaryError] = useState("");
  const [prSummaryCopied, setPrSummaryCopied] = useState(false);
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);

  // Background pre-fetch PR Summary & AI Remediation as soon as analysis ID is ready
  useEffect(() => {
    // Reset states for new analysis submission
    setRemediationResult(null);
    setRemediationLoading(false);
    setRemediationError("");
    setPrSummaryResult(null);
    setPrSummaryLoading(false);
    setPrSummaryError("");

    const id = result?.analysis_id || result?.analysisId || result?.id;
    if (!id || id === "—") return;

    setPrSummaryLoading(true);
    getPRSummary(id)
      .then((data) => setPrSummaryResult(data))
      .catch((err) => setPrSummaryError(err.message || "Failed to load summary"))
      .finally(() => setPrSummaryLoading(false));

    setRemediationLoading(true);
    generateRemediation(id)
      .then((data) => setRemediationResult(data))
      .catch((err) => setRemediationError(err.message || "Failed to load remediation"))
      .finally(() => setRemediationLoading(false));
  }, [result]);

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-400/20 bg-rose-400/5 p-5">
        <div className="flex items-start gap-3">
          <CircleAlert className="mt-0.5 shrink-0 text-rose-400" size={20} />
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
  const displayFileName = result.filename || (result.language === "java" ? "Main.java" : "main.py");
  const language = result.language || "—";
  const isSyntaxValid = result.syntax_valid ?? result.syntaxValid ?? true;
  const status = result.status || (isSyntaxValid ? "completed" : "failed");
  const message = result.message || (isSyntaxValid ? "Code analyzed successfully." : "Syntax errors found.");
  const errors = result.errors || [];
  const findings = result.findings || [];

  // Calculate Health Score
  const actionableFindings = findings.filter(
    (item) => item.title !== "Software Architecture Metrics"
  );

  const highCount = actionableFindings.filter(
    (item) => String(item.severity).toLowerCase() === "high"
  ).length;

  const mediumCount = actionableFindings.filter(
    (item) => String(item.severity).toLowerCase() === "medium"
  ).length;

  const lowCount = actionableFindings.filter(
    (item) => String(item.severity).toLowerCase() === "low"
  ).length;

  const healthScore = Math.max(
    0,
    Math.min(100, 100 - highCount * 15 - mediumCount * 8 - lowCount * 3)
  );

  const handleGenerateRemediation = async () => {
    setActiveTab("remediation");
    if (remediationResult) return;
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
      setRemediationError(err.message || "Unable to generate remediation.");
    } finally {
      setRemediationLoading(false);
    }
  };

  const handleGeneratePRSummary = async () => {
    setActiveTab("summary");
    if (prSummaryResult) return;
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
      setPrSummaryError(err.message || "Unable to compile PR summary.");
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

  const handleDownloadPDF = () => {
    if (analysisId && analysisId !== "—") {
      window.open(downloadPDFReportUrl(analysisId), "_blank");
      return;
    }
    if (!prSummaryResult) return;
    const printWindow = window.open("", "_blank");
    if (!printWindow) {
      alert("Please allow popups to download or print the PDF report.");
      return;
    }
    const dateStr = new Date().toLocaleString();
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Code Review Report - ${displayFileName}</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #0f172a; margin: 40px; }
          .header { border-bottom: 2px solid #0284c7; padding-bottom: 16px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end; }
          .title { font-size: 24px; font-weight: 800; color: #0f172a; }
          .meta { color: #64748b; font-size: 12px; margin-top: 4px; }
          .score-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 24px; margin: 20px 0; display: flex; justify-content: space-between; align-items: center; }
          .score-val { font-size: 36px; font-weight: 900; color: #0284c7; }
          .verdict { font-size: 16px; font-weight: 700; color: #0369a1; }
          .section-title { font-size: 15px; font-weight: 700; margin-top: 24px; margin-bottom: 10px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; color: #334155; }
          table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
          th { background: #f1f5f9; text-align: left; padding: 8px 12px; border: 1px solid #cbd5e1; font-weight: 700; }
          td { padding: 8px 12px; border: 1px solid #e2e8f0; }
          .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 10px; text-transform: uppercase; }
          .high { background: #ffe4e6; color: #e11d48; }
          .medium { background: #fef3c7; color: #d97706; }
          .low { background: #e0f2fe; color: #0284c7; }
          .overview { background: #f8fafc; border-left: 4px solid #0284c7; padding: 12px 16px; font-size: 13px; line-height: 1.6; color: #334155; border-radius: 0 8px 8px 0; }
          @media print { body { margin: 20px; } }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <div class="title">🛡️ Smart Code Inspection Report</div>
            <div class="meta">Target File: <strong>${displayFileName}</strong> (${language.toUpperCase()}) | ID: <code>${analysisId}</code></div>
          </div>
          <div style="text-align: right;" class="meta">
            <div>Generated: ${dateStr}</div>
            <div>CodeGuard AI Platform</div>
          </div>
        </div>

        <div class="score-box">
          <div>
            <div class="verdict">${prSummaryResult.verdict}</div>
            <div class="meta">Overall Automated Multi-Agent Assessment</div>
          </div>
          <div style="text-align: right;">
            <div class="score-val">${prSummaryResult.health_score}/100</div>
            <div style="font-size: 11px; color: #64748b; font-weight: 700;">CODE HEALTH SCORE</div>
          </div>
        </div>

        <div class="section-title">Executive Summary</div>
        <div class="overview">${prSummaryResult.executive_overview}</div>

        <div class="section-title">Severity Breakdown</div>
        <table>
          <tr>
            <th>High Severity Risks</th>
            <th>Medium Issues</th>
            <th>Low / Code Smells</th>
            <th>Total Findings</th>
          </tr>
          <tr>
            <td><span class="badge high">${prSummaryResult.severity_breakdown.high} High</span></td>
            <td><span class="badge medium">${prSummaryResult.severity_breakdown.medium} Medium</span></td>
            <td><span class="badge low">${prSummaryResult.severity_breakdown.low} Low</span></td>
            <td><strong>${prSummaryResult.severity_breakdown.total} issues</strong></td>
          </tr>
        </table>

        <div class="section-title">Prioritized Fix Roadmap</div>
        <table>
          <thead>
            <tr>
              <th style="width: 40px;">Rank</th>
              <th>Issue Title</th>
              <th style="width: 50px;">Line</th>
              <th style="width: 70px;">Severity</th>
              <th>Recommended Action</th>
            </tr>
          </thead>
          <tbody>
            ${prSummaryResult.prioritized_fixes.map(f => `
              <tr>
                <td><strong>#${f.priority}</strong></td>
                <td><strong>${f.title}</strong></td>
                <td>L${f.line}</td>
                <td><span class="badge ${f.severity.toLowerCase()}">${f.severity}</span></td>
                <td>${f.action_required}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>

        <div style="margin-top: 40px; font-size: 11px; color: #94a3b8; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 12px;">
          Smart Code Inspection Platform with Vulnerability Detection System • Automated Code Review Report
        </div>
        <script>
          window.onload = function() { window.print(); }
        </script>
      </body>
      </html>
    `;
    printWindow.document.write(html);
    printWindow.document.close();
  };

  const getFindingCategory = (item) => {
    const type = String(item.type || "").toLowerCase();
    const title = String(item.title || "").toLowerCase();
    const securityKeywords = [
      "security", "vulnerability", "injection", "xss", "csrf", "secret", "hash", "command", "authentication", "authorization"
    ];
    return securityKeywords.some(k => type.includes(k) || title.includes(k)) ? "security" : "quality";
  };

  const filteredFindings = findings.filter((item) => {
    if (activeFilter === "all") return true;
    return getFindingCategory(item) === activeFilter;
  });

  return (
    <div className="space-y-6">
      {/* ==============================================
          OVERVIEW CARD & HEALTH SCORE
      =============================================== */}
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
            <p className="mt-0.5 text-xs text-slate-400 font-mono">
              File: <span className="text-white font-semibold">{displayFileName}</span> • ID: {analysisId}
            </p>
          </div>
        </div>

        {/* 5 Metrics Summary Grid */}
        <div className="grid gap-3 sm:grid-cols-5">
          <SummaryCard label="Total Findings" value={findings.length} icon={ShieldAlert} />
          <SummaryCard label="High Severity" value={highCount} tone="rose" />
          <SummaryCard label="Medium Severity" value={mediumCount} tone="amber" />
          <SummaryCard label="Low / Code Smells" value={lowCount} tone="cyan" />
          <SummaryCard
            label="Health Score"
            value={`${healthScore}/100`}
            tone={healthScore >= 80 ? "emerald" : healthScore >= 50 ? "amber" : "rose"}
            icon={Activity}
          />
        </div>

        {/* Info badges */}
        <div className="mt-3 grid gap-2.5 sm:grid-cols-4">
          <Info icon={FileCode2} label="Source File" value={displayFileName} />
          <Info icon={Languages} label="Language" value={String(language).toUpperCase()} />
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

      {/* ==============================================
          SYNTAX ERRORS IF ANY
      =============================================== */}
      {errors.length > 0 && (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-rose-300">
            <AlertTriangle size={18} />
            <span>Syntax Errors ({errors.length})</span>
          </div>
          <div className="space-y-2">
            {errors.map((err, idx) => (
              <div key={idx} className="rounded-xl border border-rose-500/20 bg-slate-950/60 p-3 text-xs">
                <div className="mb-1 font-mono font-bold text-rose-400">Line {err.line ?? "—"}</div>
                <p className="text-slate-300">{err.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ==============================================
          MAIN INTERACTIVE NAVIGATION TAB BAR
          (Allows in-place switching without scrolling!)
      =============================================== */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-1.5 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            type="button"
            onClick={() => setActiveTab("findings")}
            className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition ${
              activeTab === "findings"
                ? "bg-cyan-400/15 text-cyan-200 border border-cyan-400/30 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <ShieldAlert size={15} />
            <span>Findings & Issues</span>
            <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300">
              {findings.length}
            </span>
          </button>

          <button
            type="button"
            onClick={handleGeneratePRSummary}
            disabled={prSummaryLoading}
            className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition ${
              activeTab === "summary"
                ? "bg-indigo-500/20 text-indigo-200 border border-indigo-400/30 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <FileText size={15} />
            <span>{prSummaryLoading ? "Compiling PR..." : "PR Review Summary"}</span>
            {prSummaryResult && (
              <span className="rounded-full bg-indigo-500/30 px-2 py-0.5 text-[10px] text-indigo-300 font-mono">
                {prSummaryResult.health_score}%
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={handleGenerateRemediation}
            disabled={remediationLoading}
            className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition ${
              activeTab === "remediation"
                ? "bg-emerald-500/20 text-emerald-200 border border-emerald-400/30 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <Sparkles size={15} />
            <span>{remediationLoading ? "Generating Fixes..." : "AI Remediation Roadmap"}</span>
            {remediationResult && (
              <span className="rounded-full bg-emerald-500/30 px-2 py-0.5 text-[10px] text-emerald-300">
                Ready
              </span>
            )}
          </button>
        </div>

        <button
          type="button"
          onClick={() => setIsAssistantOpen(true)}
          className="flex items-center gap-2 rounded-xl border border-emerald-400/30 bg-emerald-500/10 px-3.5 py-2 text-xs font-bold text-emerald-200 hover:bg-emerald-500/20 transition"
        >
          <Bot size={15} />
          <span>Ask Code Assistant</span>
        </button>
      </div>

      {/* ==============================================
          TAB 1: UNIFIED FINDINGS LIST
      =============================================== */}
      {activeTab === "findings" && (
        <div className="rounded-2xl border border-slate-700/80 bg-slate-900/50 p-5 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div className="flex flex-wrap gap-2">
              <FilterButton active={activeFilter === "all"} onClick={() => setActiveFilter("all")}>
                All <span className="ml-1.5 opacity-60">({findings.length})</span>
              </FilterButton>
              <FilterButton active={activeFilter === "quality"} onClick={() => setActiveFilter("quality")}>
                <Code2 size={13} className="mr-1 inline" />
                Code Quality
                <span className="ml-1 opacity-60">
                  ({findings.filter((i) => getFindingCategory(i) === "quality").length})
                </span>
              </FilterButton>
              <FilterButton active={activeFilter === "security"} onClick={() => setActiveFilter("security")}>
                <ShieldAlert size={13} className="mr-1 inline" />
                Security Risks
                <span className="ml-1 opacity-60">
                  ({findings.filter((i) => getFindingCategory(i) === "security").length})
                </span>
              </FilterButton>
            </div>

            <div className="text-xs text-slate-500 font-mono">
              Showing {filteredFindings.length} of {findings.length} findings
            </div>
          </div>

          {filteredFindings.length > 0 ? (
            <div className="space-y-4">
              {filteredFindings.map((item, idx) => {
                const sev = (item.severity || "low").toLowerCase();
                const category = getFindingCategory(item);
                const sevBadge =
                  sev === "high"
                    ? "border-rose-400/30 bg-rose-400/10 text-rose-300"
                    : sev === "medium"
                    ? "border-amber-400/30 bg-amber-400/10 text-amber-300"
                    : "border-cyan-400/30 bg-cyan-400/10 text-cyan-300";

                return (
                  <div key={idx} className="rounded-xl border border-slate-700/70 bg-slate-950/60 p-4 transition hover:border-slate-600">
                    <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`rounded-md border px-2 py-0.5 text-[11px] font-bold uppercase ${sevBadge}`}>
                          {item.severity || "low"}
                        </span>
                        <span className="flex items-center gap-1 text-xs font-mono uppercase tracking-wider text-slate-400">
                          {category === "security" ? <ShieldAlert size={12} className="text-rose-400" /> : <Code2 size={12} className="text-cyan-400" />}
                          {category === "security" ? "Security" : "Code Quality"}
                        </span>
                      </div>
                      <span className="rounded border border-slate-700 bg-slate-800/80 px-2 py-0.5 font-mono text-[11px] text-slate-300">
                        Line {item.line ?? "—"}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-slate-100">{item.title}</h4>
                    <p className="mt-1 text-xs text-slate-400 leading-relaxed">{item.description}</p>

                    {item.code_snippet && (
                      <div className="mt-2.5 rounded-lg border border-slate-800 bg-slate-900/80 p-2.5">
                        <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">Flagged Snippet</p>
                        <pre className="overflow-x-auto font-mono text-xs text-slate-200">
                          <code>{item.code_snippet}</code>
                        </pre>
                      </div>
                    )}

                    {item.recommendation && (
                      <div className="mt-2.5 rounded-lg border border-cyan-400/15 bg-cyan-400/5 p-2.5 text-xs text-cyan-200/90 leading-relaxed">
                        <div className="flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-cyan-300 mb-1">
                          <Lightbulb size={12} />
                          <span>RAG Knowledge Base Guidance</span>
                        </div>
                        <p className="whitespace-pre-line">{item.recommendation}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-6 text-center">
              <p className="text-xs font-semibold text-emerald-300">
                ✓ No findings match the active filter.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ==============================================
          TAB 2: PR REVIEW SUMMARY (IN-PLACE VIEW!)
      =============================================== */}
      {activeTab === "summary" && (
        <div className="rounded-2xl border border-indigo-400/30 bg-gradient-to-br from-indigo-950/30 via-slate-900/70 to-slate-950/80 p-6 shadow-glow space-y-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-indigo-400/20 pb-4">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-indigo-400/20 bg-indigo-500/10 px-3 py-1 text-xs font-bold text-indigo-200 mb-2">
                <FileText size={14} />
                Pull Request Review Summary
              </div>
              <h3 className="text-xl font-extrabold text-white">Automated PR Review Assessment</h3>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">Analysis ID: {analysisId}</p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={handleCopyPRMarkdown}
                disabled={!prSummaryResult}
                className="flex items-center gap-1.5 rounded-xl border border-indigo-400/40 bg-indigo-500/20 px-3.5 py-2 text-xs font-bold text-indigo-200 hover:bg-indigo-500/30 transition shadow-sm disabled:opacity-50"
              >
                {prSummaryCopied ? <Check size={14} className="text-emerald-300" /> : <Copy size={14} />}
                <span>{prSummaryCopied ? "Markdown Copied!" : "Copy GitHub Markdown"}</span>
              </button>

              <button
                type="button"
                onClick={handleDownloadPDF}
                disabled={!prSummaryResult}
                className="flex items-center gap-1.5 rounded-xl border border-cyan-400/40 bg-cyan-400/20 px-3.5 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-400/30 transition shadow-sm disabled:opacity-50"
              >
                <Download size={14} />
                <span>Download PDF Report</span>
              </button>
            </div>
          </div>

          {prSummaryLoading && (
            <div className="p-12 text-center text-sm text-indigo-200">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent mx-auto mb-3" />
              Compiling structured Pull Request review with health scoring...
            </div>
          )}

          {prSummaryError && (
            <div className="rounded-xl border border-rose-400/20 bg-rose-400/10 p-4 text-xs text-rose-300">
              {prSummaryError}
            </div>
          )}

          {!prSummaryLoading && prSummaryResult && (
            <div className="space-y-6">
              {/* Verdict & Health Score Banner */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-xl border border-indigo-400/20 bg-slate-950/60 p-4">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-indigo-300 mb-1">Review Verdict</p>
                  <p className="text-lg font-bold text-white">{prSummaryResult.verdict}</p>
                </div>
                <div className="rounded-xl border border-indigo-400/20 bg-slate-950/60 p-4 flex items-center justify-between">
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-wider text-indigo-300 mb-1">Code Health Score</p>
                    <p className="text-xs text-slate-400">Severity penalty algorithm</p>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-extrabold text-indigo-300 font-mono">
                      {prSummaryResult.health_score}/100
                    </span>
                  </div>
                </div>
              </div>

              {/* Executive Overview */}
              <div className="rounded-xl border border-indigo-400/20 bg-slate-950/60 p-4">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-indigo-300 mb-2">Executive Overview</p>
                <p className="text-xs text-slate-300 leading-relaxed">{prSummaryResult.executive_overview}</p>
              </div>

              {/* Severity Breakdown */}
              <div className="grid gap-3 sm:grid-cols-4">
                <div className="rounded-xl border border-rose-400/20 bg-rose-400/5 p-3">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-rose-400">High Severity</p>
                  <p className="text-xl font-bold text-rose-200 mt-1">{prSummaryResult.severity_breakdown.high}</p>
                </div>
                <div className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-3">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400">Medium Severity</p>
                  <p className="text-xl font-bold text-amber-200 mt-1">{prSummaryResult.severity_breakdown.medium}</p>
                </div>
                <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/5 p-3">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-cyan-400">Low / Code Smells</p>
                  <p className="text-xl font-bold text-cyan-200 mt-1">{prSummaryResult.severity_breakdown.low}</p>
                </div>
                <div className="rounded-xl border border-slate-700 bg-slate-800/40 p-3">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Total Issues</p>
                  <p className="text-xl font-bold text-slate-200 mt-1">{prSummaryResult.severity_breakdown.total}</p>
                </div>
              </div>

              {/* Prioritized Fix Checklist Table */}
              <div className="rounded-xl border border-slate-700/80 bg-slate-950/60 p-4">
                <div className="flex items-center gap-2 mb-3">
                  <ListOrdered size={16} className="text-indigo-300" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-200">
                    Prioritized Fix Checklist ({prSummaryResult.prioritized_fixes.length})
                  </h4>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                        <th className="py-2.5 px-3">Rank</th>
                        <th className="py-2.5 px-3">Issue</th>
                        <th className="py-2.5 px-3">Line</th>
                        <th className="py-2.5 px-3">Severity</th>
                        <th className="py-2.5 px-3">Recommended Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono">
                      {prSummaryResult.prioritized_fixes.map((fix) => {
                        const sev = (fix.severity || "").toLowerCase();
                        const badgeColor =
                          sev === "high"
                            ? "text-rose-400 bg-rose-500/10 border-rose-500/20"
                            : sev === "medium"
                            ? "text-amber-400 bg-amber-500/10 border-amber-500/20"
                            : "text-cyan-400 bg-cyan-500/10 border-cyan-500/20";

                        return (
                          <tr key={fix.priority} className="hover:bg-slate-900/40 transition">
                            <td className="py-3 px-3 font-bold text-cyan-300">#{fix.priority}</td>
                            <td className="py-3 px-3 font-sans font-semibold text-slate-200">{fix.title}</td>
                            <td className="py-3 px-3 text-slate-400">L{fix.line}</td>
                            <td className="py-3 px-3">
                              <span className={`inline-block px-2 py-0.5 rounded border text-[10px] font-bold uppercase ${badgeColor}`}>
                                {fix.severity}
                              </span>
                            </td>
                            <td className="py-3 px-3 font-sans text-slate-300 leading-relaxed">{fix.action_required}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ==============================================
          TAB 3: AI REMEDIATION ROADMAP (IN-PLACE VIEW!)
      =============================================== */}
      {activeTab === "remediation" && (
        <div className="rounded-2xl border border-cyan-400/30 bg-gradient-to-br from-cyan-950/30 via-slate-900/70 to-slate-950/80 p-6 shadow-glow space-y-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-cyan-400/20 pb-4">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-500/10 px-3 py-1 text-xs font-bold text-cyan-200 mb-2">
                <Sparkles size={14} />
                AI Remediation Agent
              </div>
              <h3 className="text-xl font-extrabold text-white">Before / After Code Corrections</h3>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">Analysis ID: {analysisId}</p>
            </div>
          </div>

          {remediationLoading && (
            <div className="p-12 text-center text-sm text-cyan-200">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent mx-auto mb-3" />
              Generating side-by-side secure code refactoring with Gemini LLM & RAG...
            </div>
          )}

          {remediationError && (
            <div className="rounded-xl border border-rose-400/20 bg-rose-400/10 p-4 text-xs text-rose-300">
              {remediationError}
            </div>
          )}

          {!remediationLoading && remediationResult && (
            <div className="space-y-6">
              {remediationResult.remediations?.map((rem, idx) => (
                <div key={idx} className="rounded-xl border border-slate-700/80 bg-slate-950/70 p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="rounded bg-cyan-400/10 px-2 py-0.5 font-mono text-[11px] font-bold text-cyan-300">
                        Finding #{idx + 1}
                      </span>
                      <h4 className="text-sm font-bold text-white">{rem.finding_title || `Issue on line ${rem.line}`}</h4>
                    </div>
                    <span className="font-mono text-xs text-slate-500">Line {rem.line}</span>
                  </div>

                  {/* Recommendation Overview */}
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-wider text-cyan-300 mb-1">Recommended Fix</p>
                    <p className="text-xs text-slate-200 leading-relaxed">{rem.recommendation}</p>
                  </div>

                  {/* Side by side code or corrected code block */}
                  <div className="grid gap-3 lg:grid-cols-2">
                    {rem.original_code && (
                      <div className="rounded-lg border border-rose-500/20 bg-rose-950/20 p-3">
                        <p className="text-[10px] font-bold uppercase tracking-wider text-rose-400 mb-1.5 flex items-center gap-1">
                          <CircleAlert size={11} />
                          Original Vulnerable Code
                        </p>
                        <pre className="overflow-x-auto font-mono text-xs text-rose-200 p-2 rounded bg-slate-950/60">
                          <code>{rem.original_code}</code>
                        </pre>
                      </div>
                    )}

                    <div className={`rounded-lg border border-emerald-500/20 bg-emerald-950/20 p-3 ${!rem.original_code ? 'lg:col-span-2' : ''}`}>
                      <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-1.5 flex items-center gap-1">
                        <CheckCircle2 size={11} />
                        Corrected Secure Code
                      </p>
                      <pre className="overflow-x-auto font-mono text-xs text-emerald-200 p-2 rounded bg-slate-950/60">
                        <code>{rem.corrected_code}</code>
                      </pre>
                    </div>
                  </div>

                  {/* Explanations & Why it works */}
                  <div className="grid gap-3 sm:grid-cols-2 text-xs">
                    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
                      <p className="font-bold text-slate-300 mb-1">Explanation</p>
                      <p className="text-slate-400 leading-relaxed">{rem.explanation}</p>
                    </div>
                    <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
                      <p className="font-bold text-slate-300 mb-1">Why It Works</p>
                      <p className="text-slate-400 leading-relaxed">{rem.why_it_works}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
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

function Info({ icon: Icon, label, value, highlight }) {
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
      <p className={`mt-0.5 text-xs font-bold ${textColor}`}>{value}</p>
    </div>
  );
}

function SummaryCard({ label, value, icon: Icon, tone = "slate" }) {
  const styles = {
    slate: { border: "border-slate-700/60", bg: "bg-slate-950/45", text: "text-slate-200" },
    rose: { border: "border-rose-400/20", bg: "bg-rose-400/5", text: "text-rose-300" },
    amber: { border: "border-amber-400/20", bg: "bg-amber-400/5", text: "text-amber-300" },
    cyan: { border: "border-cyan-400/20", bg: "bg-cyan-400/5", text: "text-cyan-300" },
    emerald: { border: "border-emerald-400/20", bg: "bg-emerald-400/5", text: "text-emerald-300" }
  };
  const style = styles[tone];

  return (
    <div className={`rounded-xl border ${style.border} ${style.bg} p-4`}>
      <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase tracking-wider text-slate-500">{label}</span>
        {Icon && <Icon size={15} className={style.text} />}
      </div>
      <p className={`mt-2 text-2xl font-bold ${style.text}`}>{value}</p>
    </div>
  );
}

function FilterButton({ active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
        active
          ? "border-cyan-400/30 bg-cyan-400/10 text-cyan-200"
          : "border-slate-700/70 bg-slate-950/40 text-slate-400 hover:border-slate-600 hover:text-slate-200"
      }`}
    >
      {children}
    </button>
  );
}