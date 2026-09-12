from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional
import copy

from app.models.modification import ModificationIntent
from app.models.trip import TripRequest
from app.workflows.trip_workflow import run_trip_workflow


class TripModifier:
    """
    Deterministic modification engine for Tripwise.
    Applies validated ModificationIntent to an existing trip request and re-runs the LangGraph workflow.
    """

    def modify_trip(
        self,
        current_trip_dict: Dict[str, Any],
        intent: ModificationIntent,
    ) -> Dict[str, Any]:
        """
        Applies intent changes to current_trip_dict and returns the workflow result along with intent & message.
        """
        if intent.confirmation_required or intent.action == "ambiguous_request":
            return {
                "status": "needs_clarification",
                "intent": intent.model_dump(mode="json"),
                "trip": current_trip_dict,
                "plan": None,
                "message": intent.clarification_message or "Modification is ambiguous. Please clarify your request.",
            }

        # Work on a copy of the current trip input fields
        updated_dict = copy.deepcopy(current_trip_dict)
        if "trip" in updated_dict and isinstance(updated_dict["trip"], dict):
            raw_req = updated_dict["trip"]
        elif "trip_request" in updated_dict and isinstance(updated_dict["trip_request"], dict):
            raw_req = updated_dict["trip_request"]
        else:
            raw_req = updated_dict

        # Extract base fields
        origin = raw_req.get("origin")
        destination = raw_req.get("destination")
        start_date_val = raw_req.get("start_date")
        end_date_val = raw_req.get("end_date")
        budget = raw_req.get("budget", 20000.0)
        travelers = raw_req.get("travelers", 1)
        preferences = list(raw_req.get("preferences") or [])

        # Parse start_date and end_date if they are strings
        if isinstance(start_date_val, str):
            s_date = datetime.strptime(start_date_val, "%Y-%m-%d").date()
        else:
            s_date = start_date_val or date.today()

        if isinstance(end_date_val, str):
            e_date = datetime.strptime(end_date_val, "%Y-%m-%d").date()
        else:
            e_date = end_date_val or s_date

        confirmation_msg = "Updated your trip according to your request."

        # Apply intent actions deterministically
        if intent.action == "change_budget":
            if intent.new_budget is not None and intent.new_budget > 0:
                budget = float(intent.new_budget)
                confirmation_msg = f"Updated total trip budget to ₹{budget:,.2f}."
            else:
                return {
                    "status": "error",
                    "error": "Invalid budget value specified.",
                    "intent": intent.model_dump(mode="json"),
                }

        elif intent.action == "change_duration":
            if intent.new_duration_days is not None and intent.new_duration_days > 0:
                e_date = s_date + timedelta(days=intent.new_duration_days - 1)
                confirmation_msg = f"Updated trip duration to {intent.new_duration_days} day(s)."
            else:
                return {
                    "status": "error",
                    "error": "Invalid duration specified.",
                    "intent": intent.model_dump(mode="json"),
                }

        elif intent.action == "change_destination":
            if intent.new_destination and intent.new_destination.strip():
                destination = intent.new_destination.strip().title()
                confirmation_msg = f"Changed destination to {destination}."
            else:
                return {
                    "status": "error",
                    "error": "Invalid destination specified.",
                    "intent": intent.model_dump(mode="json"),
                }

        elif intent.action == "add_preference":
            added = []
            for p in intent.add_preferences:
                if p and p.lower() not in [existing.lower() for existing in preferences]:
                    preferences.append(p.lower())
                    added.append(p)
            if added:
                confirmation_msg = f"Added preference(s): {', '.join(added)}."
            else:
                confirmation_msg = "Updated preferences."

        elif intent.action == "remove_preference":
            removed = []
            for p in intent.remove_preferences:
                preferences = [existing for existing in preferences if existing.lower() != p.lower()]
                removed.append(p)
            if removed:
                confirmation_msg = f"Removed preference(s): {', '.join(removed)}."
            else:
                confirmation_msg = "Updated preferences."

        elif intent.action == "remove_activity":
            # Filter out specified preferences or activity keywords
            for act in intent.remove_activity_names:
                preferences = [p for p in preferences if p.lower() != act.lower()]
            confirmation_msg = "Updated trip to adjust activities."

        elif intent.action in ("change_transport_preference", "change_accommodation_preference"):
            if intent.requested_transport_preference:
                pref = intent.requested_transport_preference.lower()
                if pref not in preferences:
                    preferences.append(pref)
            if intent.requested_accommodation_preference:
                pref = intent.requested_accommodation_preference.lower()
                if pref not in preferences:
                    preferences.append(pref)
            confirmation_msg = "Updated transport/accommodation preferences."

        elif intent.action == "optimize_budget":
            # Lower budget slightly by 15% to optimize spend
            budget = round(max(budget * 0.85, 5000.0), 2)
            confirmation_msg = f"Optimized trip budget breakdown to target ₹{budget:,.2f}."

        elif intent.action == "regenerate_itinerary":
            confirmation_msg = "Regenerated trip itinerary."

        # Construct updated input dict for run_trip_workflow
        new_trip_input = {
            "origin": origin,
            "destination": destination,
            "start_date": s_date.strftime("%Y-%m-%d"),
            "end_date": e_date.strftime("%Y-%m-%d"),
            "budget": budget,
            "travelers": travelers,
            "preferences": preferences,
        }

        # Execute deterministic LangGraph workflow
        wf_result = run_trip_workflow(new_trip_input)

        if wf_result.get("status") == "error":
            return {
                "status": "error",
                "error": wf_result.get("error"),
                "intent": intent.model_dump(mode="json"),
            }

        return {
            "status": "success",
            "intent": intent.model_dump(mode="json"),
            "trip": wf_result["trip_request"].model_dump(mode="json") if wf_result.get("trip_request") else new_trip_input,
            "plan": {
                "duration_days": wf_result.get("duration_days"),
                "duration_nights": wf_result.get("duration_nights"),
                "transport": wf_result["transport_results"].model_dump(mode="json") if wf_result.get("transport_results") else None,
                "accommodation": wf_result["accommodation_results"].model_dump(mode="json") if wf_result.get("accommodation_results") else None,
                "destination": wf_result["destination_results"].model_dump(mode="json") if wf_result.get("destination_results") else None,
                "budget": wf_result["budget_result"].model_dump(mode="json") if wf_result.get("budget_result") else None,
                "itinerary": wf_result["itinerary_result"].model_dump(mode="json") if wf_result.get("itinerary_result") else None,
            },
            "message": confirmation_msg,
        }
