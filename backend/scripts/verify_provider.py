import json
import os
import sys
import time
from typing import Any, Dict

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

# Load backend/.env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path, override=True)

from app.config import get_config_diagnostics, get_provider_details, is_provider_configured
from app.services.llm.provider import LLMConfigurationError, LLMExecutionError, LLMProvider
from app.services.trip_modifier import TripModifier


def main():
    print("=========================================================")
    print("           TRIPWISE PROVIDER VERIFICATION SUITE          ")
    print("=========================================================")

    active_provider = (os.getenv("LLM_PROVIDER") or "gemini").lower().strip()
    details = get_provider_details(active_provider)
    configured = is_provider_configured(active_provider)

    print(f"Active Provider : {active_provider.upper()}")
    print(f"Model           : {details['model']}")
    print(f"Base URL        : {details['base_url']}")
    print(f"API Key         : {'CONFIGURED' if configured else 'MISSING / EMPTY'}")
    print(f"Fallback        : {os.getenv('LLM_FALLBACK_PROVIDER') or 'DISABLED'}")
    print(f"Timeout (s)     : {details['timeout_seconds']}")
    print(f"Max Retries     : {details['max_retries']}")
    print("---------------------------------------------------------")

    if not configured:
        print(f"\n[ERROR] API key for provider '{active_provider}' is not configured in backend/.env!")
        print(f"Please set the corresponding API key (e.g. GROQ_API_KEY, GEMINI_API_KEY, NVIDIA_API_KEY, OPENROUTER_API_KEY) in .env.")
        sys.exit(1)

    try:
        # Instantiate provider strictly without rule fallback to force live API call
        provider = LLMProvider(allow_rule_fallback=False)
    except LLMConfigurationError as err:
        print(f"\n[ERROR] Configuration failed: {err}")
        sys.exit(1)

    modifier = TripModifier()

    sample_trip = {
        "origin": "Indore",
        "destination": "Goa",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15",
        "budget": 30000.0,
        "travelers": 2,
        "preferences": ["beaches", "food"],
    }

    test_prompts = [
        {"name": "English Intent", "prompt": "Make my trip cheaper", "exp_lang": "english"},
        {"name": "English Activity Request", "prompt": "Remove expensive activities", "exp_lang": "english"},
        {"name": "Hinglish Intent", "prompt": "Trip ka budget kam kar do", "exp_lang": "hinglish"},
        {"name": "Hindi Intent", "prompt": "मेरा ट्रिप सस्ता कर दो", "exp_lang": "hindi"},
        {"name": "Structured Intent", "prompt": "Change my budget to 25000", "exp_lang": "english"},
    ]

    results = []
    print("\nExecuting Standard Provider Test Suite...\n")

    for idx, t in enumerate(test_prompts, start=1):
        prompt = t["prompt"]
        print(f"[{idx}/{len(test_prompts)}] Testing: '{prompt}' ({t['name']})")
        start_time = time.time()

        try:
            intent = provider.interpret_modification(prompt, current_trip=sample_trip)
            latency_ms = round((time.time() - start_time) * 1000, 2)

            mod_res = modifier.modify_trip(sample_trip, intent)

            success = mod_res.get("status") == "success"
            action = intent.action
            lang = intent.language

            print(f"  ├─ Status   : {'SUCCESS' if success else 'FAILED'}")
            print(f"  ├─ Action   : {action}")
            print(f"  ├─ Language : {lang}")
            print(f"  ├─ Latency  : {latency_ms} ms")
            print(f"  └─ Message  : \"{mod_res.get('message')}\"")
            print("")

            results.append({
                "name": t["name"],
                "prompt": prompt,
                "status": "PASS" if success else "FAIL",
                "action": action,
                "language": lang,
                "latency_ms": latency_ms,
                "error": None,
            })
        except Exception as err:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            print(f"  ├─ Status   : FAILED")
            print(f"  ├─ Error    : {err}")
            print(f"  └─ Latency  : {latency_ms} ms\n")

            results.append({
                "name": t["name"],
                "prompt": prompt,
                "status": "FAIL",
                "action": "N/A",
                "language": "N/A",
                "latency_ms": latency_ms,
                "error": str(err),
            })

    # Performance Summary
    print("=========================================================")
    print(f"         VERIFICATION SUMMARY FOR {active_provider.upper()}          ")
    print("=========================================================")
    print(f"{'Test Prompt':<25} | {'Status':<6} | {'Action':<18} | {'Lang':<8} | {'Latency':<8}")
    print("-" * 75)

    passed_count = 0
    for r in results:
        if r["status"] == "PASS":
            passed_count += 1
        print(f"{r['name']:<25} | {r['status']:<6} | {r['action']:<18} | {r['language']:<8} | {r['latency_ms']} ms")

    print("-" * 75)
    print(f"Total Tests : {len(results)}")
    print(f"Passed      : {passed_count}")
    print(f"Failed      : {len(results) - passed_count}")

    if passed_count == len(results):
        print(f"\n[VERIFICATION PASSED] Provider '{active_provider}' is fully operational!")
        sys.exit(0)
    else:
        print(f"\n[VERIFICATION FAILED] Provider '{active_provider}' encountered errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
