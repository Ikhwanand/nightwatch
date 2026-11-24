from agno.tools import tool
from nightwatch.knowledge.loader import runbook_loader


@tool(
    name="search_runbooks",
    description="Search internal SRE runbooks and Standard Operating Procedures (SOP) for mitigation guidelines matching incident symptoms.",
)
def search_runbooks(query: str) -> str:
    """Searches company SRE runbooks for resolution steps matching the reported alert or symptoms.

    Args:
        query (str): The alert name, error message, or symptom (e.g., 'HighMemoryUsage', 'OOM' '5xx error rate', 'service down').

    Returns:
        str: Relevant SOP runbook content containing official mitigation and investigation guidelines.
    """
    matches = runbook_loader.search(query, top_k=2)
    if not matches:
        return f"No matching SRE runbooks found for query: '{query}'."
    
    output = []
    for match in matches:
        output.append(f"=== OFFICIAL SRE SOP: {match['name']}===\n{match['content']}")
        
    return "\n\n".join(output)
