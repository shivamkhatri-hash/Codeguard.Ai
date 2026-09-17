import { Home, BarChart3, Clock3, Code2, ShieldCheck, TerminalSquare, ShieldAlert, User, LogIn, LogOut, Sun, Moon } from "lucide-react";

export default function Navbar({ activePage, onNavigate, authUser, onOpenAuth, onLogout, theme, onToggleTheme }) {
  const navItems = [
    { id: "landing", label: "Home", icon: Home },
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "analyze", label: "Analyze", icon: Code2 },
    { id: "history", label: "History", icon: Clock3 }
  ];

  if (authUser?.role === "admin") {
    navItems.push({ id: "admin", label: "Admin SOC", icon: ShieldAlert });
  }

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/70 bg-[#050b14]/85 backdrop-blur-2xl">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 lg:px-8">
        <button
          type="button"
          onClick={() => onNavigate("landing")}
          aria-label="CodeGuard AI Home"
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

        <nav aria-label="Main Navigation" className="hidden items-center gap-1 rounded-xl border border-slate-800/80 bg-slate-950/40 p-1 md:flex">
          {navItems.map(({ id, label, icon: Icon }) => {
            const active = activePage === id;
            return (
              <button
                key={id}
                type="button"
                onClick={() => onNavigate(id)}
                aria-current={active ? "page" : undefined}
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

        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Light / Dark Mode Toggle Button */}
          {onToggleTheme && (
            <button
              type="button"
              onClick={onToggleTheme}
              aria-label="Toggle Theme"
              className="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-700/80 bg-slate-900/80 text-slate-300 transition hover:bg-slate-800 hover:text-white shadow-sm"
              title={theme === "light" ? "Switch to Dark Mode" : "Switch to Light Mode"}
            >
              {theme === "light" ? (
                <Moon size={16} className="text-indigo-500" />
              ) : (
                <Sun size={16} className="text-amber-400" />
              )}
            </button>
          )}

          {authUser ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-1.5 text-xs font-semibold text-slate-200">
                <div className="grid h-6 w-6 place-items-center rounded-md bg-cyan-400/10 font-mono text-cyan-300">
                  {authUser.full_name?.charAt(0) || "U"}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-xs font-bold text-white leading-none">{authUser.full_name}</p>
                  <p className="text-[10px] text-cyan-400 uppercase font-mono leading-none mt-0.5">{authUser.role}</p>
                </div>
              </div>

              <button
                type="button"
                onClick={onLogout}
                aria-label="Sign Out"
                className="flex items-center gap-1 rounded-xl border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-xs font-bold text-rose-300 hover:bg-rose-500/20 transition"
                title="Sign Out"
              >
                <LogOut size={14} />
                <span className="hidden sm:inline">Sign Out</span>
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenAuth}
              aria-label="Sign In or Sign Up"
              className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-600 px-4 py-2 text-xs font-bold text-slate-950 shadow-glow transition hover:opacity-90"
            >
              <LogIn size={15} />
              <span>Sign In / Sign Up</span>
            </button>
          )}
        </div>
      </div>

      {/* Mobile nav bar */}
      <nav aria-label="Mobile Navigation" className="mx-auto flex max-w-7xl gap-1 overflow-x-auto px-5 pb-2 md:hidden lg:px-8">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => onNavigate(id)}
            aria-current={activePage === id ? "page" : undefined}
            className={`flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold ${
              activePage === id ? "bg-cyan-400/10 text-cyan-200" : "text-slate-500"
            }`}
          >
            <Icon size={14} />
            {label}
          </button>
        ))}
      </nav>
    </header>
  );
}
