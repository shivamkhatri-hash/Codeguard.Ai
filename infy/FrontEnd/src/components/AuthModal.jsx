import { useState } from "react";
import { X, Lock, Mail, User, ShieldCheck, AlertCircle, Eye, EyeOff } from "lucide-react";
import { loginUser, signupUser } from "../services/api";

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      let res;
      if (isSignUp) {
        if (!fullName.trim()) {
          throw new Error("Please enter your full name.");
        }
        res = await signupUser({ email, password, full_name: fullName, role: "developer" });
      } else {
        res = await loginUser({ email, password });
      }
      onAuthSuccess(res);
      onClose();
    } catch (err) {
      setError(err.message || "Authentication failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="auth-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 p-4 backdrop-blur-xl animate-fadeIn"
    >
      {/* Background Radial Glow */}
      <div className="pointer-events-none absolute h-96 w-96 rounded-full bg-cyan-500/10 blur-[120px]" />

      <div className="relative w-full max-w-md overflow-hidden rounded-3xl border border-cyan-400/25 bg-slate-900/95 p-6 sm:p-8 shadow-[0_0_50px_rgba(34,211,238,0.15)] backdrop-blur-2xl transition-all">
        {/* Top Accent Line */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500" />

        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close dialog"
          className="absolute right-4 top-4 rounded-xl p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition"
        >
          <X size={18} />
        </button>

        {/* Brand Icon Header */}
        <div className="text-center">
          <div className="mx-auto mb-3 grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-cyan-300 via-blue-500 to-indigo-600 text-slate-950 shadow-glow">
            <ShieldCheck size={30} />
          </div>
          <h3 id="auth-modal-title" className="text-2xl font-black text-white tracking-tight">
            {isSignUp ? "Join CodeGuard AI" : "Welcome Back"}
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            {isSignUp
              ? "Register a Developer account to analyze code & remediate vulnerabilities"
              : "Sign in to access your code inspection reports & AI assistant"}
          </p>
        </div>

        {/* Segmented Mode Switcher */}
        <div className="mt-6 grid grid-cols-2 rounded-xl bg-slate-950 p-1 border border-slate-800">
          <button
            type="button"
            onClick={() => {
              setIsSignUp(false);
              setError("");
            }}
            className={`py-2 text-xs font-extrabold rounded-lg transition ${
              !isSignUp
                ? "bg-cyan-400/15 text-cyan-200 shadow-glow border border-cyan-400/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign In
          </button>

          <button
            type="button"
            onClick={() => {
              setIsSignUp(true);
              setError("");
            }}
            className={`py-2 text-xs font-extrabold rounded-lg transition ${
              isSignUp
                ? "bg-cyan-400/15 text-cyan-200 shadow-glow border border-cyan-400/30"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mt-4 flex items-center gap-2.5 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs font-medium text-rose-200">
            <AlertCircle size={16} className="shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Form Inputs */}
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          {isSignUp && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-bold text-slate-300">Full Name</label>
                <span className="text-[10px] font-mono text-cyan-400 bg-cyan-400/10 px-2 py-0.5 rounded border border-cyan-400/20">Role: Developer</span>
              </div>
              <div className="relative">
                <User size={16} className="absolute left-3.5 top-3 text-slate-500" />
                <input
                  type="text"
                  required
                  placeholder="Sumit Kumar Singh"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950/80 py-2.5 pl-10 pr-3 text-sm text-white placeholder-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-300 mb-1">Email Address</label>
            <div className="relative">
              <Mail size={16} className="absolute left-3.5 top-3 text-slate-500" />
              <input
                type="email"
                required
                placeholder="developer@codeguard.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950/80 py-2.5 pl-10 pr-3 text-sm text-white placeholder-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-300 mb-1">Password</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3.5 top-3 text-slate-500" />
              <input
                type={showPassword ? "text" : "password"}
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950/80 py-2.5 pl-10 pr-10 text-sm text-white placeholder-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3 text-slate-500 hover:text-slate-300"
              >
                {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-gradient-to-r from-cyan-300 via-blue-500 to-indigo-600 py-3 text-sm font-black text-slate-950 shadow-glow transition hover:opacity-90 active:scale-[0.99] disabled:opacity-50"
          >
            {loading ? "Authenticating..." : isSignUp ? "Create Developer Account" : "Sign In to Platform"}
          </button>
        </form>

        {/* Footer Toggle */}
        <div className="mt-5 text-center text-xs text-slate-400 border-t border-slate-800/80 pt-4">
          {isSignUp ? "Already registered?" : "Need a developer account?"}{" "}
          <button
            type="button"
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError("");
            }}
            className="font-bold text-cyan-300 hover:underline"
          >
            {isSignUp ? "Sign In Here" : "Create Account Now"}
          </button>
        </div>
      </div>
    </div>
  );
}
