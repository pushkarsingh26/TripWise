from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

DestinationCategory = Literal[
    "attraction",
    "activity",
    "food",
    "culture",
    "nature",
    "adventure",
    "shopping",
]


class DestinationPlace(BaseModel):
    name: str = Field(..., description="Place or activity name")
    category: DestinationCategory
    description: str = Field(..., description="Short description")
    estimated_cost_min: float = Field(
        default=0.0, description="Min illustrative cost in local currency"
    )
    estimated_cost_max: float = Field(
        default=0.0, description="Max illustrative cost in local currency"
    )
    currency: str = Field(default="INR", description="Currency code")
    recommended_duration: str = Field(
        ..., description="Recommended visit duration, e.g. 2-3 hours"
    )
    best_for: List[str] = Field(
        default_factory=list,
        description="Target tags e.g. ['beach', 'water_sports']",
    )
    is_estimate: bool = Field(
        default=True, description="Always True for estimated non-live pricing"
    )

    @model_validator(mode="after")
    def validate_destination_place(self):
        if not self.name or not self.name.strip():
            raise ValueError("Place name cannot be empty.")
        if self.estimated_cost_min < 0 or self.estimated_cost_max < 0:
            raise ValueError("Costs must be non-negative.")
        if self.estimated_cost_max < self.estimated_cost_min:
            raise ValueError(
                "estimated_cost_max cannot be less than estimated_cost_min."
            )
        return self


class DestinationResults(BaseModel):
    destination: str
    supported: bool = Field(
        default=True, description="True if destination is in dataset"
    )
    message: Optional[str] = Field(
        default=None, description="Informational message if unsupported"
    )
    recommendations: List[DestinationPlace] = Field(default_factory=list)
