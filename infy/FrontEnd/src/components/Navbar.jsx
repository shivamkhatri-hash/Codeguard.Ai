import { BarChart3, Clock3, Code2, ShieldCheck, TerminalSquare } from "lucide-react";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", icon: BarChart3 },
  { id: "analyze", label: "Analyze", icon: Code2 },
  { id: "history", label: "History", icon: Clock3 }
];

export default function Navbar({ activePage, onNavigate }) {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/70 bg-[#050b14]/85 backdrop-blur-2xl">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 lg:px-8">
        <button
          type="button"
          onClick={() => onNavigate("dashboard")}
          className="group flex items-center gap-3 text-left"
        >
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-cyan-300 to-blue-600 text-slate-950 shadow-glow transition duration-300 group-hover:scale-105">
            <TerminalSquare size={21} />
          </div>
          <div>
            <p className="text-sm font-extrabold tracking-tight text-white">CodeGuard AI</p>
            <p className="hidden text-[10px] text-slate-500 sm:block">Code Quality • Security • Intelligence</p>
          </div>
        </button>

        <nav className="hidden items-center gap-1 rounded-xl border border-slate-800/80 bg-slate-950/40 p-1 md:flex">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
            const active = activePage === id;
            return (
              <button
                key={id}
                type="button"
                onClick={() => onNavigate(id)}
                className={`flex items-center gap-2 rounded-lg px-3.5 py-2 text-xs font-semibold transition ${
                  active
                    ? "bg-cyan-400/10 text-cyan-200 shadow-[inset_0_0_0_1px_rgba(34,211,238,.14)]"
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-white"
                }`}
              >
                <Icon size={15} />
                {label}
              </button>
            );
          })}
        </nav>

        <div className="flex items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/5 px-3 py-1.5 text-[11px] font-medium text-emerald-200">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
          </span>
          <span className="hidden sm:inline">System Online</span>
          <ShieldCheck size={14} />
        </div>
      </div>

      <div className="mx-auto flex max-w-7xl gap-1 overflow-x-auto px-5 pb-2 md:hidden lg:px-8">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => onNavigate(id)}
            className={`flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold ${
              activePage === id ? "bg-cyan-400/10 text-cyan-200" : "text-slate-500"
            }`}
          >
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>
    </header>
  );
}
