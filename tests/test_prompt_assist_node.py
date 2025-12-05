import pytest

from comfyui_nodes.prompt_assist import PromptAssistNode


class DummyResponse:
    def __init__(self, output_text: str):
        self.output_text = output_text


class DummyClient:
    def __init__(self, output_text: str):
        self._output_text = output_text
        self.responses = self

    def create(self, **_: object) -> DummyResponse:  # type: ignore[override]
        return DummyResponse(self._output_text)


@pytest.fixture(autouse=True)
def clear_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def test_bypass_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    node = PromptAssistNode(client_factory=lambda: DummyClient("unused"))
    prompt, status = node.assist("keep original")
    assert prompt == "keep original"
    assert "missing" in status.lower()


def test_rewrite_uses_client_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    node = PromptAssistNode(client_factory=lambda: DummyClient("rewritten text"))
    prompt, status = node.assist("hello", model="gpt-4o-mini")
    assert prompt == "rewritten text"
    assert "gpt-4o-mini" in status


def test_rate_limit_prevents_extra_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    node = PromptAssistNode(client_factory=lambda: DummyClient("ok"))
    prompt, _ = node.assist("first", rate_limit_per_minute=1)
    assert prompt == "ok"
    with pytest.raises(ValueError):
        node.assist("second", rate_limit_per_minute=1)


def test_safety_mode_returns_sanitized_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    node = PromptAssistNode(
        client_factory=lambda: DummyClient('{"status": "flagged", "prompt": "safe text"}')
    )
    prompt, status = node.assist("unsafe prompt", mode="safety_check")
    assert prompt == "safe text"
    assert "flagged" in status
