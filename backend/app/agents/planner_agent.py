from datetime import date
from typing import Any, Dict, List, Optional, Union
from pydantic import ValidationError

from app.models.trip import TripPlanningState, TripRequest
from app.services.trip_parser import TripParser


class PlannerAgent:
    def __init__(self, parser: Optional[TripParser] = None):
        self.parser = parser or TripParser()

    def process_request(
        self,
        input_data: Union[str, Dict[str, Any]],
        ref_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Process user request and return structured response or missing field info."""
        if isinstance(input_data, str):
            extracted = self.parser.parse(input_data, ref_date=ref_date)
        else:
            extracted = input_data

        # Required fields check
        required_fields = [
            "origin",
            "destination",
            "start_date",
            "end_date",
            "budget",
            "travelers",
        ]
        missing = [
            field for field in required_fields if extracted.get(field) is None
        ]

        if missing:
            return {
                "status": "needs_information",
                "missing": missing,
            }

        # Attempt to create TripRequest Pydantic model for validation
        try:
            trip_req = TripRequest(
                origin=extracted["origin"],
                destination=extracted["destination"],
                start_date=extracted["start_date"],
                end_date=extracted["end_date"],
                budget=extracted["budget"],
                travelers=extracted["travelers"],
                preferences=extracted.get("preferences", []),
            )
        except ValidationError as ve:
            # Format validation error message
            errors = ve.errors()
            msg = errors[0]["msg"] if errors else "Invalid trip parameters."
            if "Value error, " in msg:
                msg = msg.replace("Value error, ", "")
            return {
                "status": "error",
                "error": msg,
            }
        except ValueError as ve:
            return {
                "status": "error",
                "error": str(ve),
            }

        # Calculate duration
        duration_days = (trip_req.end_date - trip_req.start_date).days + 1
        duration_nights = (trip_req.end_date - trip_req.start_date).days

        planning_state = TripPlanningState(
            trip=trip_req,
            duration_days=duration_days,
            duration_nights=duration_nights,
        )

        return {
            "status": "success",
            "trip": planning_state.trip.model_dump(mode="json"),
            "duration_days": planning_state.duration_days,
            "duration_nights": planning_state.duration_nights,
        }
