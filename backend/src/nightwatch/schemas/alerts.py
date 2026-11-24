from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from nightwatch.schemas.diagnosis import Severity


class AlertmanagerAlert(BaseModel):
    status: str
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    startsAt: Optional[str] = None
    endsAt: Optional[str] = None


class AlertmanagerPayload(BaseModel):
    version: str = "4"
    groupKey: Optional[str] = None
    status: str
    receiver: Optional[str] = None
    alerts: List[AlertmanagerAlert] = Field(default_factory=list)
    commonLabels: Dict[str, str] = Field(default_factory=dict)
    commonAnnotations: Dict[str, str] = Field(default_factory=dict)


class TriageResult(BaseModel):
    alert_name: str
    severity: Severity
    category: str = Field(..., description="Incident category: 'infra', 'database', 'application', or 'network'")
    summary: str
    is_duplicate: bool = False
 
    