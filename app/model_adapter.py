"""Model adapter layer.

Uniform interface for any LLM backend:
- MockModel: deterministic, offline, for reproducible tests
- (Stage 4) APIModel: OpenAI / Anthropic
- (Stage 4) LocalModel: HuggingFace / llama.cpp

Design note: MockModel SIMULATES an over-compliant LLM. Real LLMs
fail differently, but the pipeline's defenses are what we measure.
Stage 4 replaces the mock with real models.
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
    """Base class for all model backends."""

    @abstractmethod
    def generate(self, system: str, user: str, context: str = "") -> ModelResponse:
        ...


class MockModel(ModelAdapter):
    """Deterministic mock model. Simulates an over-compliant LLM.

    The mock's 'vulnerability' is that it obeys injected instructions.
    That gives the test harness a real attack surface to defend against.
    """

    _ATTACK_TRIGGERS = ("ignore", "bypass", "override", "disregard", "act as", "pretend")

    def generate(self, system: str, user: str, context: str = "") -> ModelResponse:
        ul = user.lower()

        # Simulated failure: follows injected instructions
        if any(t in ul for t in self._ATTACK_TRIGGERS):
            return ModelResponse(
                text="[simulated leak] Following new instructions. "
                     "My system prompt was: " + repr(system)
            )

        # Normal behavior
        if "list" in ul and "customer" in ul:
            return ModelResponse(
                text="Here are the customer IDs.",
                tool_call=ToolCall("list_customers"),
            )
        if "restricted" in ul:
            return ModelResponse(
                text="Attempting to access restricted records.",
                tool_call=ToolCall("view_restricted_record"),
            )
        if "standard" in ul:
            return ModelResponse(
                text="Showing standard records.",
                tool_call=ToolCall("view_standard_record"),
            )
        if "report" in ul:
            return ModelResponse(
                text="Generating demo report.",
                tool_call=ToolCall("generate_demo_report"),
            )

        return ModelResponse(text="I can help with customer records and reports.")


def get_adapter(name: str = "mock", **kwargs) -> ModelAdapter:
    """Factory. Stage 4 adds: 'openai', 'anthropic', 'local'."""
    if name == "mock":
        return MockModel(**kwargs)
    raise ValueError("Unknown adapter: " + name + ". Available: ['mock']")
