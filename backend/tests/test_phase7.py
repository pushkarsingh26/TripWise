from datetime import date
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.modification import ModificationIntent
from app.models.trip import TripRequest
from app.services.llm.base import BaseLLMProvider
from app.services.llm.provider import (
    LLMConfigurationError,
    LLMExecutionError,
    LLMProvider,
)
from app.services.trip_modifier import TripModifier


class DummyMockLLMProvider(BaseLLMProvider):
    """Mock provider for deterministic testing."""

    def __init__(self, mock_intent: ModificationIntent):
        self.mock_intent = mock_intent

    def interpret_modification(self, message: str, current_trip=None) -> ModificationIntent:
        return self.mock_intent


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


def test_llm_provider_unconfigured():
    provider = LLMProvider(provider="gemini", api_key="", allow_rule_fallback=False)
    assert not provider.is_configured()

    with pytest.raises(LLMConfigurationError):
        provider.interpret_modification("Make it cheaper")


def test_llm_provider_rule_fallback(base_trip_dict):
    provider = LLMProvider(provider="gemini", api_key="", allow_rule_fallback=True)
    assert provider.is_configured()

    # English budget change
    intent = provider.interpret_modification("Increase budget to 40000", base_trip_dict)
    assert intent.action == "change_budget"
    assert intent.new_budget == 40000.0

    # Hinglish duration change
    intent_hinglish = provider.interpret_modification("Trip 4 din ki kar do", base_trip_dict)
    assert intent_hinglish.action == "change_duration"
    assert intent_hinglish.new_duration_days == 4

    # Hinglish budget optimization
    intent_opt = provider.interpret_modification("Budget thoda kam karo", base_trip_dict)
    assert intent_opt.action == "optimize_budget"


def test_pydantic_modification_intent():
    intent = ModificationIntent(
        action="change_budget",
        new_budget=45000.0,
    )
    assert intent.action == "change_budget"
    assert intent.new_budget == 45000.0
    assert intent.confirmation_required is False


def test_trip_modifier_budget_change(base_trip_dict):
    modifier = TripModifier()
    intent = ModificationIntent(action="change_budget", new_budget=40000.0)

    res = modifier.modify_trip(base_trip_dict, intent)
    assert res["status"] == "success"
    assert res["trip"]["budget"] == 40000.0
    assert "40,000" in res["message"]
    assert res["plan"]["budget"] is not None


def test_trip_modifier_duration_change(base_trip_dict):
    modifier = TripModifier()
    intent = ModificationIntent(action="change_duration", new_duration_days=4)

    res = modifier.modify_trip(base_trip_dict, intent)
    assert res["status"] == "success"
    assert res["plan"]["duration_days"] == 4
    assert res["trip"]["start_date"] == "2026-10-10"
    assert res["trip"]["end_date"] == "2026-10-13"


def test_trip_modifier_destination_change(base_trip_dict):
    modifier = TripModifier()
    intent = ModificationIntent(action="change_destination", new_destination="Jaipur")

    res = modifier.modify_trip(base_trip_dict, intent)
    assert res["status"] == "success"
    assert res["trip"]["destination"] == "Jaipur"
    assert res["plan"]["itinerary"]["destination"] == "Jaipur"


def test_trip_modifier_add_preference(base_trip_dict):
    modifier = TripModifier()
    intent = ModificationIntent(action="add_preference", add_preferences=["adventure"])

    res = modifier.modify_trip(base_trip_dict, intent)
    assert res["status"] == "success"
    assert "adventure" in res["trip"]["preferences"]


def test_trip_modifier_ambiguous_request(base_trip_dict):
    modifier = TripModifier()
    intent = ModificationIntent(
        action="ambiguous_request",
        confirmation_required=True,
        clarification_message="Please specify hotel preferences.",
    )

    res = modifier.modify_trip(base_trip_dict, intent)
    assert res["status"] == "needs_clarification"
    assert res["plan"] is None
    assert "specify hotel" in res["message"]


def test_api_modify_endpoint_unconfigured(monkeypatch, base_trip_dict):
    # Ensure LLM_API_KEY is empty
    monkeypatch.setenv("LLM_API_KEY", "")
    client = TestClient(app)

    resp = client.post(
        "/api/trips/modify",
        json={
            "message": "Make this trip cheaper",
            "trip": base_trip_dict,
        },
    )
    assert resp.status_code == 503
    assert "requires an LLM provider configuration" in resp.json()["detail"]


def test_api_modify_endpoint_rule_fallback(monkeypatch, base_trip_dict):
    # Enable rule fallback for testing the endpoint logic
    monkeypatch.setattr(
        "app.api.trips.LLMProvider",
        lambda: LLMProvider(provider="gemini", api_key="", allow_rule_fallback=True),
    )
    client = TestClient(app)

    # Test valid budget modification
    resp = client.post(
        "/api/trips/modify",
        json={
            "message": "Increase budget to 50000",
            "trip": base_trip_dict,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["trip"]["budget"] == 50000.0
    assert data["plan"]["itinerary"] is not None

    # Test Hinglish duration modification
    resp_hinglish = client.post(
        "/api/trips/modify",
        json={
            "message": "Trip 4 din ki kar do",
            "trip": base_trip_dict,
        },
    )
    assert resp_hinglish.status_code == 200
    data_h = resp_hinglish.json()
    assert data_h["status"] == "success"
    assert data_h["plan"]["duration_days"] == 4

    # Test ambiguous request requiring clarification
    resp_amb = client.post(
        "/api/trips/modify",
        json={
            "message": "change hotel",
            "trip": base_trip_dict,
        },
    )
    assert resp_amb.status_code == 200
    data_amb = resp_amb.json()
    assert data_amb["status"] == "needs_clarification"
