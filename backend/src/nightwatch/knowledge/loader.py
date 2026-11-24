from pathlib import Path 
from typing import Dict, List 


class RunbookLoader:
    """Discovers, parses, and searches internal SRE runbooks written in Markdown."""
    
    def __init__(self, runbook_dir: Path | None = None):
        if runbook_dir is None:
            # Default to backend/src/nightwatch/knowledge/runbooks
            self.runbook_dir = Path(__file__).parent / "runbooks"
        else:
            self.runbook_dir = Path(runbook_dir)
        
    
    def load_all_runbooks(self) -> Dict[str, str]:
        """Loads all markdown files in the runbooks directory into memory."""
        runbooks = {}
        if not self.runbook_dir.exists():
            return runbooks
        
        for file_path in self.runbook_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                runbooks[file_path.stem] = content 
            except Exception as e:
                print(f"[RunbookLoader] Error reading {file_path}: {e}")
        
        return runbooks
    
    def search(self, query: str, top_k: int = 2) -> List[Dict[str, str]]:
        """Searches for relevant runbooks by keyword relevance score."""
        runbooks = self.load_all_runbooks()
        if not runbooks:
            return []
        
        query_terms = set(query.lower().replace("-", " ").replace("_", " ").split())
        scored_results = []
        
        for name, content in runbooks.items():
            content_lower = content.lower()
            name_lower = name.lower()
            
            # Calculate match score based on keyword frequency in title and content
            
            score = 0
            for term in query_terms:
                if len(term) < 3:
                    continue 
                if term in name_lower:
                    score += 5 # High priority if in filename/title
                if term in content_lower:
                    score += content_lower.count(term)
        
            if score > 0:
                scored_results.append({"name": name, "content": content, "score": score})
        
        # Sort descending by relevance score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]
    
# Global singleton instance 
runbook_loader = RunbookLoader()