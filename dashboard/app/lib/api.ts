import type {
  AuditLog,
  IncidentRecord,
  PendingApproval,
  SystemHealth,
} from "./types";

const API_BASE_URL = "http://localhost:7777";

export async function fetchHealth(): Promise<SystemHealth | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function fetchRecentIncidents(): Promise<IncidentRecord[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/alerts/recent`);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export async function fetchPendingApprovals(): Promise<PendingApproval[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/approvals/pending`);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export async function fetchAuditLogs(): Promise<AuditLog[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/approvals/audit-logs`);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export async function approveRemediation(
  incidentId: string,
  approver: string = "SRE On-Call",
  comments: string = "Approved via Mission Control Dashboard",
): Promise<any> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/approvals/${incidentId}/approve`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approver, comments }),
    },
  );
  if (!res.ok) throw new Error("Approval failed");
  return await res.json();
}

export async function rejectRemediation(
  incidentId: string,
  approver: string = "SRE On-Call",
  comments: string = "Rejected by operator",
): Promise<any> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/approvals/${incidentId}/reject`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approver, comments }),
    },
  );
  if (!res.ok) throw new Error("Rejection failed");
  return await res.json();
}

export async function deleteIncident(incidentId: string): Promise<boolean> {
  try {
    const res = await fetch(
      `${API_BASE_URL}/api/v1/alerts/incidents/${incidentId}`,
      {
        method: "DELETE",
      },
    );
    return res.ok;
  } catch {
    return false;
  }
}

export async function deleteAuditLog(logId: number): Promise<boolean> {
  try {
    const res = await fetch(
      `${API_BASE_URL}/api/v1/approvals/audit-logs/${logId}`,
      {
        method: "DELETE",
      },
    );
    return res.ok;
  } catch {
    return false;
  }
}


