from typing import List
from pydantic import BaseModel, Field, model_validator


class ItineraryActivity(BaseModel):
    name: str = Field(..., description="Activity or place name")
    category: str = Field(
        ..., description="Category tag e.g. attraction, food, activity"
    )
    description: str = Field(..., description="Short description")
    start_time: str = Field(..., description="HH:MM start time e.g. 09:30")
    end_time: str = Field(..., description="HH:MM end time e.g. 11:30")
    duration: str = Field(
        ..., description="Recommended duration string e.g. 2 hours"
    )
    estimated_cost_min: float = Field(
        default=0.0, description="Min illustrative cost"
    )
    estimated_cost_max: float = Field(
        default=0.0, description="Max illustrative cost"
    )
    is_estimate: bool = Field(
        default=True, description="Always True for estimated non-live pricing"
    )

    @model_validator(mode="after")
    def validate_activity(self):
        if not self.name or not self.name.strip():
            raise ValueError("Activity name cannot be empty.")
        if self.estimated_cost_min < 0 or self.estimated_cost_max < 0:
            raise ValueError("Costs must be non-negative.")
        if self.estimated_cost_max < self.estimated_cost_min:
            raise ValueError(
                "estimated_cost_max cannot be less than estimated_cost_min."
            )
        return self


class ItineraryDay(BaseModel):
    day_number: int = Field(..., description="Day index 1, 2, 3...")
    date: str = Field(..., description="Date string YYYY-MM-DD")
    title: str = Field(..., description="Descriptive title for the day")
    activities: List[ItineraryActivity] = Field(default_factory=list)
    estimated_day_cost_min: float = Field(default=0.0)
    estimated_day_cost_max: float = Field(default=0.0)


class ItineraryResult(BaseModel):
    destination: str
    start_date: str
    end_date: str
    duration_days: int
    days: List[ItineraryDay] = Field(default_factory=list)
    total_activity_cost_min: float = Field(default=0.0)
    total_activity_cost_max: float = Field(default=0.0)
    is_estimate: bool = Field(
        default=True, description="Always True for estimated non-live pricing"
    )
