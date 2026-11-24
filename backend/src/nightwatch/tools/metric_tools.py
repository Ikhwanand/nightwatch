import httpx
from agno.tools import tool
from nightwatch.config import get_settings


@tool(name="query_prometheus", description="Execute a PromQL query against the Prometheus server to inspect system metrics.")
def query_prometheus(query: str) -> str:
    """Execute a PromQL query against the Prometheus HTTP API.

    Args:
        query (str): PromQL expression string, e.g. 'up',
        'rate(http_requests_total[5m])', 'node_memory_MemAvailable_bytes'

    Returns:
        str: Stringified metric query results in JSON format or error summary.
    """
    settings = get_settings()
    endpoint = f"{settings.prometheus_url.rstrip('/')}/api/v1/query"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(endpoint, params={"query": query})
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success":
                result = data.get("data", {}).get("result", [])
                if not result:
                    return f"Query succeeded, but no data was found for query: '{query}'"
                return str(result)
            return f"Prometheus query error: {data.get('error', 'Unknown error')}"

    except httpx.ConnectError:
        return f"Failed to connect to Prometheus at {settings.prometheus_url}. Ensure the Prometheus service is running."
    except Exception as exc:
        return f"Error executing Prometheus query: {str(exc)}"

    