from agno.tools import tool
from nightwatch.db.database import search_past_incidents_db


@tool(name="search_past_incidents",
      description="Search the PostgreSQL historical database for similar past incidents and their resolutions.",
      )
def search_past_incidents(query: str) -> str:
    """Searches past incidents postmortems and diagnosis to compare patterns and solutions

    Args:
        query (str): Keyword to match against past causes (e.g., 'memory leak', 'sample-app', 'database timeout').

    Returns:
        str: Summary of matching historical incidents and how they were resolved.
    """
    past_incidents = search_past_incidents_db(query, limit=3)
    if not past_incidents:
        return f"No similar past incidents found in database matching '{query}'. This way be a novel failure mode."
    
    output = []
    for inc in past_incidents:
        diag = inc.get("diagnosis", {})
        recs = diag.get("recommended_actions", ["No actions recorded"]) if isinstance(diag, dict) else []
        output.append(
            f"- Incident [{inc['incident_id']}] (Severity: {inc['severity']}) - {inc['created_at']}\n"
            f" Suspected Cause: {inc['suspected_cause']}\n"
            f" Confidence: {inc['confidence'] * 100:.0f}%\n"
            f" Key Mitigation: {', '.join(recs[:2]) if recs else 'N/A'}"
        )
    
    return "=== MATCHING HISTORICAL INCIDENTS ===\n" + "\n".join(output)