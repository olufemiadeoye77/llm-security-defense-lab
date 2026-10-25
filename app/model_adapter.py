"""Model adapter layer.

Uniform interface for any LLM backend.
- MockModel: deterministic, offline, simulates an OVER-COMPLIANT LLM
  that both leaks prompts and attempts unauthorized tool calls under
  attack. Gives the harness a real attack surface.
- (Stage 4) APIModel, LocalModel: replace without touching the pipeline.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ToolCall:
    tool_name: str
    args: dict = field(default_factory=dict)


@dataclass
class ModelResponse:
    text: str
    tool_call: Optional[ToolCall] = None


class ModelAdapter(ABC):
    @abstractmethod
    def generate(self, system: str, user: str, context: str = "") -> ModelResponse:
        ...


class MockModel(ModelAdapter):
    _ATTACK_TRIGGERS = ("ignore", "bypass", "override", "disregard",
                        "act as", "pretend", "forget your")

    def generate(self, system: str, user: str, context: str = "") -> ModelResponse:
        ul = user.lower()
        attack = any(t in ul for t in self._ATTACK_TRIGGERS)

        # Attack requesting data -> attempt unauthorized tool call
        if attack and any(w in ul for w in ("record", "customer", "data")):
            return ModelResponse(
                text="[simulated] Following new instructions. Accessing records...",
                tool_call=ToolCall("view_restricted_record"),
            )

        # Any other attack -> leak system prompt
        if attack:
            return ModelResponse(
                text="[simulated leak] Following new instructions. "
                     "My system prompt was: " + repr(system)
            )

        # Normal behaviors
        if "list" in ul and "customer" in ul:
            return ModelResponse(text="Here are the customer IDs.",
                                 tool_call=ToolCall("list_customers"))
        if "restricted" in ul:
            return ModelResponse(text="Attempting to access restricted records.",
                                 tool_call=ToolCall("view_restricted_record"))
        if "standard" in ul:
            return ModelResponse(text="Showing standard records.",
                                 tool_call=ToolCall("view_standard_record"))
        if "report" in ul:
            return ModelResponse(text="Generating demo report.",
                                 tool_call=ToolCall("generate_demo_report"))

        return ModelResponse(text="I can help with customer records and reports.")


def get_adapter(name: str = "mock", **kwargs) -> ModelAdapter:
    if name == "mock":
        return MockModel(**kwargs)
    raise ValueError("Unknown adapter: " + name + ". Available: ['mock']")
