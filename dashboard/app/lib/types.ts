export type Severity = "P1" | "P2" | "P3" | "P4";

export interface Evidence {
  source: string;
  content: string;
  timestamp: string;
  relevance: number;
}

export interface DiagnosisReport {
  incident_id: string;
  severity: Severity;
  suspected_cause: string;
  confidence: number;
  evidence: Evidence[];
  recommended_actions: string[];
  similar_past_incidents?: string[];
  requires_human_action: boolean;
}

export interface IncidentRecord {
  incident_id: string;
  severity: Severity;
  status: "firing" | "investigated" | "mitigated" | "failed";
  suspected_cause?: string;
  confidence?: number;
  alerts?: Array<{
    status: string;
    labels: Record<string, string>;
    annotations: Record<string, string>;
  }>;
  diagnosis?: DiagnosisReport | Record<string, any>;
  created_at?: string;
}

export interface PendingApproval {
  incident_id: string;
  severity: Severity;
  suspected_cause: string;
  staged_action: string;
  created_at: string;
}

export interface AuditLog {
  id: number;
  incident_id: string;
  action_type: string;
  target: string;
  performed_by: string;
  status: string;
  details: Record<string, any>;
  timestamp: string;
}

export interface SystemHealth {
  status: string;
  app_env: string;
  default_model: string;
  prometheus_url: string;
  loki_url: string;
  database_url: string;
}
