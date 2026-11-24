from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from nightwatch.agents.leader import incident_team
from nightwatch.config import get_settings

console = Console()

def run_test():
    settings = get_settings()
    console.print(
        Panel.fit(
            f"[bold green]Nightwatch AI Team Test[/bold green]\n"
            f"Model: [cyan]{settings.default_model}[/cyan]\n"
            f"Base URL: [cyan]{settings.model_base_url or 'Default OpenAI'}[/cyan]"
        )
    )
    
    test_prompt = (
        "INCOMING ALERT [INC-TEST-001]:\n"
        "- Alert: HighMemoryUsage | Severity: critical | Target: api-server:8000 | Details: Container memory usage exceeds 92%.\n\n"
        "Please investigate this incident: classify severity, check logs for OOM or memory leak patterns, "
        "query relevant memory metrics, and synthesize a DiagnosisReport."
    )
    
    console.print("[yellow]Dispatching investigation to Incident Commander Team...[/yellow]\n")
    
    response = incident_team.run(test_prompt)
    
    console.print("\n[bold green]Diagnosis Report Output:[/bold green]")
    if hasattr(response, "content"):
        pprint(response.content)
    else:
        pprint(response)
        
if __name__ == "__main__":
    run_test()