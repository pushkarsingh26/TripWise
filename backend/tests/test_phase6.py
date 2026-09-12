from datetime import date
from fastapi.testclient import TestClient

from app.agents.accommodation_agent import AccommodationAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.destination_agent import DestinationAgent
from app.agents.itinerary_agent import ItineraryAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.transport_agent import TransportAgent
from app.main import app
from app.models.trip import TripRequest
from app.workflows.trip_workflow import run_trip_workflow

client = TestClient(app)

SAMPLE_TRIP_MULTIDAY = TripRequest(
    origin="Indore",
    destination="Goa",
    start_date=date(2026, 10, 10),
    end_date=date(2026, 10, 15),
    budget=30000.0,
    travelers=2,
    preferences=["beach"],
)

SAMPLE_TRIP_SAMEDAY = TripRequest(
    origin="Indore",
    destination="Goa",
    start_date=date(2026, 10, 10),
    end_date=date(2026, 10, 10),
    budget=15000.0,
    travelers=1,
)


def test_itinerary_agent_multiday():
    dest_res = DestinationAgent().get_destination_recommendations(
        SAMPLE_TRIP_MULTIDAY
    )
    b_res = BudgetAgent().calculate_budget(
        SAMPLE_TRIP_MULTIDAY,
        TransportAgent().get_transport_options(SAMPLE_TRIP_MULTIDAY),
        AccommodationAgent().get_accommodation_options(
            SAMPLE_TRIP_MULTIDAY, 5
        ),
        dest_res,
    )

    agent = ItineraryAgent()
    res = agent.generate_itinerary(SAMPLE_TRIP_MULTIDAY, dest_res, b_res)

    assert res.destination == "Goa"
    assert res.duration_days == 6
    assert len(res.days) == 6
    assert res.is_estimate is True

    # Verify chronological dates
    assert res.days[0].date == "2026-10-10"
    assert res.days[-1].date == "2026-10-15"

    # Verify non-overlapping times and durations
    for day in res.days:
        last_end = 0
        for act in day.activities:
            assert len(act.start_time) == 5
            assert len(act.end_time) == 5
            # Convert start_time HH:MM to minutes
            sh, sm = map(int, act.start_time.split(":"))
            eh, em = map(int, act.end_time.split(":"))
            start_m = sh * 60 + sm
            end_m = eh * 60 + em

            assert start_m >= last_end
            assert end_m > start_m
            last_end = end_m


def test_itinerary_agent_sameday():
    dest_res = DestinationAgent().get_destination_recommendations(
        SAMPLE_TRIP_SAMEDAY
    )

    agent = ItineraryAgent()
    res = agent.generate_itinerary(SAMPLE_TRIP_SAMEDAY, dest_res)

    assert res.duration_days == 1
    assert len(res.days) == 1
    assert res.days[0].date == "2026-10-10"


def test_itinerary_budget_sensitivity():
    # Over budget trip
    over_trip = TripRequest(
        origin="Indore",
        destination="Goa",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
        budget=2000.0,  # Extremely low budget -> over_budget
        travelers=2,
    )
    dest_res = DestinationAgent().get_destination_recommendations(over_trip)
    t_res = TransportAgent().get_transport_options(over_trip)
    a_res = AccommodationAgent().get_accommodation_options(over_trip, 5)
    b_res = BudgetAgent().calculate_budget(over_trip, t_res, a_res, dest_res)

    assert b_res.budget_status == "over_budget"

    agent = ItineraryAgent()
    res = agent.generate_itinerary(over_trip, dest_res, b_res)

    # Top scheduled activities should prioritize low-cost places (cost <= 500 or free)
    first_day_activities = res.days[0].activities
    assert len(first_day_activities) > 0
    assert first_day_activities[0].estimated_cost_max <= 500.0 or first_day_activities[0].estimated_cost_min == 0.0


def test_langgraph_workflow():
    input_str = "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
    final_state = run_trip_workflow(input_str)

    assert final_state["status"] == "success"
    assert final_state["trip_request"].origin == "Indore"
    assert final_state["transport_results"] is not None
    assert final_state["accommodation_results"] is not None
    assert final_state["destination_results"] is not None
    assert final_state["budget_result"] is not None
    assert final_state["itinerary_result"] is not None


def test_api_plan_endpoint_english():
    response = client.post(
        "/api/trips/plan",
        json={
            "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "itinerary" in data
    assert data["itinerary"]["duration_days"] == 6
    assert len(data["itinerary"]["days"]) == 6


def test_api_plan_endpoint_hinglish():
    response = client.post(
        "/api/trips/plan",
        json={
            "message": "Mujhe Indore se Goa jana hai 10 October se 15 October tak, budget 30k hai aur 2 log hain."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["trip"]["origin"] == "Indore"


def test_phase1_to_5_regression():
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

    # Phase 5
    assert (
        client.post(
            "/api/trips/budget",
            json={
                "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
            },
        ).status_code
        == 200
    )
