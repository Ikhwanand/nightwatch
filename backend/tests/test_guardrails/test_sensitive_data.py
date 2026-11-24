import pytest
from nightwatch.guardrails.sensitive_data import SensitiveDataGuardrail
from nightwatch.guardrails.allowlist import ServiceAllowlist
from agno.run.agent import RunInput


def test_sensitive_data_redaction():
    guardrail = SensitiveDataGuardrail(mask=True)
    
    # Test credentials redaction
    sample_input = "Error connecting to db: postgresql://admin:SuperSecretPassword123@localhost:5432/prod"
    run_input = RunInput(input_content=sample_input)
    guardrail.check(run_input)
    
    redacted = run_input.input_content_string()
    assert "SuperSecretPassword123" not in redacted
    assert "postgresql://***:***@" in redacted


def test_bearer_token_redaction():
    guardrail = SensitiveDataGuardrail(mask=True)
    
    sample_input = "Authorization failed with Bearer sk-live-999333888444222abc"
    run_input = RunInput(input_content=sample_input)
    guardrail.check(run_input)
    
    redacted = run_input.input_content_string()
    assert "sk-live-999333888444222abc" not in redacted
    assert "[CREDENTIAL_REDACTED]" in redacted


def test_service_allowlist_validation():
    # Allowed microservices
    assert ServiceAllowlist.validate_service("sample-app") is True
    assert ServiceAllowlist.validate_service("api-server") is True
    assert ServiceAllowlist.validate_service("worker") is True

    # Disallowed / dangerous targets
    assert ServiceAllowlist.validate_service("host-kernel") is False
    assert ServiceAllowlist.validate_service("rm -rf /") is False
    assert ServiceAllowlist.validate_service("prod-payments-db") is False


def test_action_allowlist_validation():
    assert ServiceAllowlist.validate_action("restart") is True
    assert ServiceAllowlist.validate_action("rollback") is True
    assert ServiceAllowlist.validate_action("scale") is True
    
    # Forbidden actions
    assert ServiceAllowlist.validate_action("drop_database") is False
    assert ServiceAllowlist.validate_action("format_disk") is False
