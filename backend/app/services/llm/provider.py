import json
import os
import re
from typing import Any, Dict, Optional
import httpx

from app.models.modification import ModificationAction, ModificationIntent
from app.services.llm.base import BaseLLMProvider


class LLMConfigurationError(Exception):
    """Raised when LLM provider is not configured or API key is missing."""
    pass


class LLMExecutionError(Exception):
    """Raised when LLM provider call or response parsing fails."""
    pass


SYSTEM_PROMPT = """You are a natural language intent parser for a travel planning system named Tripwise.
Your ONLY task is to parse the user's trip modification request and extract structured modification intent into strict JSON format matching the schema below.

CRITICAL INSTRUCTIONS:
1. You MUST return ONLY valid JSON with no extra commentary, preambles, code fences, markdown, or explanations.
2. DO NOT calculate costs, prices, or budgets.
3. DO NOT generate an itinerary or invent places.
4. If the request is ambiguous (e.g., "change hotel" without specifying budget or style, or vague modification), set "action": "ambiguous_request", "confirmation_required": true, and provide a clear question in "clarification_message".

Allowed Actions:
- "change_budget": User explicitly wants to set a specific budget amount (e.g. "Increase budget to 40000", "Make budget 25000", "Budget 30000 kar do"). Set "new_budget" (numeric).
- "change_duration": User wants to change total days (e.g. "Make this a 4 day trip", "Trip 5 din ki kar do"). Set "new_duration_days" (integer).
- "change_destination": User wants to change destination (e.g. "Change destination to Jaipur", "Go to Goa instead"). Set "new_destination" (string).
- "add_preference": User wants to add preferences/interests (e.g. "I want more adventure", "Add food experiences", "Beach activities badhao"). Set "add_preferences" (list of strings).
- "remove_preference": User wants to remove preferences (e.g. "Less sightseeing", "No shopping"). Set "remove_preferences" (list of strings).
- "remove_activity": User wants to remove specific activities or expensive activities (e.g. "Remove expensive activities", "Remove scuba diving"). Set "remove_activity_names" (list of strings).
- "change_transport_preference": User wants to change transport (e.g. "Use flight instead", "Prefer train"). Set "requested_transport_preference" (string).
- "change_accommodation_preference": User wants to change accommodation (e.g. "Stay in luxury hotel", "Prefer hostel"). Set "requested_accommodation_preference" (string).
- "optimize_budget": User asks to make trip cheaper or budget-friendly without giving an exact number (e.g. "Make this trip cheaper", "Budget thoda kam karo").
- "regenerate_itinerary": User asks to reshuffle or regenerate plan without changes.
- "ambiguous_request": User request is unclear or missing key parameters.

OUTPUT FORMAT (JSON ONLY):
{
  "action": "<action_string>",
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
    Provider-agnostic LLM client supporting Gemini, Groq, and OpenAI compatible free endpoints.
    Fail-safe when unconfigured, strict JSON parsing with Pydantic validation.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        allow_rule_fallback: bool = False,
    ):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower()
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "gemini-1.5-flash")
        self.allow_rule_fallback = allow_rule_fallback

    def is_configured(self) -> bool:
        """Returns True if API key and provider are set, or if rule fallback is enabled."""
        return bool(self.api_key and self.api_key.strip()) or self.allow_rule_fallback

    def interpret_modification(
        self,
        message: str,
        current_trip: Optional[Dict[str, Any]] = None,
    ) -> ModificationIntent:
        """
        Interprets user natural-language modification request.
        """
        if not message or not message.strip():
            return ModificationIntent(
                action="ambiguous_request",
                confirmation_required=True,
                clarification_message="Please provide a message specifying what you would like to change.",
            )

        if not self.is_configured():
            raise LLMConfigurationError(
                "Conversational trip modification requires an LLM provider configuration. "
                "Please set LLM_API_KEY in environment variables."
            )

        # If rule fallback enabled and no API key present, use rule-based intent parser
        if self.allow_rule_fallback and not (self.api_key and self.api_key.strip()):
            return self._parse_rule_based(message, current_trip)

        try:
            raw_response = self._call_llm_api(message, current_trip)
            intent = self._parse_and_validate_json(raw_response)
            return intent
        except LLMExecutionError:
            raise
        except Exception as e:
            if self.allow_rule_fallback:
                return self._parse_rule_based(message, current_trip)
            raise LLMExecutionError(f"Failed to interpret modification: {str(e)}")

    def _call_llm_api(self, message: str, current_trip: Optional[Dict[str, Any]] = None) -> str:
        """Invokes external LLM HTTP REST endpoint."""
        prompt = f"{SYSTEM_PROMPT}\n\nUser Current Trip: {json.dumps(current_trip or {})}\nUser Modification Request: \"{message}\"\nJSON Intent:"

        if self.provider == "gemini":
            return self._call_gemini_api(prompt)
        elif self.provider in ("groq", "openai"):
            return self._call_openai_compatible_api(prompt)
        else:
            # Fallback to OpenAI compatible format for generic providers
            return self._call_openai_compatible_api(prompt)

    def _call_gemini_api(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1,
            },
        }

        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                raise LLMExecutionError(f"Gemini API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
            except (KeyError, IndexError) as err:
                raise LLMExecutionError(f"Malformed Gemini API response: {data}") from err

    def _call_openai_compatible_api(self, prompt: str) -> str:
        if self.provider == "groq":
            endpoint = "https://api.groq.com/openai/v1/chat/completions"
            model_name = self.model or "llama-3.3-70b-versatile"
        else:
            endpoint = os.getenv("LLM_ENDPOINT", "https://api.openai.com/v1/chat/completions")
            model_name = self.model or "gpt-4o-mini"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        with httpx.Client(timeout=15.0) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
            if resp.status_code != 200:
                raise LLMExecutionError(f"LLM Provider API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            try:
                text = data["choices"][0]["message"]["content"]
                return text
            except (KeyError, IndexError) as err:
                raise LLMExecutionError(f"Malformed LLM API response: {data}") from err

    def _parse_and_validate_json(self, raw_text: str) -> ModificationIntent:
        """Parses raw text into JSON and validates against ModificationIntent Pydantic model."""
        cleaned = raw_text.strip()
        # Remove potential markdown code blocks
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

    def _parse_rule_based(
        self,
        message: str,
        current_trip: Optional[Dict[str, Any]] = None,
    ) -> ModificationIntent:
        """
        Rule-based parser for fallback/testing when API key is missing or testing offline.
        Supports English and Hinglish patterns.
        """
        text = message.lower().strip()

        # Check ambiguous requests first
        if text in ["change hotel", "change transport", "change accommodation", "badlo"]:
            return ModificationIntent(
                action="ambiguous_request",
                confirmation_required=True,
                clarification_message=f"Could you please specify details for '{message}'?",
            )

        # Budget extraction (e.g. "budget to 40000", "40,000", "budget 30000 kar do")
        budget_match = re.search(r'(?:budget|₹|rs\.?)\s*(?:to|is|be|=|kar do)?\s*₹?\s*([\d,]+)', text)
        if not budget_match:
            budget_match = re.search(r'([\d,]+)\s*(?:budget|rupees|rs|inr)', text)

        if budget_match and ("cheaper" not in text and "kam" not in text or "to" in text or "kar do" in text):
            val_str = budget_match.group(1).replace(",", "")
            try:
                num = float(val_str)
                if num > 0:
                    return ModificationIntent(
                        action="change_budget",
                        new_budget=num,
                    )
            except ValueError:
                pass

        # Duration extraction (e.g. "4 day trip", "make it 5 days", "3 din ki kar do")
        duration_match = re.search(r'(\d+)\s*(?:day|days|din)', text)
        if duration_match:
            try:
                days = int(duration_match.group(1))
                if days > 0:
                    return ModificationIntent(
                        action="change_duration",
                        new_duration_days=days,
                    )
            except ValueError:
                pass

        # Destination change (e.g. "change destination to Jaipur", "go to Goa instead")
        dest_match = re.search(r'(?:destination|place|go|trip)\s*(?:to|instead|badal ke)?\s*([a-zA-Z\s]+)', text)
        if "jaipur" in text:
            return ModificationIntent(action="change_destination", new_destination="Jaipur")
        elif "goa" in text:
            return ModificationIntent(action="change_destination", new_destination="Goa")
        elif "manali" in text:
            return ModificationIntent(action="change_destination", new_destination="Manali")
        elif dest_match and "cheaper" not in text and "adventure" not in text:
            dest_name = dest_match.group(1).strip().title()
            if dest_name and dest_name not in ["To", "Cheaper", "More"]:
                return ModificationIntent(action="change_destination", new_destination=dest_name)

        # Cheaper / Optimize budget (e.g. "make this trip cheaper", "remove expensive activities", "budget thoda kam karo")
        if any(kw in text for kw in ["cheaper", "sasta", "kam karo", "optimize budget", "less expensive"]):
            return ModificationIntent(action="optimize_budget")

        # Transport preference
        if "flight" in text or "air" in text:
            return ModificationIntent(action="change_transport_preference", requested_transport_preference="flight")
        elif "train" in text:
            return ModificationIntent(action="change_transport_preference", requested_transport_preference="train")

        # Accommodation preference
        if "luxury" in text or "5 star" in text or "resort" in text:
            return ModificationIntent(action="change_accommodation_preference", requested_accommodation_preference="luxury")
        elif "hostel" in text or "budget hotel" in text:
            return ModificationIntent(action="change_accommodation_preference", requested_accommodation_preference="budget")

        # Remove activity
        if "remove expensive" in text or "mehenga hata do" in text:
            return ModificationIntent(action="remove_activity", remove_activity_names=["expensive_activities"])
        elif "remove" in text or "hata do" in text:
            rem_match = re.search(r'(?:remove|hata do)\s+([a-zA-Z\s]+)', text)
            act_name = rem_match.group(1).strip() if rem_match else "activity"
            return ModificationIntent(action="remove_activity", remove_activity_names=[act_name])

        # Preferences (adventure, food, sightseeing, beach, culture)
        adds = []
        removes = []
        if "adventure" in text:
            adds.append("adventure")
        if "food" in text:
            adds.append("food")
        if "beach" in text:
            adds.append("beach")
        if "culture" in text:
            adds.append("culture")
        if "sightseeing" in text:
            if "less sightseeing" in text or "no sightseeing" in text:
                removes.append("sightseeing")
            else:
                adds.append("sightseeing")

        if adds or removes:
            return ModificationIntent(
                action="add_preference" if adds else "remove_preference",
                add_preferences=adds,
                remove_preferences=removes,
            )

        # Default fallback
        return ModificationIntent(
            action="ambiguous_request",
            confirmation_required=True,
            clarification_message=f"I wasn't sure how to modify your trip based on: '{message}'. Could you please rephrase?",
        )
