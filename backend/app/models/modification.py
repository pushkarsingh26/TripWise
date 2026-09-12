from typing import List, Literal, Optional
from pydantic import BaseModel, Field

ModificationAction = Literal[
    "change_budget",
    "change_duration",
    "change_destination",
    "add_preference",
    "remove_preference",
    "remove_activity",
    "change_transport_preference",
    "change_accommodation_preference",
    "optimize_budget",
    "regenerate_itinerary",
    "ambiguous_request",
]


class ModificationIntent(BaseModel):
    action: ModificationAction
    new_destination: Optional[str] = None
    new_budget: Optional[float] = None
    new_duration_days: Optional[int] = None
    add_preferences: List[str] = Field(default_factory=list)
    remove_preferences: List[str] = Field(default_factory=list)
    remove_activity_names: List[str] = Field(default_factory=list)
    requested_transport_preference: Optional[str] = None
    requested_accommodation_preference: Optional[str] = None
    confirmation_required: bool = False
    clarification_message: Optional[str] = None
