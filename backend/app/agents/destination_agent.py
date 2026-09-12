from typing import Optional

from app.models.destination import DestinationResults
from app.models.trip import TripRequest
from app.services.providers.destination.base import BaseDestinationProvider
from app.services.providers.destination.estimation import (
    EstimationDestinationProvider,
)


class DestinationAgent:
    def __init__(self, provider: Optional[BaseDestinationProvider] = None):
        self.provider = provider or EstimationDestinationProvider()

    def get_destination_recommendations(
        self, request: TripRequest
    ) -> DestinationResults:
        return self.provider.get_destination_recommendations(request)
