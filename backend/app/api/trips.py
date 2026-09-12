from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.accommodation_agent import AccommodationAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.transport_agent import TransportAgent
from app.models.trip import TripRequest

router = APIRouter(prefix="/api/trips", tags=["trips"])
planner_agent = PlannerAgent()
transport_agent = TransportAgent()
accommodation_agent = AccommodationAgent()


class ParseTripRequest(BaseModel):
    message: Optional[str] = None
    trip: Optional[Dict[str, Any]] = None


@router.post("/parse")
def parse_trip(payload: ParseTripRequest):
    if payload.message is not None:
        input_data = payload.message
    elif payload.trip is not None:
        input_data = payload.trip
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'message' or 'trip' must be provided in request body.",
        )

    result = planner_agent.process_request(input_data)

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@router.post("/options")
def get_trip_options(payload: ParseTripRequest):
    if payload.message is not None:
        input_data = payload.message
    elif payload.trip is not None:
        input_data = payload.trip
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'message' or 'trip' must be provided in request body.",
        )

    # 1. Run PlannerAgent
    planner_result = planner_agent.process_request(input_data)

    if planner_result.get("status") == "error":
        raise HTTPException(status_code=400, detail=planner_result.get("error"))

    if planner_result.get("status") == "needs_information":
        return planner_result

    # 2. Extract validated TripRequest
    raw_trip = planner_result["trip"]
    trip_req = TripRequest(**raw_trip)
    duration_days = planner_result["duration_days"]
    duration_nights = planner_result["duration_nights"]

    # 3. Run TransportAgent & AccommodationAgent
    transport_results = transport_agent.get_transport_options(trip_req)
    accommodation_results = accommodation_agent.get_accommodation_options(
        trip_req, duration_nights
    )

    return {
        "status": "success",
        "trip": trip_req.model_dump(mode="json"),
        "duration_days": duration_days,
        "duration_nights": duration_nights,
        "transport": transport_results.model_dump(mode="json", by_alias=True),
        "accommodation": accommodation_results.model_dump(mode="json"),
    }
