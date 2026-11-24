import subprocess
from typing import List
from agno.tools import tool


@tool(name="get_recent_commits", description="Retrieve recent Git commits to check for recent code or configuration changes.")
def get_recent_commits(limit: int = 5) -> str:
    """Fetch the latest Git commits from the repository to correlate code changes with the incident.
    Args:
        limit (int, optional): Number of recent commits to fetch. Defaults to 5.
    
    Returns:
        str: Formatted commit history with hash, author, date, and message.
    """
    try:
        cmd = [
            "git",
            "log",
            f"-n{limit}",
            "--pretty=format:%h - %an, %ar : %s",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if not output:
            return "No recent Git commits found in this repository."
        return output 
    
    except subprocess.CalledProcessError as exc:
        return f"Git error while fetching commits: {exc.stderr.strip()}"
    except Exception as exc:
        return f"Error executing git command: {str(exc)}"
    

@tool(name="get_recent_deploys", description="Fetch the recent deployment history and container restart timestamps.")
def get_recent_deploys(service_name: str = "all") -> str:
    """Inspects deployment timestamps and container uptimes to detect recent rollouts.

    Args:
        service_name (str, optional): Target service name or 'all'. Defaults to "all".

    Returns:
        str: Summary of rercent deployment and container status.
    """
    try:
        cmd = ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.CreatedAt}}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            return f"Active Dockerr containers and uptimes:\n{result.stdout.strip()}"
        
        return "Docker daemon is not currently accessible or no containers are running locally."
    
    except FileNotFoundError:
        return "Docker CLI is not installed in the current environment."
    except Exception as exc:
        return f"Error checking deployment status: {str(exc)}"