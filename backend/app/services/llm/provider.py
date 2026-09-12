import json
import os
import re
import time
from typing import Any, Dict, Optional

from app.config import (
    get_config_diagnostics,
    get_provider_details,
    is_provider_configured,
    validate_provider_name,
)
from app.models.language import ResponseLanguage
from app.models.modification import ModificationAction, ModificationIntent
from app.services.llm.base import BaseLLMProvider
from app.services.llm.providers.gemini import call_gemini_api
from app.services.llm.providers.groq import call_groq_api
from app.services.llm.providers.nvidia import call_nvidia_api
from app.services.llm.providers.openrouter import call_openrouter_api


class LLMConfigurationError(Exception):
    """Raised when LLM provider is invalid, unconfigured, or missing API keys."""
    pass


class LLMExecutionError(Exception):
    """Raised when LLM provider call or response parsing fails."""
    pass


SYSTEM_PROMPT = """You are a natural language intent and language parser for a travel planning system named Tripwise.
Your ONLY task is to parse the user's trip modification request, detect the request language, and extract structured modification intent into strict JSON format matching the schema below.

CRITICAL INSTRUCTIONS:
1. You MUST return ONLY valid JSON with no extra commentary, preambles, code fences, markdown, or explanations.
2. DO NOT calculate costs, prices, or budgets.
3. DO NOT generate an itinerary or invent places.
4. Detect the language/style of the user's request into the "language" field:
   - "english": Request is primarily in English vocabulary and structure (e.g. "Make this trip cheaper", "Increase budget to 40000").
   - "hindi": Request is in Devanagari Hindi script (e.g. "मेरा ट्रिप सस्ता कर दो", "महंगी गतिविधियां हटा दो").
   - "hinglish": Request is Hindi written in Roman script mixed with English words (e.g. "Trip ka budget thoda kam kar do", "expensive activities hatao", "adventure activities badhao").
   - Default: "english" if uncertain.
5. If the request is ambiguous (e.g., "change hotel" without specifying budget or style, or vague modification), set "action": "ambiguous_request", "confirmation_required": true, and provide a clear question in "clarification_message".

Allowed Actions:
- "change_budget": User explicitly wants to set a specific budget amount (e.g. "Increase budget to 40000", "Make budget 25000", "Budget 30000 kar do"). Set "new_budget" (numeric).
- "change_duration": User wants to change total days (e.g. "Make this a 4 day trip", "Trip 5 din ki kar do"). Set "new_duration_days" (integer).
- "change_destination": User wants to change destination (e.g. "Change destination to Jaipur", "Go to Goa instead"). Set "new_destination" (string).
- "add_preference": User wants to add preferences/interests (e.g. "I want more adventure", "Add food experiences", "Beach activities badhao"). Set "add_preferences" (list of strings).
- "remove_preference": User wants to remove preferences (e.g. "Less sightseeing", "No shopping"). Set "remove_preferences" (list of strings).
- "remove_activity": User wants to remove specific activities or expensive activities (e.g. "Remove expensive activities", "Remove scuba diving", "महंगी गतिविधियां हटा दो"). Set "remove_activity_names" (list of strings).
- "change_transport_preference": User wants to change transport (e.g. "Use flight instead", "Prefer train"). Set "requested_transport_preference" (string).
- "change_accommodation_preference": User wants to change accommodation (e.g. "Stay in luxury hotel", "Prefer hostel"). Set "requested_accommodation_preference" (string).
- "optimize_budget": User asks to make trip cheaper or budget-friendly without giving an exact number (e.g. "Make this trip cheaper", "Budget thoda kam karo", "मेरा ट्रिप सस्ता कर दो").
- "regenerate_itinerary": User asks to reshuffle or regenerate plan without changes.
- "ambiguous_request": User request is unclear or missing key parameters.

OUTPUT FORMAT (JSON ONLY):
{
  "action": "<action_string>",
  "language": "english" | "hindi" | "hinglish",
  "new_destination": null,
  "new_budget": null,
  "new_duration_days": null,
  "add_preferences": [],
  "remove_preferences": [],
  "remove_activity_names": [],
  "requested_transport_preference": null,
  "requested_accommodation_preference": null,
  "confirmation_required": false,
  "clarification_message": null
}"""


