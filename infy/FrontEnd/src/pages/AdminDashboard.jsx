import { useEffect, useState } from "react";
import {
  Users,
  ShieldAlert,
  BarChart3,
  ShieldCheck,
  UserCheck,
  UserX,
  RefreshCw,
  FileCode,
  Lock,
  Terminal,
  Activity,
  AlertCircle
} from "lucide-react";
import { getAdminStats, getAdminUsers, toggleUserStatus } from "../services/api";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [togglingId, setTogglingId] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [statsData, usersData] = await Promise.all([
        getAdminStats(),
        getAdminUsers()
      ]);
      setStats(statsData);
      setUsers(usersData);
    } catch (err) {
      setError(err.message || "Failed to load admin telemetry data. Admin credentials required.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleUser = async (userId) => {
    setTogglingId(userId);
    try {
      const res = await toggleUserStatus(userId);
      setUsers((prev) =>
        prev.map((u) => (u.user_id === userId ? { ...u, is_active: Boolean(res.is_active) } : u))
      );
      const updatedStats = await getAdminStats();
      setStats(updatedStats);
    } catch (err) {
      alert(err.message || "Failed to update user status.");
    } finally {
      setTogglingId("");
    }
  };

  if (loading) {
    return (
      <main className="min-h-[calc(100vh-72px)] grid-bg px-5 py-12 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="glass rounded-2xl p-8 text-center text-slate-400">
            <RefreshCw size={24} className="mx-auto mb-3 animate-spin text-cyan-400" />
            <p>Loading Admin Telemetry & User Registry...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-[calc(100vh-72px)] grid-bg px-5 py-12 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-8 text-center text-rose-200">
            <Lock size={40} className="mx-auto mb-3 text-rose-400" />
            <h2 className="text-xl font-bold text-white">Admin Access Restricted</h2>
            <p className="mt-2 text-sm text-slate-300">{error}</p>
            <p className="mt-4 text-xs text-slate-400">Please sign in as Administrator (<code>admin@codeguard.ai</code> / password: <code>admin</code>) to view platform management telemetry.</p>
          </div>
        </div>
      </main>
    );
  }

  const threatDist = stats?.threat_distribution || {};
  const totalThreats = Object.values(threatDist).reduce((a, b) => a + b, 0) || 1;

  return (
    <main className="min-h-[calc(100vh-72px)] grid-bg px-5 py-12 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Header Banner */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded-md bg-indigo-500/10 px-2.5 py-1 font-mono text-xs font-bold text-indigo-300 border border-indigo-500/20">
                ADMIN SOC PORTAL
              </span>
              <span className="text-xs text-slate-400">• Security Operations Center</span>
            </div>
            <h1 className="mt-2 text-3xl font-black tracking-tight text-white">Platform Security & User Administration</h1>
            <p className="text-sm text-slate-400">Global user accounts management, system audit logs, and organization vulnerability metrics.</p>
          </div>

          <button
            type="button"
            onClick={fetchData}
            className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:bg-slate-800 transition shrink-0"
          >
            <RefreshCw size={14} className="text-cyan-400" />
            <span>Refresh Telemetry</span>
          </button>
        </div>

        {/* 4 Metric Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="glass rounded-2xl p-5 border-l-4 border-l-cyan-400">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Registered Users</span>
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-cyan-400/10 text-cyan-300">
                <Users size={18} />
              </div>
            </div>
            <p className="mt-3 text-3xl font-black text-white">{stats?.total_users || 0}</p>
            <p className="mt-1 text-xs text-emerald-400 font-semibold">{stats?.active_users || 0} Active Developers</p>
          </div>

          <div className="glass rounded-2xl p-5 border-l-4 border-l-blue-500">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Inspections</span>
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-blue-500/10 text-blue-300">
                <FileCode size={18} />
              </div>
            </div>
            <p className="mt-3 text-3xl font-black text-white">{stats?.total_analyses || 0}</p>
            <p className="mt-1 text-xs text-slate-400">Executed across platform</p>
          </div>

          <div className="glass rounded-2xl p-5 border-l-4 border-l-rose-500">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Security Threats</span>
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-rose-500/10 text-rose-300">
                <ShieldAlert size={18} />
              </div>
            </div>
            <p className="mt-3 text-3xl font-black text-rose-300">{stats?.total_findings || 0}</p>
            <p className="mt-1 text-xs text-rose-400 font-semibold">{stats?.severity_breakdown?.high || 0} High Critical Risks</p>
          </div>

          <div className="glass rounded-2xl p-5 border-l-4 border-l-emerald-400">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Average Health Score</span>
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-emerald-400/10 text-emerald-300">
                <ShieldCheck size={18} />
              </div>
            </div>
            <p className="mt-3 text-3xl font-black text-emerald-300">{stats?.average_health_score || 100}/100</p>
            <p className="mt-1 text-xs text-slate-400">Organization benchmark</p>
          </div>
        </div>

        {/* Global Threat Distribution Bar Section */}
        <div className="glass rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <BarChart3 size={18} className="text-cyan-400" />
            <span>Platform Vulnerability Threat Breakdown</span>
          </h3>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 pt-2">
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                <span>SQL Injection (SQLi)</span>
                <span className="font-bold text-rose-400">{threatDist.sql_injection || 0}</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-rose-500 rounded-full"
                  style={{ width: `${Math.min(100, ((threatDist.sql_injection || 0) / totalThreats) * 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                <span>Hardcoded Secrets & API Keys</span>
                <span className="font-bold text-amber-400">{threatDist.hardcoded_secrets || 0}</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-amber-500 rounded-full"
                  style={{ width: `${Math.min(100, ((threatDist.hardcoded_secrets || 0) / totalThreats) * 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
                <span>Command Execution Risks</span>
                <span className="font-bold text-indigo-400">{threatDist.command_injection || 0}</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-indigo-500 rounded-full"
                  style={{ width: `${Math.min(100, ((threatDist.command_injection || 0) / totalThreats) * 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* User Management Section */}
        <div className="glass rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Users size={18} className="text-indigo-400" />
              <span>User & Developer Account Management</span>
            </h3>
            <span className="text-xs text-slate-400">{users.length} Total Registered Accounts</span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-400 uppercase font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3.5">User</th>
                  <th className="p-3.5">Email</th>
                  <th className="p-3.5">Role</th>
                  <th className="p-3.5">Account Status</th>
                  <th className="p-3.5">Registered</th>
                  <th className="p-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {users.map((u) => (
                  <tr key={u.user_id} className="hover:bg-slate-900/50 transition">
                    <td className="p-3.5 font-bold text-white flex items-center gap-2">
                      <div className="grid h-7 w-7 place-items-center rounded-lg bg-slate-800 font-mono text-xs font-bold text-cyan-300">
                        {u.full_name?.charAt(0) || "U"}
                      </div>
                      <span>{u.full_name}</span>
                    </td>
                    <td className="p-3.5 font-mono text-slate-400">{u.email}</td>
                    <td className="p-3.5">
                      <span className={`px-2.5 py-1 rounded-md text-[10px] font-extrabold uppercase ${u.role === 'admin' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20'}`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold ${u.is_active ? 'bg-emerald-500/10 text-emerald-300' : 'bg-rose-500/10 text-rose-300'}`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${u.is_active ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                        {u.is_active ? "Active" : "Blocked"}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-400 font-mono">{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
                    <td className="p-3.5 text-right">
                      <button
                        type="button"
                        onClick={() => handleToggleUser(u.user_id)}
                        disabled={togglingId === u.user_id || u.role === "admin"}
                        className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold transition disabled:opacity-40 disabled:cursor-not-allowed ${u.is_active ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20 hover:bg-rose-500/20' : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 hover:bg-emerald-500/20'}`}
                      >
                        {u.is_active ? <UserX size={13} /> : <UserCheck size={13} />}
                        <span>{u.is_active ? "Block User" : "Activate"}</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Global Audit Logs */}
        <div className="glass rounded-2xl p-6 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Activity size={18} className="text-emerald-400" />
            <span>Global Inspection Audit Trail</span>
          </h3>

          <div className="overflow-x-auto rounded-xl border border-slate-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-400 uppercase font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3.5">Analysis ID</th>
                  <th className="p-3.5">Filename</th>
                  <th className="p-3.5">Language</th>
                  <th className="p-3.5">Flagged Issues</th>
                  <th className="p-3.5">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {(stats?.recent_audit_logs || []).map((log) => (
                  <tr key={log.analysis_id} className="hover:bg-slate-900/50 transition">
                    <td className="p-3.5 font-mono text-cyan-400">{log.analysis_id}</td>
                    <td className="p-3.5 font-bold text-white">{log.filename || "main.py"}</td>
                    <td className="p-3.5 font-mono uppercase text-slate-400">{log.language}</td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded bg-slate-800 font-bold text-slate-200">
                        {log.findings_count} findings
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-400">{log.created_at ? new Date(log.created_at).toLocaleString() : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
