from datetime import date
from fastapi.testclient import TestClient

from app.agents.planner_agent import PlannerAgent
from app.main import app
from app.services.trip_parser import TripParser

client = TestClient(app)
planner = PlannerAgent()
REF_DATE = date(2026, 9, 12)


def test_valid_english_request():
    msg = "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
    res = planner.process_request(msg, ref_date=REF_DATE)
    assert res["status"] == "success"
    assert res["trip"]["origin"] == "Indore"
    assert res["trip"]["destination"] == "Goa"
    assert res["trip"]["start_date"] == "2026-10-10"
    assert res["trip"]["end_date"] == "2026-10-15"
    assert res["trip"]["budget"] == 30000.0
    assert res["trip"]["travelers"] == 2
    assert res["duration_days"] == 6
    assert res["duration_nights"] == 5


def test_valid_hinglish_request():
    msg = "Mujhe Indore se Goa jana hai 10 October se 15 October tak, budget 30k hai aur 2 log hain."
    res = planner.process_request(msg, ref_date=REF_DATE)
    assert res["status"] == "success"
    assert res["trip"]["origin"] == "Indore"
    assert res["trip"]["destination"] == "Goa"
    assert res["trip"]["start_date"] == "2026-10-10"
    assert res["trip"]["end_date"] == "2026-10-15"
    assert res["trip"]["budget"] == 30000.0
    assert res["trip"]["travelers"] == 2


def test_same_day_trip():
    msg = "Travel from Delhi to Jaipur on October 10 to October 10 budget 15000 for 1 person"
    res = planner.process_request(msg, ref_date=REF_DATE)
    assert res["status"] == "success"
    assert res["duration_days"] == 1
    assert res["duration_nights"] == 0


def test_date_formats():
    parser = TripParser()

    res1 = parser.parse("from Delhi to Goa 10 Oct -> 15 Oct budget 20000 for 2 people", ref_date=REF_DATE)
    assert res1["start_date"] == date(2026, 10, 10)
    assert res1["end_date"] == date(2026, 10, 15)

    res2 = parser.parse("from Delhi to Goa 10/10/2026 to 15/10/2026 budget 20000 for 2 people", ref_date=REF_DATE)
    assert res2["start_date"] == date(2026, 10, 10)
    assert res2["end_date"] == date(2026, 10, 15)


def test_missing_fields():
    # Missing budget
    res1 = planner.process_request(
        "I want to travel from Indore to Goa from October 10 to October 15 for 2 people.",
        ref_date=REF_DATE,
    )
    assert res1["status"] == "needs_information"
    assert "budget" in res1["missing"]

    # Missing destination
    res2 = planner.process_request(
        "I want to travel from Indore from October 10 to October 15 with a budget of 30000 for 2 people.",
        ref_date=REF_DATE,
    )
    assert res2["status"] == "needs_information"
    assert "destination" in res2["missing"]

    # Missing dates
    res3 = planner.process_request(
        "I want to travel from Indore to Goa with a budget of 30000 for 2 people.",
        ref_date=REF_DATE,
    )
    assert res3["status"] == "needs_information"
    assert "start_date" in res3["missing"] or "end_date" in res3["missing"]

    # Missing travelers
    res4 = planner.process_request(
        "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000.",
        ref_date=REF_DATE,
    )
    assert res4["status"] == "needs_information"
    assert "travelers" in res4["missing"]


def test_invalid_values():
    # Negative budget
    res1 = planner.process_request(
        {
            "origin": "Indore",
            "destination": "Goa",
            "start_date": date(2026, 10, 10),
            "end_date": date(2026, 10, 15),
            "budget": -500.0,
            "travelers": 2,
        }
    )
    assert res1["status"] == "error"
    assert "Budget must be greater than 0" in res1["error"]

    # Zero travelers
    res2 = planner.process_request(
        {
            "origin": "Indore",
            "destination": "Goa",
            "start_date": date(2026, 10, 10),
            "end_date": date(2026, 10, 15),
            "budget": 30000.0,
            "travelers": 0,
        }
    )
    assert res2["status"] == "error"
    assert "Travelers count must be greater than 0" in res2["error"]

    # End date before start date
    res3 = planner.process_request(
        {
            "origin": "Indore",
            "destination": "Goa",
            "start_date": date(2026, 10, 15),
            "end_date": date(2026, 10, 10),
            "budget": 30000.0,
            "travelers": 2,
        }
    )
    assert res3["status"] == "error"
    assert "End date must be on or after start date" in res3["error"]

    # Same origin and destination
    res4 = planner.process_request(
        {
            "origin": "Indore",
            "destination": "Indore",
            "start_date": date(2026, 10, 10),
            "end_date": date(2026, 10, 15),
            "budget": 30000.0,
            "travelers": 2,
        }
    )
    assert res4["status"] == "error"
    assert "Origin and destination cannot be the same" in res4["error"]


def test_api_endpoint():
    response = client.post(
        "/api/trips/parse",
        json={
            "message": "I want to travel from Indore to Goa from October 10 to October 15 with a budget of 30000 for 2 people."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["trip"]["origin"] == "Indore"
    assert data["trip"]["destination"] == "Goa"
