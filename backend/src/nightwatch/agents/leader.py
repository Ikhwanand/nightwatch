from agno.db.postgres import PostgresDb
from agno.team import Team
from agno.team.mode import TeamMode
from nightwatch.agents.log_analyst import log_analyst
from nightwatch.agents.metrics_analyst import metric_analyst
from nightwatch.agents.triage import triage_agent
from nightwatch.agents.change_investigator import change_investigator
from nightwatch.agents.remediation import remediation_agent
from nightwatch.config import get_settings, get_model
from nightwatch.schemas.diagnosis import DiagnosisReport
from nightwatch.tools.history_tools import search_past_incidents
from nightwatch.guardrails.sensitive_data import SensitiveDataGuardrail



def create_incident_team() -> Team:
    settings = get_settings()
    
    # Memory and session persistence in PostgreSQL
    db = PostgresDb(db_url=settings.database_url)
    
    return Team(
        name="Incident Commander Team",
        mode=TeamMode.coordinate, # Leader assigns tasks to specialists and synthesizes findings
        model=get_model(), # If you want use fast model you can change in parameter ex: model=get_model(settings.fast_model)
        db=db,
        enable_session_summaries=True, # Automatically summarize the session in DB
        update_memory_on_run=True, # Agent memorize pattern from previous incident.
        # Guardrails: Automatically redact sensitive credentials before processing
        pre_hooks=[SensitiveDataGuardrail(mask=True)],
        tools=[search_past_incidents], # Leader can find from previous incident.
        members=[
            triage_agent,
            log_analyst,
            metric_analyst,
            change_investigator,
            remediation_agent,
        ],
        output_schema=DiagnosisReport,
        use_json_mode=True,
        instructions=[
            "You are the Incident Commander leading an autonomous SRE virtual team.",
            "Coordinate investigations when an incident or alert is reported:",
            "   1. Have the Triage Agent classify severity and scope.",
            "   2. Delegate log investigation to the Log Analyst to retrieve concrete error traces.",
            "   3. Delegate metric analysis to the Metrics Analyst to quantify performance degradation.",
            "   4. Delegate change analysis to the Change Investigator to check recent commits and deploys.",
            "   5. Consult past incidents using `search_past_incidents` to correlate recurring patterns.",
            "   6. Have the Remediation Agent propose SOP-compliant mitigations.",
            "Synthesize all findings into a single DiagnosisReport.",
            "CRITICAL RULES:",
            "   - Output ONLY the raw JSON object matching the DiagnosisReport schema. Do NOT include markdown code blocks (```json), preamble, or any trailing commentary.",
            "   - Every conclusion MUST be backed by at least one piece of concrete evidence from logs or metrics.",
            "   - Assign a realistic confidence score (0.0 to 1.0) based on the strength of the evidence.",
            "   - Propose clear, actionable remediation steps adhering strictly to official SRE runbooks.",
            "   - Flag whether remediation requires human confirmation (default True for destructive actions).",
        ],
        show_members_responses=True,
        markdown=True,
    )
    

incident_team = create_incident_team()