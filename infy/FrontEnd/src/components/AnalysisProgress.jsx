import {
  Check,
  CircleDot,
  GitMerge,
  LoaderCircle,
  ScanSearch,
  ShieldCheck,
} from "lucide-react";

function AgentCard({ icon: Icon, title, description }) {
  return (
    <div className="rounded-xl border border-cyan-400/15 bg-slate-950/45 p-4">
      <div className="flex items-start gap-3">
        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-cyan-400/10">
          <Icon size={18} className="text-cyan-300" />
        </div>

        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">{title}</h3>
            <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
          </div>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            {description}
          </p>

          <div className="mt-3 flex items-center gap-2 text-xs text-cyan-200">
            <LoaderCircle size={13} className="animate-spin" />
            Running analysis...
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AnalysisProgress({ language }) {
  return (
    <section className="mt-6 overflow-hidden rounded-2xl border border-cyan-400/10 bg-slate-900/50">
      {/* Header */}
      <div className="border-b border-slate-800/80 px-5 py-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="grid h-8 w-8 place-items-center rounded-lg bg-cyan-400/10">
                <ScanSearch size={16} className="text-cyan-300" />
              </div>

              <div>
                <h2 className="text-sm font-bold text-white">
                  Analysis in progress
                </h2>

                <p className="mt-0.5 text-xs text-slate-500">
                  Analyzing {language || "source"} code with specialized agents
                </p>
              </div>
            </div>
          </div>

          <span className="hidden rounded-full border border-cyan-400/15 bg-cyan-400/5 px-3 py-1.5 text-[11px] font-semibold text-cyan-200 sm:inline-flex">
            Multi-agent analysis
          </span>
        </div>
      </div>

      {/* Pipeline */}
      <div className="p-5">
        {/* Syntax validation */}
        <div className="flex items-center gap-3 rounded-xl border border-emerald-400/10 bg-emerald-400/5 p-4">
          <div className="grid h-9 w-9 place-items-center rounded-lg bg-emerald-400/10">
            <Check size={17} className="text-emerald-300" />
          </div>

          <div>
            <p className="text-sm font-semibold text-white">
              Syntax validation
            </p>

            <p className="text-xs text-emerald-200/70">
              Source code received successfully
            </p>
          </div>

          <span className="ml-auto text-[11px] font-semibold uppercase tracking-wider text-emerald-300">
            Complete
          </span>
        </div>

        {/* Connector */}
        <div className="mx-auto h-5 w-px bg-slate-700" />

        {/* Agents */}
        <div className="grid gap-4 md:grid-cols-2">
          <AgentCard
            icon={ScanSearch}
            title="Code Analysis Agent"
            description="Detecting code smells, complexity issues, design anti-patterns and poor coding practices."
          />

          <AgentCard
            icon={ShieldCheck}
            title="Security Vulnerability Agent"
            description="Scanning for OWASP-standard vulnerabilities, secrets and security weaknesses."
          />
        </div>

        {/* Connector */}
        <div className="mx-auto h-5 w-px bg-slate-700" />

        {/* Orchestrator */}
        <div className="rounded-xl border border-indigo-400/15 bg-indigo-400/5 p-4">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-lg bg-indigo-400/10">
              <GitMerge size={17} className="text-indigo-300" />
            </div>

            <div>
              <p className="text-sm font-semibold text-white">
                Parallel Orchestrator
              </p>

              <p className="mt-0.5 text-xs text-slate-500">
                Waiting for both agents to complete before merging findings.
              </p>
            </div>

            <div className="ml-auto">
              <CircleDot
                size={16}
                className="animate-pulse text-indigo-300"
              />
            </div>
          </div>
        </div>

        {/* Bottom status */}
        <div className="mt-4 flex items-center justify-center gap-2 text-xs text-slate-500">
          <LoaderCircle size={13} className="animate-spin text-cyan-300" />
          <span>
            Please wait while CodeGuard analyzes your {language || "source"} code...
          </span>
        </div>
      </div>
    </section>
  );
}