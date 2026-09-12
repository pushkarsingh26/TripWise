import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.language import ResponseLanguage
from app.models.modification import ModificationIntent
from app.services.llm.base import BaseLLMProvider
from app.services.llm.provider import LLMConfigurationError, LLMProvider
from app.services.trip_modifier import TripModifier
from app.services.trip_parser import TripParser


@pytest.fixture
def base_trip_dict():
    return {
        "origin": "Indore",
        "destination": "Goa",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15",
        "budget": 30000.0,
        "travelers": 2,
        "preferences": ["beaches", "food"],
    }


def test_response_language_model_validation():
    intent_en = ModificationIntent(action="optimize_budget", language="english")
    assert intent_en.language == ResponseLanguage.ENGLISH

    intent_hi = ModificationIntent(action="optimize_budget", language="hindi")
    assert intent_hi.language == ResponseLanguage.HINDI

    intent_hing = ModificationIntent(action="optimize_budget", language="hinglish")
    assert intent_hing.language == ResponseLanguage.HINGLISH

    # Fallback to English on unsupported language string
    intent_unsupported = ModificationIntent(action="optimize_budget", language="spanish")
    assert intent_unsupported.language == ResponseLanguage.ENGLISH


def test_rule_based_language_detection(base_trip_dict):
    provider = LLMProvider(provider="gemini", api_key="", allow_rule_fallback=True)

    # English
    intent_en = provider.interpret_modification("Make my trip cheaper", base_trip_dict)
    assert intent_en.language == ResponseLanguage.ENGLISH
    assert intent_en.action == "optimize_budget"

    # Hindi
    intent_hi = provider.interpret_modification("मेरा ट्रिप सस्ता कर दो", base_trip_dict)
    assert intent_hi.language == ResponseLanguage.HINDI
    assert intent_hi.action == "optimize_budget"

    # Hinglish
    intent_hing = provider.interpret_modification("Trip ka budget kam kar do", base_trip_dict)
    assert intent_hing.language == ResponseLanguage.HINGLISH
    assert intent_hing.action == "optimize_budget"


def test_multilingual_activity_requests(base_trip_dict):
    provider = LLMProvider(provider="gemini", api_key="", allow_rule_fallback=True)

    # English activity request
    intent_en = provider.interpret_modification("Remove expensive activities", base_trip_dict)
    assert intent_en.language == ResponseLanguage.ENGLISH
    assert intent_en.action == "remove_activity"

    # Hindi activity request
    intent_hi = provider.interpret_modification("महंगी गतिविधियां हटा दो", base_trip_dict)
    assert intent_hi.language == ResponseLanguage.HINDI
    assert intent_hi.action == "remove_activity"

    # Hinglish activity request
    intent_hing = provider.interpret_modification("Expensive activities hatao aur thodi adventure activities add karo", base_trip_dict)
    assert intent_hing.language == ResponseLanguage.HINGLISH
    assert intent_hing.action == "remove_activity" or intent_hing.action == "add_preference"


def test_trip_modifier_multilingual_responses(base_trip_dict):
    modifier = TripModifier()

    # English response
    intent_en = ModificationIntent(action="change_budget", language=ResponseLanguage.ENGLISH, new_budget=40000.0)
    res_en = modifier.modify_trip(base_trip_dict, intent_en)
    assert res_en["status"] == "success"
    assert "Updated total trip budget" in res_en["message"]

    # Hindi response
    intent_hi = ModificationIntent(action="change_budget", language=ResponseLanguage.HINDI, new_budget=40000.0)
    res_hi = modifier.modify_trip(base_trip_dict, intent_hi)
    assert res_hi["status"] == "success"
    assert "बजट बदलकर" in res_hi["message"]

    # Hinglish response
    intent_hing = ModificationIntent(action="change_budget", language=ResponseLanguage.HINGLISH, new_budget=40000.0)
    res_hing = modifier.modify_trip(base_trip_dict, intent_hing)
    assert res_hing["status"] == "success"
    assert "Trip ka total budget update karke" in res_hing["message"]


def test_api_modify_endpoint_multilingual(monkeypatch, base_trip_dict):
    monkeypatch.setattr(
        "app.api.trips.LLMProvider",
        lambda: LLMProvider(provider="gemini", api_key="", allow_rule_fallback=True),
    )
    client = TestClient(app)

    # Hinglish request
    resp_hing = client.post(
        "/api/trips/modify",
        json={
            "message": "Trip 4 din ki kar do",
            "trip": base_trip_dict,
        },
    )
    assert resp_hing.status_code == 200
    data_hing = resp_hing.json()
    assert data_hing["status"] == "success"
    assert data_hing["intent"]["language"] == "hinglish"
    assert "Trip duration update karke" in data_hing["message"]

    # Hindi request
    resp_hi = client.post(
        "/api/trips/modify",
        json={
            "message": "मेरा ट्रिप सस्ता कर दो",
            "trip": base_trip_dict,
        },
    )
    assert resp_hi.status_code == 200
    data_hi = resp_hi.json()
    assert data_hi["status"] == "success"
    assert data_hi["intent"]["language"] == "hindi"
    assert "बजट कम करके" in data_hi["message"]


def test_trip_parser_multilingual_inputs():
    parser = TripParser()

    # English input
    res_en = parser.parse("Plan a trip from Indore to Goa for 5 days with a budget of 30000")
    assert res_en["origin"] == "Indore"
    assert res_en["destination"] == "Goa"
    assert res_en["budget"] == 30000.0

    # Hinglish input
    res_hing = parser.parse("Indore se Goa 5 din ka trip plan karo budget 30000 hai")
    assert res_hing["origin"] == "Indore"
    assert res_hing["destination"] == "Goa"
    assert res_hing["budget"] == 30000.0

    # Hindi Devanagari input
    res_hi = parser.parse("इंदौर से गोवा 5 दिन का ट्रिप प्लान करो, बजट 30000 है")
    assert res_hi["origin"] == "इंदौर"
    assert res_hi["destination"] == "गोवा"
    assert res_hi["budget"] == 30000.0
