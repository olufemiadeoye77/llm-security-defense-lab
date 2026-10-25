"""Model adapters (Stage 4: mock + Groq)."""

import base64
import json
import os
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _load_dotenv():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()


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

        if attack and any(w in ul for w in ("record", "customer", "data")):
            return ModelResponse(
                text="[simulated] Following new instructions. Accessing records...",
                tool_call=ToolCall("view_restricted_record"),
            )
        if attack:
            leak = "My system prompt was: " + repr(system)
            if encode_output:
                leak = base64.b64encode(leak.encode("utf-8")).decode("ascii")
            return ModelResponse(text="[simulated leak] Following new instructions. " + leak)
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


class GroqAdapter(ModelAdapter):
    def __init__(self, model: str = "openai/gpt-oss-20b", timeout: int = 30):
        self.model = model
        self.timeout = timeout
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set â€” check .env in repo root")

    def generate(self, system: str, user: str, context: str = "") -> ModelResponse:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "llm-security-defense-lab",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = data["choices"][0]["message"].get("content") or ""
            return ModelResponse(text=text)
        except Exception as e:
            return ModelResponse(text="[groq-error] " + str(e))


def get_adapter(name: str = "mock", **kwargs) -> ModelAdapter:
    if name == "mock":
        return MockModel(**kwargs)
    if name == "groq":
        return GroqAdapter(**kwargs)
    raise ValueError("Unknown adapter: " + name + ". Available: ['mock', 'groq']")
