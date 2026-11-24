import httpx
from agno.tools import tool
from nightwatch.config import get_settings


@tool(name="search_logs", description="Search logs and error patterns from Grafana Loki using LogQL query.")
def search_logs(query: str, limit: int = 50) -> str:
    """Search logs using a LogQL query against the Grafana Loki API.

    Args:
        query (str): LogQL string, e.g., '{job="api-server"} |= "error"' or '{container="sample-app"}'
        limit (int, optional): Maximum number of log entries to retrieve. Defaults to 50.

    Returns:
        str: Relevant log entries joined by newlines, or an error message on failure.
    """
    settings = get_settings()
    endpoint = f"{settings.loki_url.rstrip('/')}/loki/api/v1/query_range"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(endpoint, params={"query": query, "limit": limit})
            response.raise_for_status()
            data = response.json()

            streams = data.get("data", {}).get("result", [])
            if not streams:
                return f"No logs found for query: '{query}'"

            extracted_logs = []
            for stream in streams:
                labels = stream.get("stream", {})
                values = stream.get("values", [])
                for timestamp, log_line in values:
                    extracted_logs.append(f"[{labels.get('job', 'app')}] {log_line.strip()}")

            return "\n".join(extracted_logs[:limit])

    except httpx.ConnectError:
        return f"Failed to connect to Loki at {settings.loki_url}. Ensure the Loki service is running."
    except Exception as exc:
        return f"Error retrieving logs from Loki: {str(exc)}"
