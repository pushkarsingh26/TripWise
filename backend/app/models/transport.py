from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

TransportMode = Literal["flight", "train", "bus"]
RecommendationType = Literal["fastest", "cheapest", "balanced"]


class TransportOption(BaseModel):
    mode: TransportMode
    estimated_cost_min: float = Field(
        ..., description="Minimum estimated cost in local currency"
    )
    estimated_cost_max: float = Field(
        ..., description="Maximum estimated cost in local currency"
    )
    currency: str = Field(default="INR", description="Currency code")
    pricing_type: str = Field(
        default="round_trip", description="Indicates round-trip or one-way"
    )
    duration: str = Field(
        ..., description="Approximate travel duration, e.g. 2h 15m"
    )
    comfort_level: str = Field(
        ..., description="Comfort tier: High, Medium, Basic"
    )
    recommendation_type: RecommendationType = Field(
        ..., description="Best for category: fastest, cheapest, balanced"
    )
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    is_estimate: bool = Field(
        default=True, description="Always True for estimated non-live pricing"
    )

    @model_validator(mode="after")
    def validate_costs(self):
        if self.estimated_cost_min < 0 or self.estimated_cost_max < 0:
            raise ValueError("Transport costs must be non-negative.")
        if self.estimated_cost_max < self.estimated_cost_min:
            raise ValueError(
                "estimated_cost_max cannot be less than estimated_cost_min."
            )
        return self


class TransportResults(BaseModel):
    origin: str
    destination: str
    outbound: Optional[str] = None
    return_date: Optional[str] = Field(default=None, alias="return")
    options: List[TransportOption] = Field(default_factory=list)
