from datetime import date
from fastapi.testclient import TestClient

from app.agents.accommodation_agent import AccommodationAgent
from app.agents.budget_agent import (
    DEFAULT_FOOD_RATE_MAX,
    DEFAULT_FOOD_RATE_MIN,
    BudgetAgent,
)
from app.agents.destination_agent import DestinationAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.transport_agent import TransportAgent
from app.main import app
from app.models.trip import TripRequest

client = TestClient(app)
planner = PlannerAgent()
transport_agent = TransportAgent()
accommodation_agent = AccommodationAgent()
destination_agent = DestinationAgent()
budget_agent = BudgetAgent()

SAMPLE_TRIP = TripRequest(
    origin="Indore",
    destination="Goa",
    start_date=date(2026, 10, 10),
    end_date=date(2026, 10, 15),
    budget=30000.0,
    travelers=2,
    preferences=["beach"],
)


def test_accommodation_consumed_directly_without_traveler_multiplication():
    # 2 travelers vs 1 traveler trip request
    trip_2 = TripRequest(
        origin="Indore",
        destination="Goa",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        budget=50000.0,
        travelers=2,
    )
    trip_1 = TripRequest(
        origin="Indore",
        destination="Goa",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        budget=50000.0,
        travelers=1,
    )

    t_res = transport_agent.get_transport_options(trip_2)
    a_res = accommodation_agent.get_accommodation_options(trip_2, 5)
    d_res = destination_agent.get_destination_recommendations(trip_2)

    b_res_2 = budget_agent.calculate_budget(trip_2, t_res, a_res, d_res)
    b_res_1 = budget_agent.calculate_budget(trip_1, t_res, a_res, d_res)

    # Accommodation cost must remain identical for 1 vs 2 travelers (single room/unit assumption)
    assert (
        b_res_2.breakdown.accommodation_min
        == b_res_1.breakdown.accommodation_min
    )
    assert (
        b_res_2.breakdown.accommodation_max
        == b_res_1.breakdown.accommodation_max
    )

    # Transport cost must double for 2 travelers compared to 1 traveler
    assert (
        b_res_2.breakdown.transport_min == b_res_1.breakdown.transport_min * 2
    )


def test_activity_subset_calculation():
    t_res = transport_agent.get_transport_options(SAMPLE_TRIP)
    a_res = accommodation_agent.get_accommodation_options(SAMPLE_TRIP, 5)
    d_res = destination_agent.get_destination_recommendations(SAMPLE_TRIP)

    b_res = budget_agent.calculate_budget(SAMPLE_TRIP, t_res, a_res, d_res)

    # Total recommendations count in d_res is 9
    assert len(d_res.recommendations) > 3

    # Activity calculation should only sum top 3 recommendations × travelers (2)
    top_3 = d_res.recommendations[:3]
    expected_min = sum(p.estimated_cost_min for p in top_3) * 2
    expected_max = sum(p.estimated_cost_max for p in top_3) * 2

    assert b_res.breakdown.activities_min == expected_min
    assert b_res.breakdown.activities_max == expected_max


def test_budget_delta_and_classification_semantics():
    t_res = transport_agent.get_transport_options(SAMPLE_TRIP)
    a_res = accommodation_agent.get_accommodation_options(SAMPLE_TRIP, 5)
    d_res = destination_agent.get_destination_recommendations(SAMPLE_TRIP)

    # Test high budget -> within_budget
    high_trip = TripRequest(
        origin="Indore",
        destination="Goa",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        budget=100000.0,
        travelers=2,
    )
    res_high = budget_agent.calculate_budget(high_trip, t_res, a_res, d_res)
    assert res_high.budget_status == "within_budget"
    assert res_high.remaining_min > 0
    assert res_high.remaining_max > 0

    # Test low budget -> over_budget
    low_trip = TripRequest(
        origin="Indore",
        destination="Goa",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        budget=5000.0,
        travelers=2,
    )
    res_low = budget_agent.calculate_budget(low_trip, t_res, a_res, d_res)
    assert res_low.budget_status == "over_budget"
    assert res_low.remaining_min < 0
    assert res_low.remaining_max < 0

    # Test mid budget -> near_budget (range crossing zero)
    mid_budget = (
        res_high.breakdown.total_min + res_high.breakdown.total_max
    ) / 2.0
    mid_trip = TripRequest(
        origin="Indore",
        destination="Goa",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        budget=mid_budget,
        travelers=2,
    )
    res_mid = budget_agent.calculate_budget(mid_trip, t_res, a_res, d_res)
    assert res_mid.budget_status == "near_budget"
    assert res_mid.remaining_min < 0 < res_mid.remaining_max


def test_optimization_recommendations_from_actual_options():
    t_res = transport_agent.get_transport_options(SAMPLE_TRIP)
    a_res = accommodation_agent.get_accommodation_options(SAMPLE_TRIP, 5)
    d_res = destination_agent.get_destination_recommendations(SAMPLE_TRIP)

    res = budget_agent.calculate_budget(SAMPLE_TRIP, t_res, a_res, d_res)
    assert len(res.recommendations) > 0
    # Should recommend train (cheaper than default train/flight) or budget accommodation
    rec_text = " ".join(res.recommendations).lower()
    assert "train" in rec_text or "budget" in rec_text


def test_deterministic_repeatability():
    t_res = transport_agent.get_transport_options(SAMPLE_TRIP)
    a_res = accommodation_agent.get_accommodation_options(SAMPLE_TRIP, 5)
    d_res = destination_agent.get_destination_recommendations(SAMPLE_TRIP)

    res1 = budget_agent.calculate_budget(SAMPLE_TRIP, t_res, a_res, d_res)
    res2 = budget_agent.calculate_budget(SAMPLE_TRIP, t_res, a_res, d_res)
    assert res1.model_dump() == res2.model_dump()


def test_api_budget_endpoint_valid_english():
    response = client.post(
        "/api/trips/budget",
        json={
            "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "budget" in data
    assert data["budget"]["budget"] == 30000.0
    assert data["budget"]["is_estimate"] is True
    assert "breakdown" in data["budget"]


def test_api_budget_endpoint_hinglish():
    response = client.post(
        "/api/trips/budget",
        json={
            "message": "Mujhe Indore se Goa jana hai 10 October se 15 October tak, budget 30k hai aur 2 log hain."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["budget"]["budget"] == 30000.0


def test_phase1_to_4_regression():
    # Phase 1
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200

    # Phase 2
    assert (
        client.post(
            "/api/trips/parse",
            json={
                "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
            },
        ).status_code
        == 200
    )

    # Phase 3
    assert (
        client.post(
            "/api/trips/options",
            json={
                "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
            },
        ).status_code
        == 200
    )

    # Phase 4
    assert (
        client.post(
            "/api/trips/destinations",
            json={
                "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
            },
        ).status_code
        == 200
    )
