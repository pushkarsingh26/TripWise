from typing import Optional

from app.models.accommodation import AccommodationResults
from app.models.trip import TripRequest
from app.services.providers.accommodation.base import (
    BaseAccommodationProvider,
)
from app.services.providers.accommodation.estimation import (
    EstimationAccommodationProvider,
)


class AccommodationAgent:
    def __init__(self, provider: Optional[BaseAccommodationProvider] = None):
        self.provider = provider or EstimationAccommodationProvider()

    def get_accommodation_options(
        self, request: TripRequest, duration_nights: int
    ) -> AccommodationResults:
        return self.provider.get_accommodation_options(
            request, duration_nights
        )
