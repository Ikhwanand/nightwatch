import json 
from typing import Any, Dict, List, Optional
import psycopg
from nightwatch.config import get_settings


def get_db_connection_str() -> str:
    settings = get_settings()
    # Normalize connection string for psycopg3 (remove `+psycopg` if present)
    return settings.database_url.replace("postgresql+psycopg://", "postgresql://")

def init_db() -> None:
    """Initialize PostgreSQL tables for incidents and audit loogs."""
    conn_str = get_db_connection_str()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS incidents (
                        id SERIAL PRIMARY KEY,
                        incident_id VARCHAR(64) UNIQUE NOT NULL,
                        severity VARCHAR(10) NOT NULL,
                        status VARCHAR(32) NOT NULL DEFAULT 'investigated',
                        suspected_cause TEXT NOT NULL,
                        confidence FLOAT NOT NULL,
                        alerts JSONB NOT NULL,
                        diagnosis JSONB NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
                    CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents(created_at DESC);
                    -- Audit logs table for remediation tracking
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id SERIAL PRIMARY KEY,
                        incident_id VARCHAR(64) NOT NULL,
                        action_type VARCHAR(64) NOT NULL,
                        target VARCHAR(64) NOT NULL,
                        performed_by VARCHAR(64) NOT NULL,
                        status VARCHAR(32) NOT NULL,
                        details JSONB,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_audit_incident ON audit_logs(incident_id);
                    """
                )
            conn.commit()
            print("[NIGHTWATCH-DB] PostgreSQL tables (incidents & audit_logs) verified.")
    except Exception as exc:
        print(f"[NIGHTWATCH-DB] Database initialization warning (PostgreSQL might be starting up): {exc}")


def save_incident(
    incident_id: str,
    severity: str,
    status: str,
    suspected_cause: str,
    confidence: float,
    alerts: List[Dict[str, Any]],
    diagnosis: Dict[str, Any] | str,
) -> None:
    """Persists an investigated incident record into PostgreSQL"""
    conn_str = get_db_connection_str()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO incidents (
                        incident_id, severity, status, suspected_cause, confidence, alerts, diagnosis
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s) 
                    ON CONFLICT (incident_id) DO UPDATE
                    SET status = EXCLUDED.status, 
                        diagnosis = EXCLUDED.diagnosis;
                    """,
                    (
                        incident_id,
                        severity,
                        status,
                        suspected_cause,
                        confidence,
                        json.dumps(alerts),
                        json.dumps(diagnosis) if isinstance(diagnosis, dict) else json.dumps({"raw": diagnosis}),
                    ),
                )
            conn.commit()
        print(f"[NIGHTWATCH-DB] Incident {incident_id} saved to PostgreSQL.")
    except Exception as exc:
        print(f"[NIGHTWATCH-DB] Error saving incident to PostgreSQL: {exc}")
        
        
def update_incident_status(incident_id: str, new_status: str) -> bool:
    """Updates the status of an incident in PostgreSQL (e.g. 'remediated', 'approved', 'rejected')."""
    conn_str = get_db_connection_str()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE incidents 
                    SET status = %s 
                    WHERE incident_id = %s;
                    """,
                    (new_status, incident_id),
                )
            conn.commit()
        print(f"[NIGHTWATCH-DB] Incident {incident_id} status updated to '{new_status}'.")
        return True
    except Exception as exc:
        print(f"[NIGHTWATCH-DB] Error updating incident status: {exc}")
        return False


def delete_incident(incident_id: str) -> bool:
    """Deletes an incident record from PostgreSQL."""
    conn_str = get_db_connection_str()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM incidents 
                    WHERE incident_id = %s;
                    """,
                    (incident_id,),
                )
            conn.commit()
        print(f"[NIGHTWATCH-DB] Incident {incident_id} deleted from PostgreSQL.")
        return True
    except Exception as exc:
        print(f"[NIGHTWATCH-DB] Error deleting incident: {exc}")
        return False


