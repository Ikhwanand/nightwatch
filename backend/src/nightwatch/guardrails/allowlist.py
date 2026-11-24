from typing import Set 


class ServiceAllowlist:
    """Security allowlist enforment for automated or staged remediation actions."""
    
    # Explicitly permitted service targets in the monitored cluster
    ALLOWED_SERVICES: Set[str] = {
        "api-server",
        "sample-app",
        "worker",
        "cache",
    }
    
    ALLOWED_ACTIONS: Set[str] = {
        "restart",
        "rollback",
        "scale",
        "manual",
    }
    
    @classmethod
    def validate_service(cls, service_name: str) -> bool:
        """Checks if a target service is within the allowed in infrastructure scope."""
        return service_name.strip().lower() in cls.ALLOWED_SERVICES
    
    @classmethod
    def validate_action(cls, action_type: str) -> bool:
        """Checks if an action type is within the permitted remediation operations."""
        return action_type.strip().lower() in cls.ALLOWED_ACTIONS
    