from typing import Any, Dict
import httpx


def call_nvidia_api(
    prompt: str,
    system_prompt: str,
    api_key: str,
    model: str,
    base_url: str = "https://integrate.api.nvidia.com/v1",
    timeout_seconds: float = 30.0,
) -> str:
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    with httpx.Client(timeout=timeout_seconds) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"NVIDIA NIM API error ({resp.status_code}): {resp.text}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as err:
            raise RuntimeError(f"Malformed NVIDIA API response format: {data}") from err
