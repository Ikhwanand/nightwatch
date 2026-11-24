import uuid
from typing import Any, Dict, List
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from nightwatch.agents.leader import incident_team
from nightwatch.db.database import (
    delete_incident,
    get_recent_incidents_from_db,
    init_db,
    save_incident,
)
from nightwatch.notifications.telegram import notification_service
from nightwatch.schemas.alerts import AlertmanagerPayload, AlertmanagerAlert
from nightwatch.schemas.diagnosis import DiagnosisReport

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])

# Initialize DB tables on startup
init_db()

# In-memory store for recent incidents (persisted to PostgreSQL in Phase 3)
recent_incidents: List[Dict[str, Any]] = []


def _run_investigator(
    incident_id: str,
    firing_alerts: List[AlertmanagerAlert],
    prompt: str,
) -> None:
    """Background worker that runs the multi-agent investigation without blocking HTTP responses."""
    try:
        response = incident_team.run(prompt)
        report = response.content if hasattr(response, "content") else response
        
        severity = "P2"
        suspected_cause = "Under investigation"
        confidence = 0.8
        diagnosis_dict: Dict[str, Any] = {}
        
        if isinstance(report, DiagnosisReport):
            diagnosis_dict = report.model_dump()
            severity = report.severity.value 
            suspected_cause = report.suspected_cause
            confidence = report.confidence
        elif isinstance(report, dict):
            diagnosis_dict = report 
            severity = report.get("severity", "P2")
            suspected_cause = report.get("suspected_cause", "Automated incident diagnosis")
            confidence = float(report.get("confidence", 0.8))
        else:
            diagnosis_dict = {"raw_report": str(report)}
            suspected_cause = str(report)[:200]
        
        incident_record = {
            "incident_id": incident_id,
            "severity": severity,
            "status": "investigated",
            "alerts": [a.model_dump() for a in firing_alerts],
            "diagnosis": diagnosis_dict,
        }
        recent_incidents.append(incident_record)
        
        # Persist to PostgreSQL database
        save_incident(
            incident_id=incident_id,
            severity=severity,
            status="investigated",
            suspected_cause=suspected_cause,
            confidence=confidence,
            alerts=[a.model_dump() for a in firing_alerts],
            diagnosis=diagnosis_dict,
        )
        
        # Dispatch alert notification to Telegram
        recs = diagnosis_dict.get("recommended_actions", [])
        rec_action = recs[0] if recs else "Investigate container metrics & restart if necessary"
        target_svc = "sample-app"
        if firing_alerts and hasattr(firing_alerts[0], "labels") and firing_alerts[0].labels:
            target_svc = firing_alerts[0].labels.get("service", "sample-app")

        notification_service.send_incident_alert(
            incident_id=incident_id,
            severity=severity,
            cause=suspected_cause,
            recommended_action=rec_action,
            target_service=target_svc,
        )

        print(f"[NIGHTWATCH] Investigation completed for incident {incident_id}")
    
    except Exception as exc:
        incident_record = {
            "incident_id": incident_id,
            "status": "failed",
            "alerts": [a.model_dump() for a in firing_alerts],
            "error": str(exc),
        }
        recent_incidents.append(incident_record)
        print(f"[NIGHTWATCH] Investigation failed for {incident_id}: {exc}")


@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def receive_alertmanager_webhook(payload: AlertmanagerPayload, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Receives webhook notifications from Prometheus Alertmanager and dispatches SRE investigation asynchronously."""
    if not payload.alerts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload contains no alerts.",
        )
        
    firing_alerts = [a for a in payload.alerts if a.status == "firing"]
    if not firing_alerts:
        return {"status": "ignored", "message": "No firing alerts found in payload."}
    
    # Format incoming alert details for the Incident Commander
    alert_summaries = []
    for alert in firing_alerts:
        name = alert.labels.get("alertname", "UnknownAlert")
        severity = alert.labels.get("severity", "warning")
        instance = alert.labels.get("instance", alert.labels.get("job", "unknown-target"))
        desc = alert.annotations.get("description", alert.annotations.get("summary", "No description provided"))
        alert_summaries.append(f"- Alert: {name} | Severity: {severity} | Target: {instance} | Details: {desc}")
        
    
    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    prompt = (
        f"Incident Alert Received [{incident_id}]:\n"
        + "\n".join(alert_summaries)
        + "\n\nPlease triage this incident, consult SRE runbooks and past incidents, investigate logs and metrics, and produce a verified DiagnosisRport."
    )
    
    # Launch investigation in background thread so Alertmanager gets instant HTTP 202
    background_tasks.add_task(_run_investigator, incident_id, firing_alerts, prompt)
    
    return {
        "status": "accepted",
        "incident_id": incident_id,
        "message": "Incident investigation dispatched to Nightwatch Agent Team in background.",
    }
        
    
@router.get("/recent")
async def get_recent_incidents() -> List[Dict[str, Any]]:
    """Returns the list of recently investigated incidents from PostgreSQL (or memory fallback)."""
    db_records = get_recent_incidents_from_db(limit=100)
    if db_records:
        return db_records
    return recent_incidents[-100:]


@router.delete("/incidents/{incident_id}", status_code=status.HTTP_200_OK)
async def remove_incident(incident_id: str) -> Dict[str, Any]:
    """Deletes an incident from the database and in-memory recent cache."""
    global recent_incidents
    recent_incidents = [inc for inc in recent_incidents if inc.get("incident_id") != incident_id]
    success = delete_incident(incident_id)
    return {
        "status": "deleted",
        "incident_id": incident_id,
        "success": success,
    }
