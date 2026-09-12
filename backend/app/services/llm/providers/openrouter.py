from typing import Any, Dict
import httpx


def call_openrouter_api(
    prompt: str,
    system_prompt: str,
    api_key: str,
    model: str,
    base_url: str = "https://openrouter.ai/api/v1",
    timeout_seconds: float = 30.0,
) -> str:
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://tripwise.app",
        "X-Title": "Tripwise",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
    }

    with httpx.Client(timeout=timeout_seconds) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"OpenRouter API error ({resp.status_code}): {resp.text}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as err:
            raise RuntimeError(f"Malformed OpenRouter API response format: {data}") from err
