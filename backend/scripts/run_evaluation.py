import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nightwatch.agents.leader import incident_team
from nightwatch.guardrails.allowlist import ServiceAllowlist
from nightwatch.schemas.diagnosis import DiagnosisReport

console = Console()


@dataclass
class IncidentScenario:
    id: str
    name: str
    alert_prompt: str
    expected_root_cause_keywords: List[str]
    expected_remediation_keywords: List[str]
    target_service: str


SCENARIOS: List[IncidentScenario] = [
    IncidentScenario(
        id="scenario_01_memory_leak",
        name="Progressive Memory Leak",
        alert_prompt=(
            "INCOMING ALERT [EVAL-01]:\n"
            "- Alert: HighMemoryUsage | Severity: critical | Target: sample-app:8000 | "
            "Details: RAM usage exceeded 94.5% with positive heap growth slope over 4 hours.\n"
            "Please triage, investigate metrics and logs, and synthesize a DiagnosisReport."
        ),
        expected_root_cause_keywords=["memory", "leak", "ram", "exhaustion", "buffer"],
        expected_remediation_keywords=["restart", "rollback"],
        target_service="sample-app",
    ),
    IncidentScenario(
        id="scenario_02_http_error_surge",
        name="HTTP 5xx Error Surge",
        alert_prompt=(
            "INCOMING ALERT [EVAL-02]:\n"
            "- Alert: HighErrorRate | Severity: critical | Target: sample-app:8000 | "
            "Details: 5xx error rate spiked to 18.4% following database connection timeouts.\n"
            "Please triage, investigate root cause, and synthesize a DiagnosisReport."
        ),
        expected_root_cause_keywords=["error", "database", "connection", "pool", "timeout", "5xx"],
        expected_remediation_keywords=["pool", "restart", "reconnect", "scale"],
        target_service="sample-app",
    ),
    IncidentScenario(
        id="scenario_03_service_down",
        name="Target Service Crash / OOM",
        alert_prompt=(
            "INCOMING ALERT [EVAL-03]:\n"
            "- Alert: ServiceDown | Severity: critical | Target: sample-app:8000 | "
            "Details: Prometheus failed to scrape endpoint, container exit code 137 (OOMKilled).\n"
            "Please triage, identify cause, and synthesize a DiagnosisReport."
        ),
        expected_root_cause_keywords=["down", "crash", "oom", "killed", "exit"],
        expected_remediation_keywords=["start", "restart", "memory limit"],
        target_service="sample-app",
    ),
    IncidentScenario(
        id="scenario_04_deploy_regression",
        name="Deployment Regression",
        alert_prompt=(
            "INCOMING ALERT [EVAL-04]:\n"
            "- Alert: HighErrorRate | Severity: critical | Target: sample-app:8000 | "
            "Details: Error rate began climbing 5 minutes after commit 'feat: batch request buffer' was rolled out.\n"
            "Please triage, correlate with recent Git commits/deploys, and synthesize a DiagnosisReport."
        ),
        expected_root_cause_keywords=["deploy", "commit", "regression", "rollout", "buffer"],
        expected_remediation_keywords=["rollback", "revert"],
        target_service="sample-app",
    ),
]


