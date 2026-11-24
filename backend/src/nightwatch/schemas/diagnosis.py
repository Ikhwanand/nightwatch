from enum import Enum
from typing import List, Any
from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    P1 = "P1"  # Critical - Total downtime or data loss
    P2 = "P2"  # High - Significant performance degradation
    P3 = "P3"  # Medium - Warning or partial service disruption
    P4 = "P4"  # Low - Minor anomaly or informational


class Evidence(BaseModel):
    source: str = Field(..., description="Evidence source: 'loki_log', 'prometheus_metric', or 'deploy_history'")
    content: str = Field(..., description="Log snippet, quantitative metric value, or commit hash")
    timestamp: str = Field(..., description="Timestamp of the evidence (ISO format or time offset)")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance score of evidence to the incident (0.0 - 1.0)")


class DiagnosisReport(BaseModel):
    incident_id: str = Field(..., description="Unique incident identifier")
    severity: Severity = Field(..., description="Assessed severity level from investigation")
    suspected_cause: str = Field(..., description="A concise sentence explaining the root cause (e.g., 'Memory leak in api-server causing RAM exhaustion'), NOT just a severity label.")
    evidence: List[Evidence] = Field(..., min_length=1, description="List of concrete evidence supporting the conclusion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Agent confidence score in this diagnosis (0.0 - 1.0)")
    recommended_actions: List[str] = Field(..., description="List of recommended remediation actions")
    similar_past_incidents: List[str] = Field(
        default_factory=list,
        description="References to matching past incidents or SOP runbooks",
    )
    requires_human_action: bool = Field(True, description="Whether remediation requires human confirmation")
    
    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v: Any) -> str:
        """Automatically maps common Prometheus strings to P1-P4 enums."""
        if isinstance(v, str):
            val = v.upper()
            if "CRITICAL"  in val or val == "P1":
                return "P1"
            if "HIGH" in val or val == "P2":
                return "P2"
            if "WARN" in val or "MEDIUM" in val or val == "P3":
                return "P3"
            if "LOW" in val or "INFO" in val or val == "P4":
                return "P4"
        
        return v 

    