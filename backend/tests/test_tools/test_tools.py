import pytest
from nightwatch.tools.remediation_tools import restart_service, rollback_deploy, scale_service
from nightwatch.knowledge.loader import runbook_loader
from nightwatch.schemas.diagnosis import DiagnosisReport, Evidence, Severity


def test_remediation_allowlist_enforcement():
    # Allowed service
    res = restart_service.entrypoint(service_name="sample-app")
    assert "approved and staged" in res.lower()

    # Blocked service outside allowlist
    blocked_res = restart_service.entrypoint(service_name="crypto-miner-pod")
    assert "SECURITY ERROR" in blocked_res


def test_scale_service_bounds():
    # Valid scale
    valid = scale_service.entrypoint(service_name="sample-app", replicas=3)
    assert "scaling to 3 replicas" in valid.lower()

    # Invalid bounds (> 10)
    invalid = scale_service.entrypoint(service_name="sample-app", replicas=999)
    assert "INVALID PARAMETER" in invalid


def test_runbook_loader_matching():
    matches = runbook_loader.search("High memory usage buffer leak", top_k=2)
    assert len(matches) > 0
    assert "high_memory_usage" in [m["name"] for m in matches]


def test_diagnosis_report_schema_normalization():
    # Test that 'critical' is automatically normalized to 'P1'
    report = DiagnosisReport(
        incident_id="INC-TEST-01",
        severity="critical",  # lowercase string alias
        suspected_cause="Memory leak in request buffer",
        evidence=[
            Evidence(source="prometheus_metric", content="RAM 95%", timestamp="2026-11-24T12:00:00Z", relevance=0.9)
        ],
        confidence=0.95,
        recommended_actions=["Restart container"],
    )
    assert report.severity == Severity.P1
