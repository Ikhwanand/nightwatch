from agno.db.postgres import PostgresDb
from agno.workflow.condition import Condition
from agno.workflow.step import Step
from agno.workflow.workflow import Workflow
from nightwatch.agents.change_investigator import change_investigator
from nightwatch.agents.leader import incident_team
from nightwatch.agents.log_analyst import log_analyst
from nightwatch.agents.metrics_analyst import metric_analyst
from nightwatch.agents.remediation import remediation_agent
from nightwatch.agents.triage import triage_agent
from nightwatch.config import get_settings


settings = get_settings()
db = PostgresDb(db_url=settings.database_url)

investigation_workflow = Workflow(
    name="Incident Investigation Workflow",
    db=db,
    steps=[
        # Step 1: Triage alert is coming
        Step(
            name="Triage",
            description="Classification severity (P1-P4) dan deduplication alert",
            agent=triage_agent,
        ),
        # Step 2: Conditional Deep Investigation (especially severity P1 & P2)
        Condition(
            name="Check Severity",
            description="Do deep dive if incident is P1 or P2",
            evaluator=lambda step_input, ctx: getattr(ctx, "session_state", {}).get("severity") in ["P1", "P2"],
            steps=[
                Step(name="Log Analysis", agent=log_analyst),
                Step(name="Metrics Analysis", agent=metric_analyst),
                Step(name="Change Investigation", agent=change_investigator),
            ],
        ),
        # Step 3: Remediation based on SOP
        Step(
            name="Remediation Proposal",
            description="Formulate mitigation action based on SOP",
            agent=remediation_agent,
        ),
        # Step 4: Final Diagnosis Synthesis
        Step(
            name="Incident Commander Synthesis",
            description="Synthesize last diagnosis report",
            agent=incident_team,
        ),
    ],
)