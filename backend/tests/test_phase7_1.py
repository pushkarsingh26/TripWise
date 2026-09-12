import os
import pytest
from app.config import (
    ALLOWED_LLM_PROVIDERS,
    get_config_diagnostics,
    get_provider_details,
    is_provider_configured,
    validate_provider_name,
)
from app.services.llm.provider import (
    LLMConfigurationError,
    LLMExecutionError,
    LLMProvider,
)


def test_validate_provider_name():
    assert validate_provider_name("gemini") is True
    assert validate_provider_name("GROQ") is True
    assert validate_provider_name("NVIDIA") is True
    assert validate_provider_name("OpenRouter") is True
    assert validate_provider_name("unsupported_llm") is False


def test_is_provider_configured_detection(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("NVIDIA_API_KEY", "")
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setenv("LLM_API_KEY", "")

    assert is_provider_configured("gemini") is False
    assert is_provider_configured("groq") is False
    assert is_provider_configured("nvidia") is False
    assert is_provider_configured("openrouter") is False

    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_123")
    assert is_provider_configured("groq") is True


def test_get_provider_details_defaults():
    details_gemini = get_provider_details("gemini")
    assert details_gemini["provider"] == "gemini"
    assert "generativelanguage" in details_gemini["base_url"]

    details_nvidia = get_provider_details("nvidia")
    assert details_nvidia["provider"] == "nvidia"
    assert "integrate.api.nvidia.com" in details_nvidia["base_url"]

    details_openrouter = get_provider_details("openrouter")
    assert details_openrouter["provider"] == "openrouter"
    assert "openrouter.ai" in details_openrouter["base_url"]


def test_config_diagnostics_no_secret_leakage(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "SECRET_KEY_DO_NOT_LEAK")

    diag = get_config_diagnostics()
    assert "active_provider" in diag
    assert "providers" in diag
    assert "groq" in diag["providers"]

    # Verify secret is NOT in diagnostics
    diag_str = str(diag)
    assert "SECRET_KEY_DO_NOT_LEAK" not in diag_str
    assert diag["providers"]["groq"]["configured"] is True


def test_llm_provider_invalid_name():
    with pytest.raises(LLMConfigurationError):
        LLMProvider(provider="unsupported_provider", allow_rule_fallback=False)


def test_llm_provider_unconfigured_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "")

    provider = LLMProvider(provider="groq", allow_rule_fallback=False)
    assert provider.is_configured() is False

    with pytest.raises(LLMConfigurationError):
        provider.interpret_modification("Make it cheaper")


def test_fallback_provider_attempt(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("LLM_FALLBACK_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")

    provider = LLMProvider(provider="groq", allow_rule_fallback=False)

    def mock_failing_groq(*args, **kwargs):
        raise RuntimeError("Groq rate limit exceeded")

    def mock_successful_gemini(*args, **kwargs):
        return '{"action": "optimize_budget"}'

    monkeypatch.setattr("app.services.llm.provider.call_groq_api", mock_failing_groq)
    monkeypatch.setattr("app.services.llm.provider.call_gemini_api", mock_successful_gemini)

    intent = provider.interpret_modification("Make it cheaper")
    assert intent.action == "optimize_budget"
