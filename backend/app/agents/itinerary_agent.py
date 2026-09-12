from datetime import timedelta
import re
from typing import List, Optional

from app.models.budget import BudgetResult
from app.models.destination import DestinationPlace, DestinationResults
from app.models.itinerary import (
    ItineraryActivity,
    ItineraryDay,
    ItineraryResult,
)
from app.models.trip import TripRequest


class ItineraryAgent:
    def generate_itinerary(
        self,
        request: TripRequest,
        destination_results: DestinationResults,
        budget_result: Optional[BudgetResult] = None,
    ) -> ItineraryResult:
        # Calculate trip dates
        num_days = max(1, (request.end_date - request.start_date).days + 1)
        dates = [
            request.start_date + timedelta(days=i) for i in range(num_days)
        ]

        # Candidates from DestinationResults
        candidates = list(destination_results.recommendations)

        # Apply budget sensitivity to filter/rank candidates
        budget_status = (
            budget_result.budget_status if budget_result else "within_budget"
        )
        candidates = self._filter_candidates_by_budget(
            candidates, budget_status
        )

        # Distribute candidates across days
        scheduled_days: List[ItineraryDay] = []
        total_activity_min = 0.0
        total_activity_max = 0.0

        cand_idx = 0
        num_candidates = len(candidates)

        for i, current_date in enumerate(dates):
            day_num = i + 1
            date_str = str(current_date)

            # Determine number of activities for this day (1 to 2 for same day / arrival, up to 3 for full days)
            if num_days == 1:
                max_acts_for_day = 2
            elif i == 0 or i == num_days - 1:
                max_acts_for_day = 2
            else:
                max_acts_for_day = 3

            day_activities: List[ItineraryActivity] = []
            start_minutes = 570  # 09:30 in minutes from midnight (9*60 + 30)
            day_cost_min = 0.0
            day_cost_max = 0.0

            acts_added = 0
            while cand_idx < num_candidates and acts_added < max_acts_for_day:
                place = candidates[cand_idx]
                cand_idx += 1

                duration_hours = self._parse_duration_hours(
                    place.recommended_duration
                )
                duration_minutes = int(duration_hours * 60)

                # Cap activity end time before 20:00 (1200 mins)
                if start_minutes + duration_minutes > 1200 and acts_added > 0:
                    break

                s_time = self._format_time(start_minutes)
                e_time = self._format_time(start_minutes + duration_minutes)

                act = ItineraryActivity(
                    name=place.name,
                    category=place.category,
                    description=place.description,
                    start_time=s_time,
                    end_time=e_time,
                    duration=place.recommended_duration,
                    estimated_cost_min=place.estimated_cost_min,
                    estimated_cost_max=place.estimated_cost_max,
                    is_estimate=True,
                )
                day_activities.append(act)
                day_cost_min += place.estimated_cost_min
                day_cost_max += place.estimated_cost_max

                # Advance cursor by duration + 30 min break / lunch
                start_minutes += duration_minutes + 30
                acts_added += 1

            # Day title
            if day_num == 1:
                title = f"Day 1: Arrival & {destination_results.destination} Exploration"
            elif day_num == num_days:
                title = f"Day {day_num}: Final Sights & Departure"
            else:
                top_cat = (
                    day_activities[0].category.title()
                    if day_activities
                    else "Sights"
                )
                title = f"Day {day_num}: {top_cat} & Local Culture"

            day_obj = ItineraryDay(
                day_number=day_num,
                date=date_str,
                title=title,
                activities=day_activities,
                estimated_day_cost_min=day_cost_min,
                estimated_day_cost_max=day_cost_max,
            )
            scheduled_days.append(day_obj)
            total_activity_min += day_cost_min
            total_activity_max += day_cost_max

        return ItineraryResult(
            destination=request.destination,
            start_date=str(request.start_date),
            end_date=str(request.end_date),
            duration_days=num_days,
            days=scheduled_days,
            total_activity_cost_min=total_activity_min,
            total_activity_cost_max=total_activity_max,
            is_estimate=True,
        )

    def _filter_candidates_by_budget(
        self, candidates: List[DestinationPlace], budget_status: str
    ) -> List[DestinationPlace]:
        if budget_status == "over_budget":
            # Strongly prioritize lowest max cost first
            return sorted(
                candidates,
                key=lambda p: (p.estimated_cost_max, p.estimated_cost_min),
            )
        elif budget_status == "near_budget":
            # Prefer lower-to-moderate cost activities
            return sorted(candidates, key=lambda p: p.estimated_cost_min)
        else:
            return candidates

    def _parse_duration_hours(self, duration_str: str) -> float:
        d_lower = duration_str.lower()
        if "full day" in d_lower:
            return 4.5
        if "half day" in d_lower:
            return 3.0

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:-|to)?\s*(\d+(?:\.\d+)?)?", d_lower
        )
        if match:
            v1 = float(match.group(1))
            if match.group(2):
                v2 = float(match.group(2))
                return min(3.5, max(1.0, (v1 + v2) / 2.0))
            return min(3.5, max(1.0, v1))

        return 2.0

    def _format_time(self, total_minutes: int) -> str:
        hours = (total_minutes // 60) % 24
        mins = total_minutes % 60
        return f"{hours:02d}:{mins:02d}"
