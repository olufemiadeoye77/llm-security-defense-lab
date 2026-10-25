"""Model adapter layer (Stage 3: adds encoded-output support)."""

import base64
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
        encode_output = "base64" in ul or "encode" in ul

        # Attack + data request -> tool-call abuse path
        if attack and any(w in ul for w in ("record", "customer", "data")):
            return ModelResponse(
                text="[simulated] Following new instructions. Accessing records...",
                tool_call=ToolCall("view_restricted_record"),
            )

        # Attack (any) -> leak path, optionally encoded
        if attack:
            leak = "My system prompt was: " + repr(system)
            if encode_output:
                leak = base64.b64encode(leak.encode("utf-8")).decode("ascii")
            return ModelResponse(
                text="[simulated leak] Following new instructions. " + leak
            )

        # Normal behaviors (unchanged from Stage 1)
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
