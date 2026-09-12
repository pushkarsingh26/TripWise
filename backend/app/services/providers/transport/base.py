from abc import ABC, abstractmethod

from app.models.transport import TransportResults
from app.models.trip import TripRequest


class BaseTransportProvider(ABC):
    @abstractmethod
    def get_transport_options(self, request: TripRequest) -> TransportResults:
        """Abstract method to retrieve transport options for a given trip request."""
        pass
