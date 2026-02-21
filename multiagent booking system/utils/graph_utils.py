"""
Utility functions for graph operations and state management
"""

from typing import Any, Dict
from datetime import datetime
import uuid

from models.state import TravelAgentState, ConversationMessage, CustomerInfo, TravelBooking


def create_initial_state(query: str, session_id: str = None) -> TravelAgentState:
    """Create a blank initial state for a brand-new conversation."""
    if session_id is None:
        session_id = str(uuid.uuid4())

    return TravelAgentState(
        customer_info=CustomerInfo(
            customer_id=None,
            name=None,
            email=None,
            phone=None,
            preferences={},
        ),
        messages=[],
        current_query=query,
        query_type=None,
        current_agent=None,
        agent_responses={},
        booking_info=TravelBooking(
            booking_id=None,
            booking_stage="collecting_info",
            booking_status="pending",
            origin=None,
            destination=None,
            departure_date=None,
            return_date=None,
            travelers=1,
            cabin_class="Economy",
            selected_flight_id=None,
            flight_number=None,
            airline=None,
            price=None,
            currency=None,
        ),
        is_complete=False,
        error_message=None,
        session_id=session_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def resume_state(query: str, previous: dict) -> TravelAgentState:
    """
    Build a state that continues an existing conversation loaded from SQLite.

    Carries forward:
      - All previous messages (full history)
      - Accumulated booking_info (origin, destination, date, class, etc.)
      - Session metadata (session_id, created_at)
    """
    state = create_initial_state(query, previous["session_id"])
    state["messages"]     = previous["messages"]
    state["booking_info"] = previous["booking_info"]
    state["created_at"]   = previous["created_at"]
    state["is_complete"]  = False   # reset so the graph processes the new turn

    # Restore cached flight results so flight selection works across turns
    if previous.get("last_flights_json"):
        state["agent_responses"]["last_flights_json"] = previous["last_flights_json"]

    return state


def add_message_to_state(
    state: TravelAgentState,
    role: str,
    content: str,
    agent_name: str = None,
) -> TravelAgentState:
    """Append a message to the conversation history."""
    new_message = ConversationMessage(
        role=role,
        content=content,
        timestamp=datetime.now(),
        agent_name=agent_name,
    )
    updated = state.copy()
    updated["messages"]   = state["messages"] + [new_message]
    updated["updated_at"] = datetime.now()
    return updated


def update_state_field(state: TravelAgentState, field: str, value: Any) -> TravelAgentState:
    """Return a copy of state with one field replaced."""
    updated = state.copy()
    updated[field]        = value
    updated["updated_at"] = datetime.now()
    return updated
