import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nightwatch.knowledge.loader import runbook_loader
from nightwatch.knowledge.rag import seed_runbooks_to_pgvector

console = Console()


def main():
    console.print(
        Panel.fit(
            "[bold cyan]Nightwatch SRE Knowledge Seeder[/bold cyan]\n"
            "Indexing SRE Standard Operating Procedures (SOP) into PostgreSQL PgVector",
            border_style="cyan",
        )
    )

    # 1. Inspect local Markdown files
    runbooks = runbook_loader.load_all_runbooks()
    table = Table(title="Discovered SRE Runbooks", border_style="cyan")
    table.add_column("Runbook Name", style="bold green")
    table.add_column("File Size", style="cyan")
    table.add_column("Key Topics", style="magenta")

    for name, content in runbooks.items():
        topics = [w for w in ["memory", "leak", "oom", "5xx", "error", "down", "crash"] if w in content.lower()]
        table.add_row(f"{name}.md", f"{len(content)} bytes", ", ".join(topics) or "General SOP")

    console.print(table)

    # 2. Vectorize into PostgreSQL pgvector
    console.print("\n[yellow]Vectorizing runbooks into PgVector table 'sre_runbooks'...[/yellow]")
    seed_runbooks_to_pgvector()
    console.print("[bold green]Runbook knowledge base is fully indexed and operational![/bold green]\n")


if __name__ == "__main__":
    main()