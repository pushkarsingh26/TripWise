from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.planner_agent import PlannerAgent

router = APIRouter(prefix="/api/trips", tags=["trips"])
planner_agent = PlannerAgent()


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
