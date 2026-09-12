from abc import ABC, abstractmethod

from app.models.accommodation import AccommodationResults
from app.models.trip import TripRequest


class BaseAccommodationProvider(ABC):
    @abstractmethod
    def get_accommodation_options(
        self, request: TripRequest, duration_nights: int
    ) -> AccommodationResults:
        """Abstract method to retrieve accommodation options for a given trip request and nights count."""
        pass
