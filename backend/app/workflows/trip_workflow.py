from typing import Any, Dict, List, Optional, Union
from typing_extensions import TypedDict

# pyrefly: ignore [missing-import]
from langgraph.graph import END, START, StateGraph

from app.agents.accommodation_agent import AccommodationAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.destination_agent import DestinationAgent
from app.agents.itinerary_agent import ItineraryAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.transport_agent import TransportAgent
from app.models.accommodation import AccommodationResults
from app.models.budget import BudgetResult
from app.models.destination import DestinationResults
from app.models.itinerary import ItineraryResult
from app.models.transport import TransportResults
from app.models.trip import TripRequest


class TripWorkflowState(TypedDict):
    input_data: Union[str, Dict[str, Any]]
    status: str
    error: Optional[str]
    missing: Optional[List[str]]
    trip_request: Optional[TripRequest]
    duration_days: Optional[int]
    duration_nights: Optional[int]
    transport_results: Optional[TransportResults]
    accommodation_results: Optional[AccommodationResults]
    destination_results: Optional[DestinationResults]
    budget_result: Optional[BudgetResult]
    itinerary_result: Optional[ItineraryResult]


def planner_node(state: TripWorkflowState) -> Dict[str, Any]:
    agent = PlannerAgent()
    res = agent.process_request(state["input_data"])

    if res.get("status") == "error":
        return {
            "status": "error",
            "error": res.get("error"),
        }

    if res.get("status") == "needs_information":
        return {
            "status": "needs_information",
            "missing": res.get("missing"),
        }

    raw_trip = res["trip"]
    trip_req = TripRequest(**raw_trip)
    return {
        "status": "success",
        "trip_request": trip_req,
        "duration_days": res["duration_days"],
        "duration_nights": res["duration_nights"],
    }


def transport_node(state: TripWorkflowState) -> Dict[str, Any]:
    agent = TransportAgent()
    res = agent.get_transport_options(state["trip_request"])
    return {"transport_results": res}


def accommodation_node(state: TripWorkflowState) -> Dict[str, Any]:
    agent = AccommodationAgent()
    res = agent.get_accommodation_options(
        state["trip_request"], state["duration_nights"]
    )
    return {"accommodation_results": res}


def destination_node(state: TripWorkflowState) -> Dict[str, Any]:
    agent = DestinationAgent()
    res = agent.get_destination_recommendations(state["trip_request"])
    return {"destination_results": res}


def budget_node(state: TripWorkflowState) -> Dict[str, Any]:
    agent = BudgetAgent()
    res = agent.calculate_budget(
        state["trip_request"],
        state["transport_results"],
        state["accommodation_results"],
        state["destination_results"],
    )
    return {"budget_result": res}


def itinerary_node(state: TripWorkflowState) -> Dict[str, Any]:
    agent = ItineraryAgent()
    res = agent.generate_itinerary(
        state["trip_request"],
        state["destination_results"],
        state["budget_result"],
    )
    return {"itinerary_result": res}


def route_after_planner(state: TripWorkflowState) -> str:
    if state["status"] != "success":
        return END
    return "transport"


def build_trip_workflow():
    builder = StateGraph(TripWorkflowState)

    builder.add_node("planner", planner_node)
    builder.add_node("transport", transport_node)
    builder.add_node("accommodation", accommodation_node)
    builder.add_node("destination", destination_node)
    builder.add_node("budget", budget_node)
    builder.add_node("itinerary", itinerary_node)

    builder.add_edge(START, "planner")

    builder.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            END: END,
            "transport": "transport",
        },
    )

    # Parallel execution of options generation
    builder.add_edge("planner", "accommodation")
    builder.add_edge("planner", "destination")

    # Aggregate into budget and itinerary
    builder.add_edge(["transport", "accommodation", "destination"], "budget")
    builder.add_edge("budget", "itinerary")
    builder.add_edge("itinerary", END)

    return builder.compile()


_compiled_workflow = None


def get_trip_workflow():
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = build_trip_workflow()
    return _compiled_workflow


def run_trip_workflow(
    input_data: Union[str, Dict[str, Any]]
) -> TripWorkflowState:
    graph = get_trip_workflow()
    initial_state: TripWorkflowState = {
        "input_data": input_data,
        "status": "pending",
        "error": None,
        "missing": None,
        "trip_request": None,
        "duration_days": None,
        "duration_nights": None,
        "transport_results": None,
        "accommodation_results": None,
        "destination_results": None,
        "budget_result": None,
        "itinerary_result": None,
    }
    return graph.invoke(initial_state)
