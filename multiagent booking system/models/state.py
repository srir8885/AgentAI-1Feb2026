from typing import List, Optional, Dict, Any, TypedDict
from datetime import datetime


class CustomerInfo(TypedDict):
    """Customer information structure"""
    customer_id: Optional[str]
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    preferences: Dict[str, Any]


class TravelBooking(TypedDict):
    """
    Travel booking information.

    Extended to support multi-turn follow-up conversations:
      - origin / cabin_class collected across turns
      - booking_stage tracks where in the flow we are
      - selected_flight_id / flight_number / airline set after user picks
    """
    booking_id:          Optional[str]
    booking_stage:       str   # collecting_info | showing_options | confirmed
    booking_status:      str   # pending | confirmed | cancelled

    # Route
    origin:              Optional[str]
    destination:         Optional[str]
    departure_date:      Optional[str]
    return_date:         Optional[str]

    # Preferences
    travelers:           int
    cabin_class:         str   # Economy | Business

    # Selected flight (set once user chooses)
    selected_flight_id:  Optional[int]
    flight_number:       Optional[str]
    airline:             Optional[str]
    price:               Optional[float]
    currency:            Optional[str]


class ConversationMessage(TypedDict):
    """Individual message in conversation"""
    role: str          # "user" | "agent" | "assistant"
    content: str
    timestamp: datetime
    agent_name: Optional[str]


class TravelAgentState(TypedDict):
    """Main state for the travel customer management system"""
    # Customer information
    customer_info: CustomerInfo

    # Full conversation history
    messages: List[ConversationMessage]

    # Current query and context
    current_query: str
    query_type: Optional[str]   # booking | complaint | information | general

    # Agent routing
    current_agent: Optional[str]
    agent_responses: Dict[str, Any]

    # Travel booking data
    booking_info: TravelBooking

    # System state
    is_complete: bool
    error_message: Optional[str]

    # Metadata
    session_id: str
    created_at: datetime
    updated_at: datetime
