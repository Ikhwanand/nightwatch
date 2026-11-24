import React, { useEffect, useState } from "react";
import {
  approveRemediation,
  deleteAuditLog,
  deleteIncident,
  fetchAuditLogs,
  fetchHealth,
  fetchPendingApprovals,
  fetchRecentIncidents,
  rejectRemediation,
} from "../lib/api";
import type {
  AuditLog,
  IncidentRecord,
  PendingApproval,
  SystemHealth,
} from "../lib/types";
import {
  ActivityIcon,
  AlertOctagonIcon,
  CheckCircleIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  RefreshIcon,
  ShieldIcon,
  TerminalIcon,
  TrashIcon,
} from "../components/Icons";

export function meta() {
  return [
    { title: "Nightwatch SRE | Autonomous Incident Commander" },
    {
      name: "description",
      content: "Autonomous Virtual SRE & Incident Response Dashboard",
    },
  ];
}

export default function DashboardHome() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [incidents, setIncidents] = useState<IncidentRecord[]>([]);
  const [pendingApprovals, setPendingApprovals] = useState<PendingApproval[]>(
    [],
  );
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [selectedIncident, setSelectedIncident] =
    useState<IncidentRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [incidentPage, setIncidentPage] = useState(1);
  const INCIDENTS_PER_PAGE = 5;

  const loadData = async () => {
    setLoading(true);
    const [h, incs, apprs, logs] = await Promise.all([
      fetchHealth(),
      fetchRecentIncidents(),
      fetchPendingApprovals(),
      fetchAuditLogs(),
    ]);
    setHealth(h);
    setIncidents(incs);
    setPendingApprovals(apprs);
    setAuditLogs(logs);

    if (incs.length > 0 && !selectedIncident) {
      setSelectedIncident(incs[0]);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 6000); // Poll every 6 seconds
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (incidentId: string) => {
    try {
      await approveRemediation(incidentId, "SRE Lead");
      setActionMessage(`Remediation executed for ${incidentId}`);
      setTimeout(() => setActionMessage(null), 4000);
      await loadData();
    } catch {
      alert("Failed to approve remediation.");
    }
  };

  const handleReject = async (incidentId: string) => {
    try {
      await rejectRemediation(incidentId, "SRE Lead");
      setActionMessage(`Remediation rejected for ${incidentId}`);
      setTimeout(() => setActionMessage(null), 4000);
      await loadData();
    } catch {
      alert("Failed to reject remediation.");
    }
  };

  const handleDeleteIncident = async (
    e: React.MouseEvent,
    incidentId: string,
  ) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to delete incident ${incidentId}?`)) {
      return;
    }
    try {
      const ok = await deleteIncident(incidentId);
      if (ok) {
        setActionMessage(`Incident ${incidentId} removed from stream`);
        setTimeout(() => setActionMessage(null), 3000);
        if (selectedIncident?.incident_id === incidentId) {
          setSelectedIncident(null);
        }
        await loadData();
      } else {
        alert("Failed to delete incident.");
      }
    } catch {
      alert("Error deleting incident.");
    }
  };

  const handleDeleteAuditLog = async (
    e: React.MouseEvent,
    logId: number,
  ) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to delete audit log #${logId}?`)) {
      return;
    }
    try {
      const ok = await deleteAuditLog(logId);
      if (ok) {
        setActionMessage(`Audit log #${logId} deleted successfully.`);
        setTimeout(() => setActionMessage(null), 3000);
        await loadData();
      } else {
        alert("Failed to delete audit log.");
      }
    } catch {
      alert("Error deleting audit log.");
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case "P1":
        return "bg-red-500/10 text-red-400 border border-red-500/30";
      case "P2":
        return "bg-amber-500/10 text-amber-400 border border-amber-500/30";
      case "P3":
        return "bg-yellow-500/10 text-yellow-400 border border-yellow-500/30";
      default:
        return "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30";
    }
  };

  const diagnosis = selectedIncident?.diagnosis as any;

  const totalIncidentPages =
    Math.ceil(incidents.length / INCIDENTS_PER_PAGE) || 1;
  const activePage = Math.min(incidentPage, totalIncidentPages);
  const paginatedIncidents = incidents.slice(
    (activePage - 1) * INCIDENTS_PER_PAGE,
    activePage * INCIDENTS_PER_PAGE,
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-4 md:p-8">
      {/* Header Bar */}
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 mb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg border border-indigo-500/30">
              <ShieldIcon className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                NIGHTWATCH{" "}
                <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-mono">
                  v0.1.0
                </span>
              </h1>
              <p className="text-xs md:text-sm text-slate-400">
                Autonomous SRE Multi-Agent Telemetry & Incident Commander
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-900 border border-slate-800 text-xs font-mono">
            <span
              className={`w-2 h-2 rounded-full ${health ? "bg-emerald-400 animate-pulse" : "bg-red-400"}`}
            />
            {health ? "AGENTS ONLINE" : "CONNECTING..."}
          </div>
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 rounded-md bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 transition-colors"
            title="Refresh Data"
          >
            <RefreshIcon
              className={`w-4 h-4 ${loading ? "animate-spin text-indigo-400" : ""}`}
            />
          </button>
        </div>
      </header>

      {actionMessage && (
        <div className="mb-6 p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm rounded-md flex items-center gap-2">
          <CheckCircleIcon className="w-4 h-4" />
          {actionMessage}
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800/80">
          <div className="text-xs text-slate-400 font-medium">
            TOTAL INCIDENTS
          </div>
          <div className="text-2xl font-bold text-white mt-1">
            {incidents.length}
          </div>
          <div className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
            <ActivityIcon className="w-3 h-3" /> Scanned by Prometheus
          </div>
        </div>

        <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800/80">
          <div className="text-xs text-slate-400 font-medium">
            PENDING APPROVALS
          </div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {pendingApprovals.length}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            Human-in-the-Loop Gate
          </div>
        </div>

        <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800/80">
          <div className="text-xs text-slate-400 font-medium">ACTIVE MODEL</div>
          <div className="text-sm font-mono text-indigo-300 truncate mt-1">
            {health?.default_model || "oc/mimo-v2.6-flash-free"}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            Agno Multi-Agent Team
          </div>
        </div>

        <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800/80">
          <div className="text-xs text-slate-400 font-medium">
            SECURITY GUARDRAILS
          </div>
          <div className="text-sm font-semibold text-emerald-400 mt-1">
            Active & Enforcing
          </div>
          <div className="text-xs text-slate-400 mt-1">
            Allowlist & Credential Masking
          </div>
        </div>
      </div>

      {/* Main Grid: Feed & Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Live Incident Feed (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-2">
              <AlertOctagonIcon className="w-4 h-4 text-indigo-400" /> Live
              Incident Stream
            </h2>
            <span className="text-xs text-slate-500 font-mono">
              {incidents.length} recorded
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[750px] pr-1">
            {incidents.length === 0 ? (
              <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800 text-slate-400 text-sm">
                No incidents recorded yet. Trigger a fault injection from
                terminal to see live telemetry.
              </div>
            ) : (
              paginatedIncidents.map((inc) => (
                <div
                  key={inc.incident_id}
                  onClick={() => setSelectedIncident(inc)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    selectedIncident?.incident_id === inc.incident_id
                      ? "bg-indigo-950/30 border-indigo-500/50 shadow-lg shadow-indigo-950/50"
                      : "bg-slate-900/40 hover:bg-slate-900/80 border-slate-800/80"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-indigo-300 font-bold">
                        {inc.incident_id}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${getSeverityBadge(inc.severity)}`}
                      >
                        {inc.severity || "P2"}
                      </span>
                    </div>
                    <button
                      onClick={(e) => handleDeleteIncident(e, inc.incident_id)}
                      title={`Delete ${inc.incident_id}`}
                      className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                    >
                      <TrashIcon className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div className="text-sm font-semibold text-slate-200 mt-2 line-clamp-2">
                    {inc.suspected_cause ||
                      inc.diagnosis?.suspected_cause ||
                      "Autonomous investigation active..."}
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 mt-3 pt-2 border-t border-slate-800/60 font-mono">
                    <span>Target: sample-app</span>
                    <span>{inc.status || "investigated"}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination Controls */}
          {incidents.length > INCIDENTS_PER_PAGE && (
            <div className="flex items-center justify-between pt-3 px-1 border-t border-slate-800/80 text-xs text-slate-400 font-mono">
              <span>
                {(activePage - 1) * INCIDENTS_PER_PAGE + 1}–
                {Math.min(activePage * INCIDENTS_PER_PAGE, incidents.length)} of{" "}
                {incidents.length}
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setIncidentPage((p) => Math.max(1, p - 1))}
                  disabled={activePage === 1}
                  className="p-1 rounded bg-slate-900 border border-slate-800 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-800 text-slate-300 transition-colors"
                  title="Previous page"
                >
                  <ChevronLeftIcon className="w-3.5 h-3.5" />
                </button>
                {Array.from({ length: totalIncidentPages }, (_, i) => i + 1).map(
                  (num) => (
                    <button
                      key={num}
                      onClick={() => setIncidentPage(num)}
                      className={`w-6 h-6 rounded text-xs flex items-center justify-center font-semibold transition-colors ${
                        num === activePage
                          ? "bg-indigo-600 text-white"
                          : "bg-slate-900 border border-slate-800 text-slate-400 hover:bg-slate-800"
                      }`}
                    >
                      {num}
                    </button>
                  ),
                )}
                <button
                  onClick={() =>
                    setIncidentPage((p) => Math.min(totalIncidentPages, p + 1))
                  }
                  disabled={activePage >= totalIncidentPages}
                  className="p-1 rounded bg-slate-900 border border-slate-800 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-800 text-slate-300 transition-colors"
                  title="Next page"
                >
                  <ChevronRightIcon className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Deep Investigation & Approvals (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Detailed Diagnosis View */}
          <div className="p-6 bg-slate-900/60 rounded-xl border border-slate-800/90 shadow-xl">
            <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-2 mb-4">
              <TerminalIcon className="w-4 h-4 text-emerald-400" /> SRE Incident
              Diagnosis
            </h2>

            {selectedIncident ? (
              <div className="space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-slate-800">
                  <div>
                    <span className="font-mono text-base font-bold text-white">
                      {selectedIncident.incident_id}
                    </span>
                    <div className="text-xs text-slate-400 mt-0.5">
                      Status: {selectedIncident.status}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-bold px-2.5 py-1 rounded-md ${getSeverityBadge(selectedIncident.severity)}`}
                    >
                      SEVERITY: {selectedIncident.severity}
                    </span>
                    {diagnosis?.confidence && (
                      <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                        Confidence: {(diagnosis.confidence * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>

                {/* Root Cause */}
                <div>
                  <div className="text-xs font-mono text-slate-400 uppercase">
                    Suspected Root Cause
                  </div>
                  <div className="text-sm font-medium text-slate-200 mt-1 p-3 rounded-lg bg-slate-950 border border-slate-800/80">
                    {selectedIncident.suspected_cause ||
                      diagnosis?.suspected_cause ||
                      "Awaiting multi-agent synthesis..."}
                  </div>
                </div>

                {/* Evidence Traces */}
                {diagnosis?.evidence && diagnosis.evidence.length > 0 && (
                  <div>
                    <div className="text-xs font-mono text-slate-400 uppercase mb-2">
                      Evidence Corroboration
                    </div>
                    <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                      {diagnosis.evidence.map((ev: any, idx: number) => (
                        <div
                          key={idx}
                          className="p-2.5 bg-slate-950 rounded border border-slate-800/60 text-xs font-mono"
                        >
                          <div className="flex items-center justify-between text-indigo-400 mb-1">
                            <span>[{ev.source}]</span>
                            <span className="text-[10px] text-slate-500">
                              Relevance: {(ev.relevance * 100).toFixed(0)}%
                            </span>
                          </div>
                          <div className="text-slate-300 break-words">
                            {ev.content}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommended Mitigation */}
                {diagnosis?.recommended_actions && (
                  <div>
                    <div className="text-xs font-mono text-slate-400 uppercase mb-2">
                      SOP Runbook Mitigations
                    </div>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {diagnosis.recommended_actions.map(
                        (act: string, idx: number) => (
                          <li
                            key={idx}
                            className="p-2 bg-indigo-950/20 rounded border border-indigo-900/30 flex items-start gap-2"
                          >
                            <span className="text-indigo-400 font-bold">•</span>
                            <span>{act}</span>
                          </li>
                        ),
                      )}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 text-sm">
                Select an incident from the stream to view full agent analysis.
              </div>
            )}
          </div>

          {/* Pending Human Approvals */}
          <div className="p-6 bg-slate-900/60 rounded-xl border border-slate-800/90 shadow-xl">
            <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-2 mb-4">
              <ShieldIcon className="w-4 h-4 text-amber-400" /> Staged Human
              Approvals (HITL)
            </h2>

            {pendingApprovals.length === 0 ? (
              <div className="text-xs text-slate-500 p-4 bg-slate-950/40 rounded-lg border border-slate-800 text-center">
                No remediation actions currently awaiting approval.
              </div>
            ) : (
              <div className="space-y-3">
                {pendingApprovals.map((appr) => (
                  <div
                    key={appr.incident_id}
                    className="p-4 bg-slate-950 rounded-lg border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-indigo-400 font-bold">
                          {appr.incident_id}
                        </span>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${getSeverityBadge(appr.severity)}`}
                        >
                          {appr.severity}
                        </span>
                      </div>
                      <div className="text-xs text-slate-300 font-mono">
                        Action: {appr.staged_action}
                      </div>
                      <div className="text-[11px] text-slate-500">
                        {appr.suspected_cause}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 w-full md:w-auto">
                      <button
                        onClick={() => handleApprove(appr.incident_id)}
                        className="flex-1 md:flex-none px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold transition-colors"
                      >
                        Approve & Execute
                      </button>
                      <button
                        onClick={() => handleReject(appr.incident_id)}
                        className="flex-1 md:flex-none px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs transition-colors"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* PostgreSQL Audit Log Trail */}
          <div className="p-6 bg-slate-900/60 rounded-xl border border-slate-800/90 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-2">
                <CheckCircleIcon className="w-4 h-4 text-indigo-400" /> Immutable
                PostgreSQL Audit Trail
              </h2>
              <span className="text-xs text-slate-500 font-mono">
                {auditLogs.length} events logged
              </span>
            </div>

            <div className="overflow-x-auto max-h-[320px] overflow-y-auto rounded-lg border border-slate-800/80 scrollbar-thin scrollbar-thumb-slate-800">
              <table className="w-full text-left text-xs font-mono relative">
                <thead className="sticky top-0 bg-slate-900 border-b border-slate-800 z-10 shadow-sm">
                  <tr className="text-slate-400 font-semibold">
                    <th className="py-2.5 px-3">INCIDENT</th>
                    <th className="py-2.5 px-3">ACTION</th>
                    <th className="py-2.5 px-3">TARGET</th>
                    <th className="py-2.5 px-3">OPERATOR</th>
                    <th className="py-2.5 px-3">STATUS</th>
                    <th className="py-2.5 px-3">TIMESTAMP</th>
                    <th className="py-2.5 px-3 text-right">ACTION</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40 text-slate-300">
                  {auditLogs.length === 0 ? (
                    <tr>
                      <td
                        colSpan={7}
                        className="py-6 text-center text-slate-500"
                      >
                        No audit actions recorded yet.
                      </td>
                    </tr>
                  ) : (
                    auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-2.5 px-3 text-indigo-300 font-bold">
                          {log.incident_id}
                        </td>
                        <td className="py-2.5 px-3 text-slate-200">
                          {log.action_type}
                        </td>
                        <td className="py-2.5 px-3 text-slate-400">
                          {log.target || "sample-app"}
                        </td>
                        <td className="py-2.5 px-3 text-slate-400">
                          {log.performed_by}
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${
                              log.status === "executed"
                                ? "text-emerald-400 bg-emerald-500/10 border border-emerald-500/30"
                                : log.status === "rejected"
                                  ? "text-red-400 bg-red-500/10 border border-red-500/30"
                                  : "text-amber-400 bg-amber-500/10 border border-amber-500/30"
                            }`}
                          >
                            {log.status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-[10px] text-slate-500">
                          {log.timestamp.slice(0, 19)}
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <button
                            onClick={(e) => handleDeleteAuditLog(e, log.id)}
                            title={`Delete audit log #${log.id}`}
                            className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors inline-flex items-center justify-center"
                          >
                            <TrashIcon className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
