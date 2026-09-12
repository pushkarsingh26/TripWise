from datetime import date
from fastapi.testclient import TestClient

from app.agents.accommodation_agent import AccommodationAgent
from app.agents.transport_agent import TransportAgent
from app.main import app
from app.models.accommodation import AccommodationResults
from app.models.transport import TransportResults
from app.models.trip import TripRequest
from app.services.providers.accommodation.base import (
    BaseAccommodationProvider,
)
from app.services.providers.transport.base import BaseTransportProvider

client = TestClient(app)

SAMPLE_TRIP = TripRequest(
    origin="Indore",
    destination="Goa",
    start_date=date(2026, 10, 10),
    end_date=date(2026, 10, 15),
    budget=30000.0,
    travelers=2,
    preferences=["beach"],
)


def test_transport_agent():
    agent = TransportAgent()
    results = agent.get_transport_options(SAMPLE_TRIP)

    assert results.origin == "Indore"
    assert results.destination == "Goa"
    assert len(results.options) == 3

    modes = {opt.mode for opt in results.options}
    assert "flight" in modes
    assert "train" in modes
    assert "bus" in modes

    for opt in results.options:
        assert opt.estimated_cost_min > 0
        assert opt.estimated_cost_max >= opt.estimated_cost_min
        assert opt.is_estimate is True


def test_accommodation_agent():
    agent = AccommodationAgent()
    nights = 5
    results = agent.get_accommodation_options(SAMPLE_TRIP, duration_nights=nights)

    assert results.destination == "Goa"
    assert results.nights == 5
    assert len(results.options) == 3

    categories = {opt.category for opt in results.options}
    assert "budget" in categories
    assert "mid_range" in categories
    assert "premium" in categories

    for opt in results.options:
        assert opt.is_estimate is True
        # Verify strict Python arithmetic formula: estimated_total = nightly_rate * nights
        assert opt.estimated_total_min == opt.estimated_price_per_night_min * nights
        assert opt.estimated_total_max == opt.estimated_price_per_night_max * nights


def test_provider_dependency_injection():
    # Test that TransportAgent accepts custom provider implementing BaseTransportProvider
    class CustomTransportProvider(BaseTransportProvider):
        def get_transport_options(self, request: TripRequest) -> TransportResults:
            return TransportResults(
                origin=request.origin,
                destination=request.destination,
                options=[],
            )

    custom_transport_agent = TransportAgent(provider=CustomTransportProvider())
    custom_t_res = custom_transport_agent.get_transport_options(SAMPLE_TRIP)
    assert custom_t_res.options == []

    # Test that AccommodationAgent accepts custom provider implementing BaseAccommodationProvider
    class CustomAccommodationProvider(BaseAccommodationProvider):
        def get_accommodation_options(
            self, request: TripRequest, duration_nights: int
        ) -> AccommodationResults:
            return AccommodationResults(
                destination=request.destination,
                check_in=str(request.start_date),
                check_out=str(request.end_date),
                nights=duration_nights,
                options=[],
            )

    custom_acc_agent = AccommodationAgent(provider=CustomAccommodationProvider())
    custom_a_res = custom_acc_agent.get_accommodation_options(SAMPLE_TRIP, 3)
    assert custom_a_res.options == []


def test_api_options_endpoint_valid_english():
    response = client.post(
        "/api/trips/options",
        json={
            "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["trip"]["origin"] == "Indore"
    assert data["trip"]["destination"] == "Goa"
    assert data["duration_days"] == 6
    assert data["duration_nights"] == 5

    # Check transport results
    assert "transport" in data
    assert len(data["transport"]["options"]) == 3

    # Check accommodation results
    assert "accommodation" in data
    assert len(data["accommodation"]["options"]) == 3


def test_api_options_endpoint_valid_hinglish():
    response = client.post(
        "/api/trips/options",
        json={
            "message": "Mujhe Indore se Goa jana hai 10 October se 15 October tak, budget 30k hai aur 2 log hain."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["trip"]["origin"] == "Indore"
    assert data["trip"]["destination"] == "Goa"


def test_api_options_endpoint_missing_budget():
    response = client.post(
        "/api/trips/options",
        json={
            "message": "I want to travel from Indore to Goa from October 10 to October 15 for 2 people."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "needs_information"
    assert "budget" in data["missing"]


def test_phase1_and_phase2_regression():
    # Phase 1 endpoints
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/docs").status_code == 200

    # Phase 2 endpoint
    res2 = client.post(
        "/api/trips/parse",
        json={
            "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
        },
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "success"
