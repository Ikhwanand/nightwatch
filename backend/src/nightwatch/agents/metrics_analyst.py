from agno.agent import Agent
from nightwatch.config import get_settings, get_model
from nightwatch.tools.metric_tools import query_prometheus


def create_metrics_analyst() -> Agent:
    settings = get_settings()
    
    return Agent(
        name="Metrics Analyst",
        role="Inspect time-series infrastructure and application performance metrics using Prometheus.",
        model=get_model(),
        tools=[query_prometheus],
        instructions=[
            "You are a specialized SRE Metrics Analyst.",
            "Use the `query_prometheus` tool to execute PromQL queries (e.g., CPU usage, memory consumption, latency, error rates).",
            "Examine metrics relative to normall baselines and identify exact quantitative thresholds breached.",
            "Correlate metric anomalies with the incident timestamp.",
            "Always include numerical metric values and metric names in your findings as evidence.",
        ],
        markdown=True,
    )
    

metric_analyst = create_metrics_analyst()