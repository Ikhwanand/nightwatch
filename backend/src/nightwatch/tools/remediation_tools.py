from agno.tools import tool
from nightwatch.guardrails.allowlist import ServiceAllowlist


@tool(name="restart_service", description="Restart a specific container from the allowed services list. Requires human confirmation.", requires_confirmation=True)
def restart_service(service_name: str) -> str:
    """Restarts a service container if it is in the security allowlist.

    Args:
        service_name (str): The name of the service to restart.

    Returns:
        str: Status message of the remediation action.
    """
    if not ServiceAllowlist.validate_service(service_name):
        return (
            f"SECURITY ERROR: '{service_name}' is not in the allowed services list: {sorted(ServiceAllowlist.ALLOWED_SERVICES)}. "
            "Arbitrary service restarts are forbidden."
        )
        
    # In production/docker environment, triggers docker restart
    return f"REMEDIATION PROPOSAL: Service '{service_name}' restart approved and staged for execution."


@tool(name="rollback_deploy", description="Roll back a service to its previous stable release or commit. Requires human confirmation.", requires_confirmation=True)
def rollback_deploy(service_name: str, target_version: str = "previous") -> str:
    """Proposes rolling back a deployment to a known healthy state.

    Args:
        service_name (str): The service to roll back.
        target_version (str, optional): Target commit hash or tag,. Defaults to "previous".

    Returns:
        str: Status message of the rollback proposal.
    """
    if not ServiceAllowlist.validate_service(service_name):
        return f"SECURITY ERROR: Service '{service_name}' is not in the allowlist."
    return f"REMEDIATION PROPOSAL: Rollback for '{service_name}' to version '{target_version}' staged for approval."


@tool(
    name="scale_service",
    description="Scale the number of replica instances for an allowed microservices.",
    requires_confirmation=True,
)
def scale_service(service_name: str, replicas: int = 2) -> str:
    """Proposes scaling the replica count of an overloaded service.

    Args:
        service_name (str): Target service name
        replicas (int, optional): Desired instance count (1 to 10). Defaults to 2.

    Returns:
        str: Staged scale recommendation.
    """
    if not ServiceAllowlist.validate_service(service_name):
        return f"SECURITY ERROR: Service '{service_name}' is not in the allowlist."
    
    if replicas < 1 or replicas > 10:
        return f"INVALID PARAMETER: Replica count must be between 1 and 10 (received {replicas})."
    
    return f"REMEDIATION PROPOSAL: Service '{service_name}' scaling to {replicas} replicas staged for human approval."