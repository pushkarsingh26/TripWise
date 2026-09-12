from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional
import copy

from app.models.language import ResponseLanguage
from app.models.modification import ModificationIntent
from app.models.trip import TripRequest
from app.workflows.trip_workflow import run_trip_workflow


class TripModifier:
    """
    Deterministic modification engine for Tripwise.
    Applies validated ModificationIntent to an existing trip request, re-runs the LangGraph workflow,
    and returns localized responses matching the detected language (English, Hindi, Hinglish).
    """

    def modify_trip(
        self,
        current_trip_dict: Dict[str, Any],
        intent: ModificationIntent,
    ) -> Dict[str, Any]:
        """
        Applies intent changes to current_trip_dict and returns the workflow result along with intent & localized message.
        """
        lang = intent.language or ResponseLanguage.ENGLISH

        if intent.confirmation_required or intent.action == "ambiguous_request":
            default_msg = "Modification request is ambiguous. Please clarify."
            if lang == ResponseLanguage.HINDI:
                default_msg = "संशोधन अनुरोध स्पष्ट नहीं है। कृपया अपना अनुरोध स्पष्ट करें।"
            elif lang == ResponseLanguage.HINGLISH:
                default_msg = "Modification request clear nahi hai. Please apna request clarify karein."

            return {
                "status": "needs_clarification",
                "intent": intent.model_dump(mode="json"),
                "trip": current_trip_dict,
                "plan": None,
                "message": intent.clarification_message or default_msg,
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
        if lang == ResponseLanguage.HINDI:
            confirmation_msg = "आपकी यात्रा योजना को आपके अनुरोध के अनुसार अपडेट कर दिया गया है।"
        elif lang == ResponseLanguage.HINGLISH:
            confirmation_msg = "Aapki trip plan aapke request ke according update kar di hai."

        # Apply intent actions deterministically
        if intent.action == "change_budget":
            if intent.new_budget is not None and intent.new_budget > 0:
                budget = float(intent.new_budget)
                if lang == ResponseLanguage.HINDI:
                    confirmation_msg = f"ट्रिप का कुल बजट बदलकर ₹{budget:,.2f} कर दिया गया है।"
                elif lang == ResponseLanguage.HINGLISH:
                    confirmation_msg = f"Trip ka total budget update karke ₹{budget:,.2f} kar diya hai."
                else:
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
                if lang == ResponseLanguage.HINDI:
                    confirmation_msg = f"ट्रिप की अवधि बदलकर {intent.new_duration_days} दिन कर दी गई है।"
                elif lang == ResponseLanguage.HINGLISH:
                    confirmation_msg = f"Trip duration update karke {intent.new_duration_days} days kar di hai."
                else:
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
                if lang == ResponseLanguage.HINDI:
                    confirmation_msg = f"गंतव्य बदलकर {destination} कर दिया गया है।"
                elif lang == ResponseLanguage.HINGLISH:
                    confirmation_msg = f"Destination change karke {destination} kar diya hai."
                else:
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
                if lang == ResponseLanguage.HINDI:
                    confirmation_msg = f"आपकी पसंद ({', '.join(added)}) जोड़ दी गई है।"
                elif lang == ResponseLanguage.HINGLISH:
                    confirmation_msg = f"Aapki preference ({', '.join(added)}) add kar di hai."
                else:
                    confirmation_msg = f"Added preference(s): {', '.join(added)}."

        elif intent.action == "remove_preference":
            removed = []
            for p in intent.remove_preferences:
                preferences = [existing for existing in preferences if existing.lower() != p.lower()]
                removed.append(p)
            if removed:
                if lang == ResponseLanguage.HINDI:
                    confirmation_msg = f"आपकी पसंद ({', '.join(removed)}) हटा दी गई है।"
                elif lang == ResponseLanguage.HINGLISH:
                    confirmation_msg = f"Preference ({', '.join(removed)}) remove kar di hai."
                else:
                    confirmation_msg = f"Removed preference(s): {', '.join(removed)}."

        elif intent.action == "remove_activity":
            for act in intent.remove_activity_names:
                preferences = [p for p in preferences if p.lower() != act.lower()]
            if lang == ResponseLanguage.HINDI:
                confirmation_msg = "ट्रिप में से मांगी गई गतिविधियां हटा दी गई हैं।"
            elif lang == ResponseLanguage.HINGLISH:
                confirmation_msg = "Trip me se requested activities adjust kar di hain."
            else:
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
            if lang == ResponseLanguage.HINDI:
                confirmation_msg = "परिवहन/आवास की प्राथमिकताओं को अपडेट कर दिया गया है।"
            elif lang == ResponseLanguage.HINGLISH:
                confirmation_msg = "Transport/accommodation preferences update kar diye hain."
            else:
                confirmation_msg = "Updated transport/accommodation preferences."

        elif intent.action == "optimize_budget":
            budget = round(max(budget * 0.85, 5000.0), 2)
            if lang == ResponseLanguage.HINDI:
                confirmation_msg = f"मैंने ट्रिप का बजट कम करके (लक्ष्य ₹{budget:,.2f}) आपकी योजना दोबारा तैयार कर दी है।"
            elif lang == ResponseLanguage.HINGLISH:
                confirmation_msg = f"Maine trip ka budget reduce karke (target ₹{budget:,.2f}) itinerary dobara generate kar di hai."
            else:
                confirmation_msg = f"Optimized trip budget breakdown to target ₹{budget:,.2f}."

        elif intent.action == "regenerate_itinerary":
            if lang == ResponseLanguage.HINDI:
                confirmation_msg = "ट्रिप की यात्रा योजना दोबारा तैयार कर दी गई है।"
            elif lang == ResponseLanguage.HINGLISH:
                confirmation_msg = "Trip ki itinerary dobara generate kar di hai."
            else:
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
