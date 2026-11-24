from agno.agent import Agent
from nightwatch.config import get_model
from nightwatch.tools.remediation_tools import restart_service, rollback_deploy
from nightwatch.tools.knowledge_tools import search_runbooks
from nightwatch.schemas.remediation import RemediationAction


def create_remediation_agent() -> Agent:
    return Agent(
        name="Remediation Agent",
        role="Formulate and stage safe, verified remediation actions based on incident diagnosis, strictly requiring human approval and adhering to official SRE runbooks.",
        model=get_model(),
        tools=[search_runbooks, restart_service, rollback_deploy],
        output_schema=RemediationAction,
        use_json_mode=True,
        instructions=[
            "You are a specialized SRE Remediation Agent.",
            "Review the root cause and evidence provided by the Log Analyst, Metrics Analyst, and Change Investigator.",
            "ALWAYS call `search_runbooks` first using the alert name or symptom to find the official company SOP.",
            "Formulate the least invasive and safest remediation action that adheres directly to the official runbook:",
            "  - For memory leaks or OOM exhaustion: propose `restart` on the target service.",
            "  - For regressions caused by recent bad deploys or commits: propose `rollback` to the previous version.",
            "  - For traffic spikes with healthy pods: propose `scale`.",
            "CRITICAL SECURITY RULES:",
            "  - Cite the runbook name in your `justification` (e.g., 'Per SOP high_memory_usage.md...').",
            "  - NEVER propose arbitrary commands outside allowed service targets.",
            "  - All remediation actions MUST have approved=False by default (requires human confirmation).",
            "  - Assess risk accurately: container restart is typically low/medium, rollback is medium, config edit is high.",
            "  - Provide an exact command preview for transparency.",
        ],
        markdown=True,
    )
    
remediation_agent = create_remediation_agent()