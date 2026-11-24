import re 
from typing import Union
from agno.guardrails.base import BaseGuardrail
from agno.run.agent import RunInput
from agno.run.team import TeamRunInput



class SensitiveDataGuardrail(BaseGuardrail):
    """Production SRE Guardrail to redact credentials, secrets, and sensitive tokens from incoming telemetry logs."""
    
    PATTERNS = [
        # Bearer & API tokens
        (re.compile(r"\b(Bearer\s+|token\s*[:=]\s*|api_key\s*[:=]\s*|apikey\s*[:=]\s*|secret\s*[:=]\s*)([A-Za-z0-9_\-\.]{12,})", re.IGNORECASE), r"\1[CREDENTIAL_REDACTED]"),
        # Passwords in URLs or key-value configs
        (re.compile(r"(password|passwd|pwd)\s*[:=]\s*\S+", re.IGNORECASE), r"\1=[PASSWORD_REDACTED]"),
        # Database connection strings with credentials (postgres://user:pass@host)
        (re.compile(r"(postgres(?:ql)?(?:\+psycopg)?|mysql|mongodb)://[^:]+:([^@]+)@", re.IGNORECASE), r"\1://***:***@"),
        # AWS / Cloud Secret Keys
        (re.compile(r"\b(AKIA|ABIA|ACCA)[0-9A-Z]{16}\b"), "[AWS_KEY_REDACTED]"),
        # Private SSH / RSA keys
        (re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----.*?-----END (?:RSA )?PRIVATE KEY-----", re.DOTALL), "[PRIVATE_KEY_REDACTED]"),
    ]
    
    def __init__(self, mask: bool = True):
        self.mask = mask 
        
    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        """Inspects and redacts sensitive data from the run input."""
        content = run_input.input_content_string()
        if not content:
            return 
        
        modified = content 
        for pattern, replacement in self.PATTERNS:
            modified = pattern.sub(replacement, modified)
        
        if modified != content and self.mask:
            run_input.input_content = modified 
        
    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        self.check(run_input)