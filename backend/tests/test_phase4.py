from datetime import date
from fastapi.testclient import TestClient

from app.agents.destination_agent import DestinationAgent
from app.main import app
from app.models.destination import DestinationResults
from app.models.trip import TripRequest
from app.services.providers.destination.base import BaseDestinationProvider

client = TestClient(app)

SAMPLE_TRIP_GOA = TripRequest(
    origin="Indore",
    destination="Goa",
    start_date=date(2026, 10, 10),
    end_date=date(2026, 10, 15),
    budget=30000.0,
    travelers=2,
    preferences=["beach"],
)


def test_destination_agent_goa():
    agent = DestinationAgent()
    results = agent.get_destination_recommendations(SAMPLE_TRIP_GOA)

    assert results.destination == "Goa"
    assert results.supported is True
    assert len(results.recommendations) > 0

    # Verify preference ranking: beach recommendation appears first when 'beach' is in preferences
    first_rec = results.recommendations[0]
    assert any(
        "beach" in tag.lower() for tag in first_rec.best_for
    ) or "beach" in first_rec.name.lower()

    for place in results.recommendations:
        assert len(place.name) > 0
        assert place.estimated_cost_min >= 0
        assert place.estimated_cost_max >= place.estimated_cost_min
        assert place.is_estimate is True


def test_destination_agent_preference_ranking():
    agent = DestinationAgent()

    # Preference: history
    history_trip = TripRequest(
        origin="Indore",
        destination="Goa",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        budget=30000.0,
        travelers=2,
        preferences=["HISTORY"],
    )
    res_history = agent.get_destination_recommendations(history_trip)
    assert res_history.supported is True
    top_history = res_history.recommendations[0]
    assert "history" in [t.lower() for t in top_history.best_for] or "culture" in top_history.category.lower()

    # Preference: adventure
    adventure_trip = TripRequest(
        origin="Indore",
        destination="Goa",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        budget=30000.0,
        travelers=2,
        preferences=["adventure"],
    )
    res_adventure = agent.get_destination_recommendations(adventure_trip)
    assert res_adventure.supported is True
    top_adventure = res_adventure.recommendations[0]
    assert "adventure" in [t.lower() for t in top_adventure.best_for] or "adventure" in top_adventure.category.lower()


def test_unsupported_destination_handling():
    agent = DestinationAgent()
    unsupported_trip = TripRequest(
        origin="Indore",
        destination="Antarctica",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        budget=30000.0,
        travelers=2,
    )
    results = agent.get_destination_recommendations(unsupported_trip)
    assert results.supported is False
    assert "currently unavailable" in results.message
    assert len(results.recommendations) == 0


def test_destination_dependency_injection():
    class CustomDestinationProvider(BaseDestinationProvider):
        def get_destination_recommendations(
            self, request: TripRequest
        ) -> DestinationResults:
            return DestinationResults(
                destination=request.destination,
                supported=True,
                recommendations=[],
            )

    custom_agent = DestinationAgent(provider=CustomDestinationProvider())
    custom_res = custom_agent.get_destination_recommendations(SAMPLE_TRIP_GOA)
    assert custom_res.recommendations == []


def test_api_destinations_endpoint_english():
    response = client.post(
        "/api/trips/destinations",
        json={
            "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["destination"]["destination"] == "Goa"
    assert data["destination"]["supported"] is True
    assert len(data["destination"]["recommendations"]) > 0


def test_api_destinations_endpoint_hinglish():
    response = client.post(
        "/api/trips/destinations",
        json={
            "message": "Mujhe Indore se Goa jana hai 10 October se 15 October tak, budget 30k hai aur 2 log hain."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["destination"]["destination"] == "Goa"


def test_api_destinations_endpoint_missing_destination():
    response = client.post(
        "/api/trips/destinations",
        json={
            "message": "I want to travel from October 10 to October 15 with a budget of 30000 for 2 people."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "needs_information"
    assert "destination" in data["missing"]


def test_phase1_2_3_regression():
    # Phase 1
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200

    # Phase 2
    res2 = client.post(
        "/api/trips/parse",
        json={
            "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
        },
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "success"

    # Phase 3
    res3 = client.post(
        "/api/trips/options",
        json={
            "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
        },
    )
    assert res3.status_code == 200
    assert res3.json()["status"] == "success"
