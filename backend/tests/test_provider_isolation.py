import pytest
from app.services.llm.provider import LLMExecutionError, LLMProvider


def test_groq_isolation(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "")

    groq_called = False
    gemini_called = False
    nvidia_called = False
    openrouter_called = False

    def mock_groq(*args, **kwargs):
        nonlocal groq_called
        groq_called = True
        return '{"action": "optimize_budget", "language": "english"}'

    def mock_gemini(*args, **kwargs):
        nonlocal gemini_called
        gemini_called = True
        return '{"action": "optimize_budget", "language": "english"}'

    def mock_nvidia(*args, **kwargs):
        nonlocal nvidia_called
        nvidia_called = True
        return '{"action": "optimize_budget", "language": "english"}'

    def mock_openrouter(*args, **kwargs):
        nonlocal openrouter_called
        openrouter_called = True
        return '{"action": "optimize_budget", "language": "english"}'

    monkeypatch.setattr("app.services.llm.provider.call_groq_api", mock_groq)
    monkeypatch.setattr("app.services.llm.provider.call_gemini_api", mock_gemini)
    monkeypatch.setattr("app.services.llm.provider.call_nvidia_api", mock_nvidia)
    monkeypatch.setattr("app.services.llm.provider.call_openrouter_api", mock_openrouter)

    provider = LLMProvider(provider="groq", allow_rule_fallback=False)
    intent = provider.interpret_modification("Make my trip cheaper")

    assert intent.action == "optimize_budget"
    assert groq_called is True
    assert gemini_called is False
    assert nvidia_called is False
    assert openrouter_called is False


def test_gemini_isolation(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")
    monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "")

    groq_called = False
    gemini_called = False

    def mock_groq(*args, **kwargs):
        nonlocal groq_called
        groq_called = True
        return '{"action": "optimize_budget", "language": "english"}'

    def mock_gemini(*args, **kwargs):
        nonlocal gemini_called
        gemini_called = True
        return '{"action": "optimize_budget", "language": "english"}'

    monkeypatch.setattr("app.services.llm.provider.call_groq_api", mock_groq)
    monkeypatch.setattr("app.services.llm.provider.call_gemini_api", mock_gemini)

    provider = LLMProvider(provider="gemini", allow_rule_fallback=False)
    intent = provider.interpret_modification("Make my trip cheaper")

    assert intent.action == "optimize_budget"
    assert gemini_called is True
    assert groq_called is False


def test_no_fallback_when_disabled(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")

    gemini_called = False

    def mock_failing_groq(*args, **kwargs):
        raise RuntimeError("Groq authentication failure")

    def mock_gemini(*args, **kwargs):
        nonlocal gemini_called
        gemini_called = True
        return '{"action": "optimize_budget", "language": "english"}'

    monkeypatch.setattr("app.services.llm.provider.call_groq_api", mock_failing_groq)
    monkeypatch.setattr("app.services.llm.provider.call_gemini_api", mock_gemini)

    provider = LLMProvider(provider="groq", allow_rule_fallback=False)

    with pytest.raises(LLMExecutionError) as exc_info:
        provider.interpret_modification("Make my trip cheaper")

    assert "Provider 'groq' call failed" in str(exc_info.value)
    assert gemini_called is False
