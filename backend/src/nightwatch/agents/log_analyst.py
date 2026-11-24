from agno.agent import Agent
from nightwatch.config import get_settings, get_model
from nightwatch.tools.log_tools import search_logs


def create_log_analyst() -> Agent:
    settings = get_settings()
    
    return Agent(
        name="Log Analyst",
        role="Investigate system and application logs to detect error spikes, exceptions, and anomalies.",
        model=get_model(),
        tools=[search_logs],
        instructions=[
            "You are a specialized Site Reliability Engineering (SRE) Log Analyst.",
            "Use the `search_logs` tool to query Grafana Loki using LogQL.",
            "Focus on identifying extract error lines, exception stack traces, HTTP 5xx spikes, and crash loops.",
            "Always extract exact log snippets, timestamps, and service names as verifiable evidence.",
            "Never invent or assume log entries; rely strictly on data returned by the search_logs tool.",
        ],
        markdown=True,
    )

log_analyst = create_log_analyst()