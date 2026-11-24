from enum import Enum
from pydantic import BaseModel, Field 


class ActionType(str, Enum):
    restart = "restart"
    rollback = "rollback"
    scale = "scale"
    manual = "manual"
    
class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    

class RemediationAction(BaseModel):
    action_type: ActionType = Field(
        ...,
        description="Type of remediation action: restart, rollback, scale, or manual",
    )
    target: str = Field(
        ...,
        description="Target service, deployment, or contianer name (e.g., `sample-app`, `api-server`)",
    )
    justification: str = Field(
        ...,
        description="Clear rationale linking this remediation to the root cause identified in diagnosis",
    )
    risk_level: RiskLevel = Field(
        ...,
        description="Operational risk level of this action (low, medium, high)",
    )
    command_preview: str = Field(
        ...,
        description="The exact command or API call that would be executed (e.g., `docker restart sample-app`)",
    )
    approved: bool = Field(
        default=False,
        description="Approval state. Strictly requires human approval before execution.",
    )
    
    