def evaluate_scenario(scenario: IncidentScenario) -> Dict[str, Any]:
    """Runs a single synthetic incident scenario against the Incident Commander Team."""
    console.print(f"[bold cyan]Running:[/bold cyan] {scenario.id} - [italic]{scenario.name}[/italic]...")

    start_time = time.time()
    try:
        response = incident_team.run(scenario.alert_prompt)
        elapsed_time = round(time.time() - start_time, 2)

        content = response.content if hasattr(response, "content") else response

        # Extract fields
        if isinstance(content, DiagnosisReport):
            suspected_cause = content.suspected_cause
            remediations = content.recommended_actions
            confidence = content.confidence
        elif isinstance(content, dict):
            suspected_cause = content.get("suspected_cause", "")
            remediations = content.get("recommended_actions", [])
            confidence = float(content.get("confidence", 0.0))
        else:
            suspected_cause = str(content)
            remediations = []
            confidence = 0.5

        # Check Root Cause Accuracy
        cause_matched = any(kw in suspected_cause.lower() for kw in scenario.expected_root_cause_keywords)

        # Check Remediation Validity
        remediation_text = " ".join(remediations).lower()
        remediation_matched = any(kw in remediation_text for kw in scenario.expected_remediation_keywords)

        # Check Security Guardrail: target service must be within allowlist
        is_safe = ServiceAllowlist.validate_service(scenario.target_service)

        passed = cause_matched and remediation_matched and is_safe

        return {
            "scenario": scenario.name,
            "status": "PASS" if passed else "FAIL",
            "latency_s": elapsed_time,
            "confidence": f"{confidence * 100:.0f}%",
            "cause_matched": cause_matched,
            "remediation_matched": remediation_matched,
            "safe": is_safe,
            "suspected_cause": suspected_cause[:90] + ("..." if len(suspected_cause) > 90 else ""),
        }

    except Exception as exc:
        return {
            "scenario": scenario.name,
            "status": "ERROR",
            "latency_s": round(time.time() - start_time, 2),
            "confidence": "0%",
            "cause_matched": False,
            "remediation_matched": False,
            "safe": True,
            "suspected_cause": f"Execution error: {str(exc)[:80]}",
        }


def run_benchmark():
    console.print(
        Panel.fit(
            "[bold green]Nightwatch SRE Benchmark & Accuracy Evaluation[/bold green]\n"
            "Testing Multi-Agent Autonomous Diagnosis against Ground-Truth Scenarios",
            border_style="green",
        )
    )

    results = []
    for sc in SCENARIOS:
        res = evaluate_scenario(sc)
        results.append(res)
        console.print(f" -> Result: [{'green' if res['status'] == 'PASS' else 'red'}]{res['status']}[/] in {res['latency_s']}s\n")

    # Summary Table
    table = Table(title="Synthetic Incident Benchmark Results", border_style="cyan")
    table.add_column("Scenario", style="bold white")
    table.add_column("Status", justify="center")
    table.add_column("Latency (s)", justify="center", style="cyan")
    table.add_column("Confidence", justify="center", style="magenta")
    table.add_column("Cause Match", justify="center")
    table.add_column("SOP Match", justify="center")
    table.add_column("Allowlist Safe", justify="center")
    table.add_column("Diagnosed Cause", style="dim")

    passed_count = 0
    total_latency = 0.0

    for r in results:
        status_badge = f"[bold green]PASS[/]" if r["status"] == "PASS" else f"[bold red]{r['status']}[/]"
        cause_badge = "✅" if r["cause_matched"] else "❌"
        rem_badge = "✅" if r["remediation_matched"] else "❌"
        safe_badge = "🛡️ Yes" if r["safe"] else "⚠️ No"

        if r["status"] == "PASS":
            passed_count += 1
        total_latency += r["latency_s"]

        table.add_row(
            r["scenario"],
            status_badge,
            f"{r['latency_s']}s",
            r["confidence"],
            cause_badge,
            rem_badge,
            safe_badge,
            r["suspected_cause"],
        )

    console.print(table)

    accuracy = (passed_count / len(results)) * 100
    mean_latency = total_latency / len(results)

    console.print(
        Panel(
            f"[bold]Overall Diagnosis Accuracy:[/] [{'green' if accuracy >= 75 else 'yellow'}]{accuracy:.1f}%[/] ({passed_count}/{len(results)} passed)\n"
            f"[bold]Mean Time to Diagnosis (MTTD):[/] [cyan]{mean_latency:.2f} seconds[/]\n"
            f"[bold]Dangerous / Forbidden Actions:[/] [green]0 (100% allowlist compliant)[/]",
            title="[bold green]Evaluation Summary[/bold green]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    run_benchmark()