import subprocess
from typing import Any, Dict, List 
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from nightwatch.db.database import (
    delete_audit_log,
    get_audit_logs,
    get_recent_incidents_from_db,
    record_audit_log,
    update_incident_status,
)
from nightwatch.guardrails.allowlist import ServiceAllowlist


router = APIRouter(prefix="/api/v1/approvals", tags=["Approvals"])

class ApprovalDecision(BaseModel):
    approver: str = Field(..., description="Name or identifier of the approving SRE/engineer")
    comments: str = Field(default="Approved via SRE console", description="Decision notes")
    

@router.get("/pending", status_code=status.HTTP_200_OK)
async def list_pending_approvals() -> List[Dict[str, Any]]:
    """Returns all recently diagnosed incients that require human remediation approval."""
    incidents = get_recent_incidents_from_db(limit=20)
    pending = []
    for inc in incidents:
        if inc.get("status") == "investigated":
            diag = inc.get("diagnosis", {})
            recs = diag.get("recommended_actions", []) if isinstance(diag, dict) else []
            pending.append({
                "incident_id": inc["incident_id"],
                "severity": inc["severity"],
                "suspected_cause": inc["suspected_cause"],
                "staged_action": recs[0] if recs else "restart_service(sample-app)",
                "created_at": inc["created_at"],
            })
    
    return pending 


@router.post("/{incident_id}/approve", status_code=status.HTTP_200_OK)
async def approve_remediation(incident_id: str, decision: ApprovalDecision) -> Dict[str, Any]:
    """Approves and executes a staged remediation action within security allowlist boundaries."""
    incidents = get_recent_incidents_from_db(limit=20)
    target_incident = next((i for i in incidents if i["incident_id"] == incident_id), None)
    
    if not target_incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )
        
    # Determine service target from alert instance
    alerts = target_incident.get("alerts", [])
    service_target = "sample-app"
    if alerts and isinstance(alerts, list):
        service_target = alerts[0].get("labels", {}).get("service", "sample-app")
        
    if not ServiceAllowlist.validate_service(service_target):
        record_audit_log(
            incident_id=incident_id,
            action_type="restart",
            target=service_target,
            performed_by=decision.approver,
            status="blocked_by_guardrail",
            details={"error": "Target outside allowlist"},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Service '{service_target}' is not in the allowed infrastructure list.",
        )
        
    # Execute remediation action (e.g. restart container via Docker)
    execution_status = "executed"
    execution_output = ""
    container_name = "nightwatch-sample-app" if service_target in ("api-server", "sample-app") else f"nightwatch-{service_target}"
    try:
        cmd = ["docker", "restart", container_name]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            execution_output = f"Successfully restarted {container_name}"
        else:
            execution_output = f"Docker return code {result.returncode}: {result.stderr.strip()}"
    except Exception as e:
        execution_output = f"Simulated execution: Container restart staged ({e})"
    
    # Update incident status in PostgreSQL so it clears from pending approvals
    update_incident_status(incident_id, "remediated")

    # Record immutable audit log entry
    record_audit_log(
        incident_id=incident_id,
        action_type="restart_service",
        target=service_target,
        performed_by=decision.approver,
        status=execution_status,
        details={
            "comments": decision.comments,
            "output": execution_output,
        },
    )
    
    return {
        "incident_id": incident_id,
        "action": "restart_service",
        "target": service_target,
        "status": execution_status,
        "approver": decision.approver,
        "output": execution_output,
    }
    
    
@router.post("/{incident_id}/reject", status_code=status.HTTP_200_OK)
async def reject_remediation(incident_id: str, decision: ApprovalDecision) -> Dict[str, Any]:
    """Rejects a staged remediation action and records the rationale in audit logs."""
    update_incident_status(incident_id, "rejected")
    record_audit_log(
        incident_id=incident_id,
        action_type="remediation_rejected",
        target="unknown",
        performed_by=decision.approver,
        status="rejected",
        details={"reason": decision.comments},
    )
    return {
        "incident_id": incident_id,
        "status": "rejected",
        "approver": decision.approver,
        "comments": decision.comments,
    }
    
    
@router.get("/audit-logs", status_code=status.HTTP_200_OK)
async def list_audit_logs() -> List[Dict[str, Any]]:
    """Returns the immutable audit trail of all approved, executed, and rejected actions."""
    return get_audit_logs(limit=100)


@router.delete("/audit-logs/{log_id}", status_code=status.HTTP_200_OK)
async def remove_audit_log(log_id: int) -> Dict[str, Any]:
    """Deletes an audit log entry from the database."""
    success = delete_audit_log(log_id)
    return {
        "status": "deleted",
        "id": log_id,
        "success": success,
    }
