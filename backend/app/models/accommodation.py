from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

AccommodationCategory = Literal["budget", "mid_range", "premium"]


class AccommodationOption(BaseModel):
    name: str = Field(
        ...,
        description="Generic category name e.g. Budget Stay, Mid-range Stay, Premium Stay",
    )
    category: AccommodationCategory
    estimated_price_per_night_min: float = Field(
        ..., description="Min estimated rate per night"
    )
    estimated_price_per_night_max: float = Field(
        ..., description="Max estimated rate per night"
    )
    estimated_total_min: float = Field(
        ..., description="Min estimated total stay cost"
    )
    estimated_total_max: float = Field(
        ..., description="Max estimated total stay cost"
    )
    currency: str = Field(default="INR", description="Currency code")
    location_description: str = Field(
        ..., description="General location or neighborhood description"
    )
    rating: Optional[float] = Field(
        default=None, description="Average tier rating e.g. 3.5, 4.0"
    )
    amenities: List[str] = Field(default_factory=list)
    is_estimate: bool = Field(
        default=True, description="Always True for estimated non-live pricing"
    )

    @model_validator(mode="after")
    def validate_costs(self):
        if (
            self.estimated_price_per_night_min < 0
            or self.estimated_price_per_night_max < 0
        ):
            raise ValueError("Nightly price must be non-negative.")
        if self.estimated_total_min < 0 or self.estimated_total_max < 0:
            raise ValueError("Total cost must be non-negative.")
        return self


class AccommodationResults(BaseModel):
    destination: str
    check_in: str
    check_out: str
    nights: int
    options: List[AccommodationOption] = Field(default_factory=list)
