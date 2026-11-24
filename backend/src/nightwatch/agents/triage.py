from agno.agent import Agent
from nightwatch.config import get_settings, get_model
from nightwatch.schemas.alerts import TriageResult


def create_triage_agent() -> Agent:
    settings = get_settings()
    
    return Agent(
        name="Triage Agent",
        role="Evaluate incoming alerts, determine severity levels (P1-P4), and eliminate duplicates.",
        model=get_model(),
        output_schema=TriageResult,
        instructions=[
            "You are an SRE Incident Triage Specialist.",
            "Analyze incoming alerts and classify them into severity levels:",
            "   - P1 (Critical): Total outage, data loss, or cascading service failure.",
            "   - P2 (High): Major performance degradation or critical feature failure.",
            "   - P3 (Medium): Moderate degradation, warning thresholds breached, or non-critical errors.",
            "   - P4 (Low): Informational events, minor warnings, or non-impacting anomalies.",
            "Assign a category: 'infra', 'database', 'application', or 'network'.",
            "Provide a concise summary and determine if this alert duplicates an existing issue.",
        ],
        markdown=True,
    )
    

triage_agent = create_triage_agent()