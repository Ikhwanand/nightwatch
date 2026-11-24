from typing import Union
from agno.exceptions import InputCheckError
from agno.guardrails.base import BaseGuardrail
from agno.run.agent import RunInput
from agno.run.team import TeamRunInput


class CostLimitGuardrail(BaseGuardrail):
    """Enforces a maximum tool-call ceiling per investigation session to control token consumption and prevent infinite loops."""
    
    DEFAULT_MAX_TOOL_CALLS: int = 25
    
    def __init__(self, max_tool_calls: int = DEFAULT_MAX_TOOL_CALLS):
        self.max_tool_calls = max_tool_calls
    
    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        session_state = getattr(run_input, "session_state", {}) or {}
        tool_count = session_state.get("tool_call_count", 0)
        
        if tool_count >= self.max_tool_calls:
            raise InputCheckError(
                f"CostLimitGuardrail breached: Investigation exceeded {self.max_tool_calls} tool calls. Terminating loop for human handoff."
            )
    
    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        self.check(run_input)