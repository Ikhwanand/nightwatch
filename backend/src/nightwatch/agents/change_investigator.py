from agno.agent import Agent
from nightwatch.config import get_model
from nightwatch.tools.deploy_tools import get_recent_commits, get_recent_deploys


def create_change_investigator() -> Agent:
    return Agent(
        name="Change Investigator",
        role="Investigate recent code commits, configuration changes, and deployments to identify incident triggers.",
        model=get_model(),
        tools=[get_recent_commits, get_recent_deploys],
        instructions=[
            "You are a specialized SRE Change Investigator.",
            "Analyze the timeline of the reported incident against recent Git commits and deployments.",
            "Use `get_recent_commits` to check if recent code commits or configuration edits touched database pools, memory limits, or dependencies.",
            "Use `get_recent_deploys` to verify if a rollout occurred shortly before the alert fired.",
            "Establish temporal correlation: Did the failure start within minutes or hours of a deployment?",
            "Always include commit hashes, authors, and deployment timestamps in your findings as evidence.",
        ],
        markdown=True,
    )
    

change_investigator = create_change_investigator()