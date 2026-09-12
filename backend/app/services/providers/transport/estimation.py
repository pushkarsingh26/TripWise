from app.models.transport import TransportOption, TransportResults
from app.models.trip import TripRequest
from app.services.providers.transport.base import BaseTransportProvider


class EstimationTransportProvider(BaseTransportProvider):
    def get_transport_options(self, request: TripRequest) -> TransportResults:
        # Generate flight option
        flight = TransportOption(
            mode="flight",
            estimated_cost_min=4500.0,
            estimated_cost_max=8500.0,
            currency="INR",
            pricing_type="round_trip",
            duration="2h 15m",
            comfort_level="High",
            recommendation_type="fastest",
            pros=["Fastest travel time", "Direct connection"],
            cons=["Higher cost", "Airport check-in overhead"],
            is_estimate=True,
        )

        # Generate train option
        train = TransportOption(
            mode="train",
            estimated_cost_min=1200.0,
            estimated_cost_max=2800.0,
            currency="INR",
            pricing_type="round_trip",
            duration="14h 30m",
            comfort_level="Medium",
            recommendation_type="balanced",
            pros=["Scenic route", "Good value for money"],
            cons=["Longer travel duration"],
            is_estimate=True,
        )

        # Generate bus option
        bus = TransportOption(
            mode="bus",
            estimated_cost_min=800.0,
            estimated_cost_max=1800.0,
            currency="INR",
            pricing_type="round_trip",
            duration="16h 00m",
            comfort_level="Basic",
            recommendation_type="cheapest",
            pros=["Lowest cost", "Frequent availability"],
            cons=["Longest duration", "Variable road comfort"],
            is_estimate=True,
        )

        return TransportResults(
            origin=request.origin,
            destination=request.destination,
            outbound=str(request.start_date),
            return_date=str(request.end_date),
            options=[flight, train, bus],
        )
