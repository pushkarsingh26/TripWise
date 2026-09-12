from typing import List, Literal
from pydantic import BaseModel, Field, model_validator

BudgetStatus = Literal["within_budget", "near_budget", "over_budget"]


class BudgetBreakdown(BaseModel):
    transport_min: float = Field(
        default=0.0,
        description="Transport cost min (multiplied by travelers)",
    )
    transport_max: float = Field(
        default=0.0,
        description="Transport cost max (multiplied by travelers)",
    )
    accommodation_min: float = Field(
        default=0.0,
        description="Accommodation cost min (consumed directly from Phase 3)",
    )
    accommodation_max: float = Field(
        default=0.0,
        description="Accommodation cost max (consumed directly from Phase 3)",
    )
    activities_min: float = Field(
        default=0.0,
        description="Activities cost min (subset multiplied by travelers)",
    )
    activities_max: float = Field(
        default=0.0,
        description="Activities cost max (subset multiplied by travelers)",
    )
    food_min: float = Field(
        default=0.0,
        description="Food cost min (daily rate × travelers × days)",
    )
    food_max: float = Field(
        default=0.0,
        description="Food cost max (daily rate × travelers × days)",
    )
    local_travel_min: float = Field(
        default=0.0,
        description="Local travel min (daily rate × travelers × days)",
    )
    local_travel_max: float = Field(
        default=0.0,
        description="Local travel max (daily rate × travelers × days)",
    )
    miscellaneous_min: float = Field(
        default=0.0,
        description="Miscellaneous min (daily rate × travelers × days)",
    )
    miscellaneous_max: float = Field(
        default=0.0,
        description="Miscellaneous max (daily rate × travelers × days)",
    )
    total_min: float = Field(
        default=0.0, description="Sum of category minimums"
    )
    total_max: float = Field(
        default=0.0, description="Sum of category maximums"
    )
    currency: str = Field(default="INR", description="Currency code")
    is_estimate: bool = Field(
        default=True, description="Always True for estimated non-live pricing"
    )

    @model_validator(mode="after")
    def validate_totals(self):
        if self.total_min < 0 or self.total_max < 0:
            raise ValueError("Budget breakdown totals must be non-negative.")
        if self.total_max < self.total_min:
            raise ValueError(
                "total_max cannot be less than total_min in breakdown."
            )
        return self


class BudgetResult(BaseModel):
    budget: float = Field(..., description="User requested budget")
    breakdown: BudgetBreakdown
    budget_status: BudgetStatus = Field(
        ..., description="within_budget, near_budget, or over_budget"
    )
    remaining_min: float = Field(
        ...,
        description="budget - total_max (min estimated remaining / negative if over budget)",
    )
    remaining_max: float = Field(
        ..., description="budget - total_min (max estimated remaining)"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Optimization suggestions derived from available options",
    )
    is_estimate: bool = Field(
        default=True, description="Always True for estimated non-live pricing"
    )