def get_recent_incidents_from_db(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve recently recorded incidents from PostgreSQL"""
    conn_str = get_db_connection_str()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT incident_id, severity, status, suspected_cause, confidence, alerts, diagnosis, created_at 
                    FROM incidents
                    ORDER BY created_at DESC
                    LIMIT %s; 
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                results = []
                for row in rows:
                    results.append(
                        {
                            "incident_id": row[0],
                            "severity": row[1],
                            "status": row[2],
                            "suspected_cause": row[3],
                            "confidence": row[4],
                            "alerts": row[5] if isinstance(row[5], list) else json.loads(row[5]),
                            "diagnosis": row[6] if isinstance(row[6], dict) else json.loads(row[6]),
                            "created_at": str(row[7]),
                        }
                    )
                return results 
    except Exception as exc:
        print(f"[NIGHTWATCH-DB] Error querying incidents from PostgreSQL: {exc}")
        return []
    



def search_past_incidents_db(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Searches past incidents matching the query string in suspected_cause or incident_id."""
    conn_str = get_db_connection_str()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT incident_id, severity, suspected_cause, confidence, diagnosis, created_at 
                    FROM incidents
                    WHERE suspected_cause ILIKE %s OR incident_id ILIKE %s ORDER BY created_at DESC
                    LIMIT %s; 
                    """,
                    (f"%{query}%", f"%{query}%", limit),
                )
                rows = cur.fetchall()
                results = []
                for row in rows:
                    results.append(
                        {
                            "incident_id": row[0],
                            "severity": row[1],
                            "suspected_cause": row[2],
                            "confidence": row[3],
                            "diagnosis": row[4] if isinstance(row[4], dict) else json.loads(row[4]),
                            "created_at": str(row[5]),
                        }
                    )
                return results 
    except Exception as exc:
        print(f"[NIGHTWATCH-DB] Error searching past incidents: {exc}")
        return []


def record_audit_log(
    incident_id: str, 
    action_type: str, 
    target: str, 
    performed_by: str, 
    status: str,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Records an immutable audit log entry for any remediation action."""
    conn_str = get_db_connection_str()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_logs (incident_id, action_type, target, performed_by, status, details)
                    VALUES (%s, %s, %s, %s, %s, %s) 
                    """,
                    (
                        incident_id,
                        action_type,
                        target,
                        performed_by,
                        status,
                        json.dumps(details or {}),
                    ),
                )
            conn.commit()
            print(f"[NIGHTWATCH-AUDIT] Recorded action '{action_type}' for {incident_id} by {performed_by}.")
    except Exception as exc:
        print(f"[NIGHTWATCH-AUDIT] Failed to write audit log: {exc}")
    

def get_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetches recent audit log entries."""
    conn_str = get_db_connection_str()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, incident_id, action_type, target, performed_by, status, details, timestamp
                    FROM audit_logs
                    ORDER BY timestamp DESC
                    LIMIT %s; 
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                return [
                    {
                        "id": r[0],
                        "incident_id": r[1],
                        "action_type": r[2],
                        "target": r[3],
                        "performed_by": r[4],
                        "status": r[5],
                        "details": r[6] if isinstance(r[6], dict) else json.loads(r[6]),
                        "timestamp": str(r[7]),
                    }
                    for r in rows
                ]
    except Exception as exc:
        print(f"[NIGHTWATCH-AUDIT] Error fetching audit logs: {exc}")
        return []


def delete_audit_log(log_id: int) -> bool:
    """Deletes an audit log entry from PostgreSQL."""
    conn_str = get_db_connection_str()
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM audit_logs 
                    WHERE id = %s;
                    """,
                    (log_id,),
                )
            conn.commit()
        print(f"[NIGHTWATCH-AUDIT] Audit log ID {log_id} deleted from PostgreSQL.")
        return True
    except Exception as exc:
        print(f"[NIGHTWATCH-AUDIT] Error deleting audit log: {exc}")
        return False
