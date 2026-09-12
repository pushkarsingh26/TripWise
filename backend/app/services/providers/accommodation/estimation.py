from app.models.accommodation import (
    AccommodationOption,
    AccommodationResults,
)
from app.models.trip import TripRequest
from app.services.providers.accommodation.base import (
    BaseAccommodationProvider,
)


class EstimationAccommodationProvider(BaseAccommodationProvider):
    def get_accommodation_options(
        self, request: TripRequest, duration_nights: int
    ) -> AccommodationResults:
        nights = max(0, duration_nights)

        # Budget Stay tier
        budget_min_rate = 800.0
        budget_max_rate = 1500.0
        budget_stay = AccommodationOption(
            name="Budget Stay",
            category="budget",
            estimated_price_per_night_min=budget_min_rate,
            estimated_price_per_night_max=budget_max_rate,
            estimated_total_min=budget_min_rate * nights,
            estimated_total_max=budget_max_rate * nights,
            currency="INR",
            location_description="Standard budget hostels or guesthouses near city transit",
            rating=3.8,
            amenities=["Free Wi-Fi", "Air Conditioning", "Basic Breakfast"],
            is_estimate=True,
        )

        # Mid-range Stay tier
        mid_min_rate = 2500.0
        mid_max_rate = 4500.0
        mid_stay = AccommodationOption(
            name="Mid-range Stay",
            category="mid_range",
            estimated_price_per_night_min=mid_min_rate,
            estimated_price_per_night_max=mid_max_rate,
            estimated_total_min=mid_min_rate * nights,
            estimated_total_max=mid_max_rate * nights,
            currency="INR",
            location_description="3-star hotels or private boutique stays near key attractions",
            rating=4.2,
            amenities=[
                "Free Wi-Fi",
                "Breakfast Included",
                "24/7 Room Service",
                "Swimming Pool",
            ],
            is_estimate=True,
        )

        # Premium Stay tier
        premium_min_rate = 6000.0
        premium_max_rate = 12000.0
        premium_stay = AccommodationOption(
            name="Premium Stay",
            category="premium",
            estimated_price_per_night_min=premium_min_rate,
            estimated_price_per_night_max=premium_max_rate,
            estimated_total_min=premium_min_rate * nights,
            estimated_total_max=premium_max_rate * nights,
            currency="INR",
            location_description="4-star to 5-star luxury resorts or prime beachfront properties",
            rating=4.7,
            amenities=[
                "Free Wi-Fi",
                "Buffet Breakfast",
                "Spa & Wellness",
                "Ocean View / Prime Location",
                "Airport Shuttle",
            ],
            is_estimate=True,
        )

        return AccommodationResults(
            destination=request.destination,
            check_in=str(request.start_date),
            check_out=str(request.end_date),
            nights=nights,
            options=[budget_stay, mid_stay, premium_stay],
        )
