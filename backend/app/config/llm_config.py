import os
from typing import Any, Dict, Set

ALLOWED_LLM_PROVIDERS: Set[str] = {"groq", "nvidia", "gemini", "openrouter"}

DEFAULT_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"


def validate_provider_name(provider_name: str) -> bool:
    """Returns True if provider_name is one of the supported free providers."""
    return provider_name.lower().strip() in ALLOWED_LLM_PROVIDERS


def is_provider_configured(provider_name: str) -> bool:
    """
    Checks if API key for the given provider is present in environment variables.
    Does NOT make live network or API calls.
    """
    p_clean = provider_name.lower().strip()
    if p_clean == "gemini":
        key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY", "")
    elif p_clean == "groq":
        key = os.getenv("GROQ_API_KEY", "")
    elif p_clean == "nvidia":
        key = os.getenv("NVIDIA_API_KEY", "")
    elif p_clean == "openrouter":
        key = os.getenv("OPENROUTER_API_KEY", "")
    else:
        return False

    return bool(key and key.strip())


def get_provider_details(provider_name: str) -> Dict[str, Any]:
    """
    Returns specific configuration parameters for a requested provider.
    """
    p_clean = provider_name.lower().strip()

    if p_clean == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY", "")
        model = os.getenv("GEMINI_MODEL") or os.getenv("LLM_MODEL") or DEFAULT_GEMINI_MODEL
        base_url = "https://generativelanguage.googleapis.com/v1beta"
    elif p_clean == "groq":
        api_key = os.getenv("GROQ_API_KEY", "")
        model = os.getenv("GROQ_MODEL") or os.getenv("LLM_MODEL") or "llama-3.3-70b-versatile"
        base_url = "https://api.groq.com/openai/v1"
    elif p_clean == "nvidia":
        api_key = os.getenv("NVIDIA_API_KEY", "")
        model = os.getenv("NVIDIA_MODEL") or os.getenv("LLM_MODEL") or "meta/llama-3.3-70b-instruct"
        base_url = os.getenv("NVIDIA_BASE_URL") or DEFAULT_NVIDIA_BASE_URL
    elif p_clean == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        model = os.getenv("OPENROUTER_MODEL") or os.getenv("LLM_MODEL") or "meta-llama/llama-3.3-70b-instruct:free"
        base_url = os.getenv("OPENROUTER_BASE_URL") or DEFAULT_OPENROUTER_BASE_URL
    else:
        raise ValueError(f"Unsupported LLM provider '{provider_name}'. Allowed providers: {sorted(ALLOWED_LLM_PROVIDERS)}")

    try:
        timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    except ValueError:
        timeout = 30.0

    try:
        retries = int(os.getenv("LLM_MAX_RETRIES", "2"))
    except ValueError:
        retries = 2

    return {
        "provider": p_clean,
        "api_key": api_key.strip(),
        "model": model.strip(),
        "base_url": base_url.strip(),
        "timeout_seconds": max(timeout, 1.0),
        "max_retries": max(retries, 0),
    }


def get_config_diagnostics() -> Dict[str, Any]:
    """
    Returns safe configuration diagnostics without leaking actual API key secrets.
    """
    active_provider = (os.getenv("LLM_PROVIDER") or "gemini").lower().strip()
    fallback_provider = (os.getenv("LLM_FALLBACK_PROVIDER") or "").lower().strip()

    provider_status = {}
    for p in sorted(ALLOWED_LLM_PROVIDERS):
        details = get_provider_details(p)
        provider_status[p] = {
            "configured": is_provider_configured(p),
            "model": details["model"],
            "base_url": details["base_url"],
        }

    try:
        timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    except ValueError:
        timeout = 30.0

    try:
        retries = int(os.getenv("LLM_MAX_RETRIES", "2"))
    except ValueError:
        retries = 2

    return {
        "active_provider": active_provider,
        "active_provider_valid": validate_provider_name(active_provider),
        "active_provider_configured": is_provider_configured(active_provider) if validate_provider_name(active_provider) else False,
        "fallback_provider": fallback_provider if fallback_provider else None,
        "fallback_provider_configured": is_provider_configured(fallback_provider) if validate_provider_name(fallback_provider) else False,
        "providers": provider_status,
        "timeout_seconds": timeout,
        "max_retries": retries,
    }
