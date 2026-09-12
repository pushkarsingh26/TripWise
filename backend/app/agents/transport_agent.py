from typing import Optional

from app.models.transport import TransportResults
from app.models.trip import TripRequest
from app.services.providers.transport.base import BaseTransportProvider
from app.services.providers.transport.estimation import (
    EstimationTransportProvider,
)


class TransportAgent:
    def __init__(self, provider: Optional[BaseTransportProvider] = None):
        self.provider = provider or EstimationTransportProvider()

    def get_transport_options(self, request: TripRequest) -> TransportResults:
        return self.provider.get_transport_options(request)
