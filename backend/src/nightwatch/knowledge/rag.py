from pathlib import Path
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.markdown_reader import MarkdownReader
from agno.vectordb.pgvector import PgVector, SearchType
from nightwatch.config import get_settings
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder


settings = get_settings()

# Inisialisasi PgVector Knowledge Base bawaan Agno
runbook_knowledge = Knowledge(
    vector_db=PgVector(
        table_name="sre_runbooks",
        db_url=settings.database_url,
        search_type=SearchType.hybrid, # Hybrid Search: Semantic Vector + Keyword BM25
        embedder=SentenceTransformerEmbedder(),
    ),
)


def seed_runbooks_to_pgvector() -> None:
    """Reads all markdown runbooks and embeds them into PostgreSQL via Agno Knowledge."""
    runbook_dir = Path(__file__).parent / "runbooks"
    if not runbook_dir.exists():
        print(f"[RAG] Directory {runbook_dir} not found")
        return 
    
    print(f"[RAG] Ingesting SRE runbooks from {runbook_dir} into PostgreSQL PgVector...")
    try:
        runbook_knowledge.insert(
            path=str(runbook_dir),
            reader=MarkdownReader(),
            upsert=True,
        )
        print("[RAG] SRE runbooks successfully indexed into PgVector table 'sre_runbooks'.")
    except Exception as exc:
        print(f"[RAG] Warning during PgVector ingestion: {exc}")
        

if __name__ == "__main__":
    seed_runbooks_to_pgvector()