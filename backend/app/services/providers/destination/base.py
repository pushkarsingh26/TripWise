from abc import ABC, abstractmethod

from app.models.destination import DestinationResults
from app.models.trip import TripRequest


class BaseDestinationProvider(ABC):
    @abstractmethod
    def get_destination_recommendations(
        self, request: TripRequest
    ) -> DestinationResults:
        """Abstract method to retrieve destination recommendations for a trip request."""
        pass
