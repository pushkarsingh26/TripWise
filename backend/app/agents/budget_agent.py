from typing import List, Optional

from app.models.accommodation import AccommodationResults
from app.models.budget import BudgetBreakdown, BudgetResult, BudgetStatus
from app.models.destination import DestinationResults
from app.models.transport import TransportResults
from app.models.trip import TripRequest

DEFAULT_FOOD_RATE_MIN = 500.0
DEFAULT_FOOD_RATE_MAX = 1000.0

DEFAULT_LOCAL_TRAVEL_RATE_MIN = 200.0
DEFAULT_LOCAL_TRAVEL_RATE_MAX = 500.0

DEFAULT_MISCELLANEOUS_RATE_MIN = 100.0
DEFAULT_MISCELLANEOUS_RATE_MAX = 300.0

ACTIVITY_SUBSET_COUNT = 3


class BudgetAgent:
    def __init__(
        self,
        food_rate_min: float = DEFAULT_FOOD_RATE_MIN,
        food_rate_max: float = DEFAULT_FOOD_RATE_MAX,
        local_rate_min: float = DEFAULT_LOCAL_TRAVEL_RATE_MIN,
        local_rate_max: float = DEFAULT_LOCAL_TRAVEL_RATE_MAX,
        misc_rate_min: float = DEFAULT_MISCELLANEOUS_RATE_MIN,
        misc_rate_max: float = DEFAULT_MISCELLANEOUS_RATE_MAX,
        activity_subset_count: int = ACTIVITY_SUBSET_COUNT,
    ):
        self.food_rate_min = food_rate_min
        self.food_rate_max = food_rate_max
        self.local_rate_min = local_rate_min
        self.local_rate_max = local_rate_max
        self.misc_rate_min = misc_rate_min
        self.misc_rate_max = misc_rate_max
        self.activity_subset_count = activity_subset_count

    def calculate_budget(
        self,
        request: TripRequest,
        transport_results: TransportResults,
        accommodation_results: AccommodationResults,
        destination_results: DestinationResults,
    ) -> BudgetResult:
        travelers = max(1, request.travelers)
        days = max(1, (request.end_date - request.start_date).days + 1)

        # 1. Transport Cost (multiplied by travelers)
        # Select balanced option if available, otherwise first option
        selected_transport = None
        if transport_results.options:
            balanced = [
                opt
                for opt in transport_results.options
                if opt.recommendation_type == "balanced"
            ]
            selected_transport = (
                balanced[0] if balanced else transport_results.options[0]
            )

        if selected_transport:
            transport_min = selected_transport.estimated_cost_min * travelers
            transport_max = selected_transport.estimated_cost_max * travelers
        else:
            transport_min = 0.0
            transport_max = 0.0

        # 2. Accommodation Cost (consumed directly from Phase 3 totals, NOT multiplied by travelers)
        selected_acc = None
        if accommodation_results.options:
            mid = [
                opt
                for opt in accommodation_results.options
                if opt.category == "mid_range"
            ]
            selected_acc = mid[0] if mid else accommodation_results.options[0]

        if selected_acc:
            accommodation_min = selected_acc.estimated_total_min
            accommodation_max = selected_acc.estimated_total_max
        else:
            accommodation_min = 0.0
            accommodation_max = 0.0

        # 3. Activity Cost (subset × travelers)
        recs = destination_results.recommendations[: self.activity_subset_count]
        act_per_person_min = sum(p.estimated_cost_min for p in recs)
        act_per_person_max = sum(p.estimated_cost_max for p in recs)
        activities_min = act_per_person_min * travelers
        activities_max = act_per_person_max * travelers

        # 4. Daily Categories (Food, Local Travel, Miscellaneous)
        food_min = self.food_rate_min * travelers * days
        food_max = self.food_rate_max * travelers * days

        local_travel_min = self.local_rate_min * travelers * days
        local_travel_max = self.local_rate_max * travelers * days

        miscellaneous_min = self.misc_rate_min * travelers * days
        miscellaneous_max = self.misc_rate_max * travelers * days

        # 5. Totals
        total_min = (
            transport_min
            + accommodation_min
            + activities_min
            + food_min
            + local_travel_min
            + miscellaneous_min
        )
        total_max = (
            transport_max
            + accommodation_max
            + activities_max
            + food_max
            + local_travel_max
            + miscellaneous_max
        )

        breakdown = BudgetBreakdown(
            transport_min=transport_min,
            transport_max=transport_max,
            accommodation_min=accommodation_min,
            accommodation_max=accommodation_max,
            activities_min=activities_min,
            activities_max=activities_max,
            food_min=food_min,
            food_max=food_max,
            local_travel_min=local_travel_min,
            local_travel_max=local_travel_max,
            miscellaneous_min=miscellaneous_min,
            miscellaneous_max=miscellaneous_max,
            total_min=total_min,
            total_max=total_max,
            currency="INR",
            is_estimate=True,
        )

        # 6. Budget Delta Semantics
        user_budget = request.budget
        remaining_min = user_budget - total_max
        remaining_max = user_budget - total_min

        # 7. Budget Status Classification
        if total_max <= user_budget:
            budget_status: BudgetStatus = "within_budget"
        elif total_min <= user_budget:
            budget_status = "near_budget"
        else:
            budget_status = "over_budget"

        # 8. Optimization Recommendations from Actual Options
        recommendations: List[str] = []

        # Transport Optimization
        if selected_transport and transport_results.options:
            cheaper_transports = [
                t
                for t in transport_results.options
                if (t.estimated_cost_min * travelers)
                < (selected_transport.estimated_cost_min * travelers)
            ]
            if cheaper_transports:
                cheapest = min(
                    cheaper_transports, key=lambda t: t.estimated_cost_min
                )
                sav_min = (
                    selected_transport.estimated_cost_min - cheapest.estimated_cost_min
                ) * travelers
                sav_max = (
                    selected_transport.estimated_cost_max - cheapest.estimated_cost_max
                ) * travelers
                recommendations.append(
                    f"Choose {cheapest.mode.title()} instead of {selected_transport.mode.title()} to reduce estimated transport cost by ₹{sav_min:,.0f}–₹{sav_max:,.0f}."
                )

        # Accommodation Optimization
        if selected_acc and accommodation_results.options:
            cheaper_accs = [
                a
                for a in accommodation_results.options
                if a.estimated_total_min < selected_acc.estimated_total_min
            ]
            if cheaper_accs:
                cheapest_acc = min(
                    cheaper_accs, key=lambda a: a.estimated_total_min
                )
                sav_min = selected_acc.estimated_total_min - cheapest_acc.estimated_total_min
                sav_max = selected_acc.estimated_total_max - cheapest_acc.estimated_total_max
                recommendations.append(
                    f"Choose {cheapest_acc.name} accommodation to reduce estimated stay cost by ₹{sav_min:,.0f}–₹{sav_max:,.0f}."
                )

        if activities_max > 0:
            recommendations.append(
                "Prioritize lower-cost or free activities to reduce estimated activity spending."
            )

        return BudgetResult(
            budget=user_budget,
            breakdown=breakdown,
            budget_status=budget_status,
            remaining_min=remaining_min,
            remaining_max=remaining_max,
            recommendations=recommendations,
            is_estimate=True,
        )
