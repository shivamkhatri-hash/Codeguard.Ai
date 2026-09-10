import { Component } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen grid-bg flex items-center justify-center p-6 text-slate-100">
          <div className="max-w-md w-full glass rounded-2xl p-8 border border-rose-500/30 text-center space-y-4 shadow-2xl">
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-rose-500/10 text-rose-400 mx-auto">
              <AlertCircle size={28} />
            </div>
            <h2 className="text-xl font-bold text-white">Something went wrong</h2>
            <p className="text-xs text-slate-400">
              {this.state.error?.message || "An unexpected UI rendering error occurred."}
            </p>
            <button
              type="button"
              onClick={this.handleReset}
              className="inline-flex items-center justify-center gap-2 w-full rounded-xl bg-gradient-to-r from-cyan-400 to-blue-600 px-5 py-3 text-xs font-bold text-slate-950 shadow-glow hover:opacity-90 transition"
            >
              <RefreshCw size={15} />
              <span>Reset & Reload Workspace</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
