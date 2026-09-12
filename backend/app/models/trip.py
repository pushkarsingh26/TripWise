from datetime import date
from typing import List
from pydantic import BaseModel, Field, model_validator


class TripRequest(BaseModel):
    origin: str = Field(..., description="Origin city or location")
    destination: str = Field(..., description="Destination city or location")
    start_date: date = Field(..., description="Start date of trip")
    end_date: date = Field(..., description="End date of trip")
    budget: float = Field(..., description="Total trip budget")
    travelers: int = Field(..., description="Number of travelers")
    preferences: List[str] = Field(
        default_factory=list, description="Travel preferences"
    )

    @model_validator(mode="after")
    def validate_trip_request(self):
        if not self.origin or not self.origin.strip():
            raise ValueError("Origin cannot be empty.")
        if not self.destination or not self.destination.strip():
            raise ValueError("Destination cannot be empty.")

        if self.origin.strip().lower() == self.destination.strip().lower():
            raise ValueError("Origin and destination cannot be the same.")

        if self.end_date < self.start_date:
            raise ValueError("End date must be on or after start date.")

        if self.budget <= 0:
            raise ValueError("Budget must be greater than 0.")

        if self.travelers <= 0:
            raise ValueError("Travelers count must be greater than 0.")

        return self


class TripPlanningState(BaseModel):
    trip: TripRequest
    duration_days: int
    duration_nights: int