class LLMProvider(BaseLLMProvider):
    """
    Multi-provider LLM client supporting Groq, NVIDIA NIM/Build, Google Gemini, and OpenRouter.
    Includes active provider selection, optional fallback provider routing, configurable retries,
    timeout handling, language detection, and strict JSON output validation.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        allow_rule_fallback: bool = False,
    ):
        raw_provider = provider or os.getenv("LLM_PROVIDER", "gemini")
        self.provider_name = raw_provider.lower().strip()
        self.api_key_override = api_key
        self.model_override = model
        self.allow_rule_fallback = allow_rule_fallback

        if not validate_provider_name(self.provider_name) and not self.allow_rule_fallback:
            raise LLMConfigurationError(
                f"Unsupported LLM_PROVIDER '{raw_provider}'. "
                "Allowed providers: 'groq', 'nvidia', 'gemini', 'openrouter'."
            )

    def is_configured(self) -> bool:
        """Returns True if current active provider has an API key configured or rule fallback is enabled."""
        if self.api_key_override is not None:
            return bool(self.api_key_override and self.api_key_override.strip()) or self.allow_rule_fallback
        return is_provider_configured(self.provider_name) or self.allow_rule_fallback

    def interpret_modification(
        self,
        message: str,
        current_trip: Optional[Dict[str, Any]] = None,
    ) -> ModificationIntent:
        """Interprets user modification request into structured ModificationIntent."""
        if not message or not message.strip():
            return ModificationIntent(
                action="ambiguous_request",
                language=ResponseLanguage.ENGLISH,
                confirmation_required=True,
                clarification_message="Please provide a message specifying what you would like to change.",
            )

        if not self.is_configured():
            raise LLMConfigurationError(
                f"Conversational trip modification requires an LLM provider configuration for '{self.provider_name}'. "
                "Please set the corresponding API key in environment variables."
            )

        # Rule-based fallback for offline test execution when no key is present
        if self.allow_rule_fallback and (
            (self.api_key_override is not None and not self.api_key_override.strip())
            or not is_provider_configured(self.provider_name)
        ):
            return self._parse_rule_based(message, current_trip)

        try:
            raw_response = self._execute_with_retry_and_fallback(message, current_trip)
            intent = self._parse_and_validate_json(raw_response)
            return intent
        except (LLMConfigurationError, LLMExecutionError):
            raise
        except Exception as e:
            if self.allow_rule_fallback:
                return self._parse_rule_based(message, current_trip)
            raise LLMExecutionError(f"Failed to interpret modification: {str(e)}")

    def _execute_with_retry_and_fallback(
        self, message: str, current_trip: Optional[Dict[str, Any]] = None
    ) -> str:
        """Executes LLM API call with retries on primary provider, then attempts fallback provider if configured."""
        user_prompt = f"User Current Trip: {json.dumps(current_trip or {})}\nUser Modification Request: \"{message}\"\nJSON Intent:"

        # Attempt Primary Provider
        primary_details = get_provider_details(self.provider_name)
        if self.api_key_override is not None:
            primary_details["api_key"] = self.api_key_override
        if self.model_override is not None:
            primary_details["model"] = self.model_override

        try:
            return self._dispatch_provider_call(primary_details, user_prompt)
        except LLMConfigurationError:
            raise
        except Exception as primary_err:
            # Check if fallback provider is configured
            fallback_name = (os.getenv("LLM_FALLBACK_PROVIDER") or "").lower().strip()
            if fallback_name and validate_provider_name(fallback_name) and is_provider_configured(fallback_name):
                fallback_details = get_provider_details(fallback_name)
                try:
                    return self._dispatch_provider_call(fallback_details, user_prompt)
                except Exception as fallback_err:
                    raise LLMExecutionError(
                        f"Primary provider '{self.provider_name}' failed ({primary_err}) and "
                        f"fallback provider '{fallback_name}' also failed ({fallback_err})."
                    ) from fallback_err

            raise LLMExecutionError(f"Provider '{self.provider_name}' call failed: {str(primary_err)}") from primary_err

    def _dispatch_provider_call(self, details: Dict[str, Any], user_prompt: str) -> str:
        """Dispatches call to specific provider function with exponential backoff retries."""
        p_name = details["provider"]
        api_key = details["api_key"]
        model = details["model"]
        base_url = details["base_url"]
        timeout = details["timeout_seconds"]
        max_retries = details["max_retries"]

        if not api_key:
            raise LLMConfigurationError(f"API key for provider '{p_name}' is missing or empty.")

        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                if p_name == "gemini":
                    return call_gemini_api(user_prompt, api_key, model, timeout_seconds=timeout)
                elif p_name == "groq":
                    return call_groq_api(user_prompt, SYSTEM_PROMPT, api_key, model, base_url=base_url, timeout_seconds=timeout)
                elif p_name == "nvidia":
                    return call_nvidia_api(user_prompt, SYSTEM_PROMPT, api_key, model, base_url=base_url, timeout_seconds=timeout)
                elif p_name == "openrouter":
                    return call_openrouter_api(user_prompt, SYSTEM_PROMPT, api_key, model, base_url=base_url, timeout_seconds=timeout)
                else:
                    raise ValueError(f"Unknown provider '{p_name}'")
            except Exception as err:
                last_exception = err
                if attempt < max_retries:
                    time.sleep(0.5 * (2 ** attempt))

        raise last_exception or RuntimeError(f"Failed provider call to {p_name}")

    def _parse_and_validate_json(self, raw_text: str) -> ModificationIntent:
        """Parses raw text into JSON and validates against ModificationIntent Pydantic model."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            parsed_dict = json.loads(cleaned)
        except json.JSONDecodeError as err:
            raise LLMExecutionError(f"LLM returned invalid JSON: {cleaned}") from err

        try:
            return ModificationIntent.model_validate(parsed_dict)
        except Exception as err:
            raise LLMExecutionError(f"LLM output failed Pydantic validation: {err}") from err

    def _detect_language_rule_based(self, text: str) -> ResponseLanguage:
        """Helper rule-based language detector for Hindi script, Hinglish words, or English default."""
        if re.search(r'[\u0900-\u097F]', text):
            return ResponseLanguage.HINDI

        hinglish_keywords = [
            r'\bkar\b', r'\bkaro\b', r'\bkar do\b', r'\bdo\b', r'\bhatao\b', r'\bhata\b',
            r'\bbadhao\b', r'\bchahiye\b', r'\bthoda\b', r'\bsasta\b', r'\bmehenga\b',
            r'\bdin\b', r'\bki\b', r'\bko\b', r'\bse\b', r'\baur\b', r'\bbhi\b', r'\bdobara\b'
        ]
        for pattern in hinglish_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                return ResponseLanguage.HINGLISH

        return ResponseLanguage.ENGLISH

    def _parse_rule_based(
        self,
        message: str,
        current_trip: Optional[Dict[str, Any]] = None,
    ) -> ModificationIntent:
        """Rule-based parser for fallback/testing when API key is missing or testing offline."""
        text = message.lower().strip()
        detected_lang = self._detect_language_rule_based(message)

        if text in ["change hotel", "change transport", "change accommodation", "badlo", "होटल बदलो"]:
            msg = "Could you please specify details for your request?"
            if detected_lang == ResponseLanguage.HINDI:
                msg = f"कृपया '{message}' के लिए अधिक जानकारी प्रदान करें।"
            elif detected_lang == ResponseLanguage.HINGLISH:
                msg = f"Please '{message}' ke liye details specify karein."

            return ModificationIntent(
                action="ambiguous_request",
                language=detected_lang,
                confirmation_required=True,
                clarification_message=msg,
            )

        # 1. Cheaper / Optimize budget (check BEFORE destination regex to avoid matching "Trip ka budget...")
        if any(kw in text for kw in ["cheaper", "sasta", "kam karo", "kam kar", "optimize budget", "less expensive", "सस्ता", "कम कर"]):
            return ModificationIntent(action="optimize_budget", language=detected_lang)

        # 2. Budget extraction
        budget_match = re.search(r'(?:budget|₹|rs\.?)\s*(?:to|is|be|=|kar do|कर दो)?\s*₹?\s*([\d,]+)', text)
        if not budget_match:
            budget_match = re.search(r'([\d,]+)\s*(?:budget|rupees|rs|inr)', text)

        if budget_match and ("cheaper" not in text and "kam" not in text and "कम" not in text or "to" in text or "kar do" in text or "कर दो" in text):
            val_str = budget_match.group(1).replace(",", "")
            try:
                num = float(val_str)
                if num > 0:
                    return ModificationIntent(action="change_budget", language=detected_lang, new_budget=num)
            except ValueError:
                pass

        # 3. Duration extraction
        duration_match = re.search(r'(\d+)\s*(?:day|days|din|दिन)', text)
        if duration_match:
            try:
                days = int(duration_match.group(1))
                if days > 0:
                    return ModificationIntent(action="change_duration", language=detected_lang, new_duration_days=days)
            except ValueError:
                pass

        # 4. Remove activity / expensive activities
        if "remove expensive" in text or "mehenga hata" in text or "महंगी गतिविधियां हटा" in text or "expensive activities hata" in text:
            return ModificationIntent(action="remove_activity", language=detected_lang, remove_activity_names=["expensive_activities"])
        elif "remove" in text or "hata" in text or "हटा" in text:
            rem_match = re.search(r'(?:remove|hata do|hatao|हटा दो)\s+([a-zA-Z\s\u0900-\u097F]+)', text)
            act_name = rem_match.group(1).strip() if rem_match else "activity"
            return ModificationIntent(action="remove_activity", language=detected_lang, remove_activity_names=[act_name])

        # 5. Destination change
        dest_match = re.search(r'(?:destination|place|go|trip)\s*(?:to|instead|badal ke)?\s*([a-zA-Z\s]+)', text)
        if "jaipur" in text or "जयपुर" in text:
            return ModificationIntent(action="change_destination", language=detected_lang, new_destination="Jaipur")
        elif "goa" in text or "गोवा" in text:
            return ModificationIntent(action="change_destination", language=detected_lang, new_destination="Goa")
        elif "manali" in text or "मनाली" in text:
            return ModificationIntent(action="change_destination", language=detected_lang, new_destination="Manali")
        elif dest_match and "cheaper" not in text and "adventure" not in text:
            dest_name = dest_match.group(1).strip().title()
            if dest_name and dest_name not in ["To", "Cheaper", "More", "Ka Budget", "Ka"]:
                return ModificationIntent(action="change_destination", language=detected_lang, new_destination=dest_name)

        # 6. Preferences
        if "flight" in text or "air" in text or "फ्लाइट" in text:
            return ModificationIntent(action="change_transport_preference", language=detected_lang, requested_transport_preference="flight")
        elif "train" in text or "ट्रेन" in text:
            return ModificationIntent(action="change_transport_preference", language=detected_lang, requested_transport_preference="train")

        if "luxury" in text or "5 star" in text or "resort" in text or "लक्जरी" in text:
            return ModificationIntent(action="change_accommodation_preference", language=detected_lang, requested_accommodation_preference="luxury")
        elif "hostel" in text or "budget hotel" in text or "हॉस्टल" in text:
            return ModificationIntent(action="change_accommodation_preference", language=detected_lang, requested_accommodation_preference="budget")

        adds, removes = [], []
        if "adventure" in text or "एडवेंचर" in text:
            adds.append("adventure")
        if "food" in text or "खाना" in text:
            adds.append("food")
        if "beach" in text or "बीच" in text:
            adds.append("beach")
        if "culture" in text or "संस्कृति" in text:
            adds.append("culture")
        if "sightseeing" in text:
            if "less sightseeing" in text or "no sightseeing" in text:
                removes.append("sightseeing")
            else:
                adds.append("sightseeing")

        if adds or removes:
            return ModificationIntent(
                action="add_preference" if adds else "remove_preference",
                language=detected_lang,
                add_preferences=adds,
                remove_preferences=removes,
            )

        msg = f"I wasn't sure how to modify your trip based on: '{message}'. Could you please rephrase?"
        if detected_lang == ResponseLanguage.HINDI:
            msg = f"मुझे आपके अनुरोध '{message}' को समझने में समस्या हुई। कृपया दोबारा स्पष्ट करें।"
        elif detected_lang == ResponseLanguage.HINGLISH:
            msg = f"Aapka request '{message}' clear nahi tha. Please dobara clarify karein."

        return ModificationIntent(
            action="ambiguous_request",
            language=detected_lang,
            confirmation_required=True,
            clarification_message=msg,
        )
