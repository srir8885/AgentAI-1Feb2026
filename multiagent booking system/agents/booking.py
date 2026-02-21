"""
Booking Agent — multi-turn flight booking with SQLite-backed persistent state.

Conversation stages
───────────────────
  collecting_info  → ask for any missing required fields (destination, date)
  showing_options  → flights shown; waiting for user to pick one
  confirmed        → user picked a flight; booking confirmed

Flight data comes from mcp_server_flights.py (SQLite via MCP).
Conversation state persists across turns via session_store.py (SQLite).
"""

import asyncio
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from models.state import TravelAgentState, TravelBooking
from utils.graph_utils import add_message_to_state, update_state_field

_MCP_SERVER = str(Path(__file__).parent.parent / "mcp_server_flights.py")

AVAILABLE_DESTINATIONS = ["London", "Paris"]
AVAILABLE_DATES        = ["2026-02-21", "2026-02-22", "2026-02-23"]
DATE_LABELS            = {"2026-02-21": "21 Feb (Sat)", "2026-02-22": "22 Feb (Sun)", "2026-02-23": "23 Feb (Mon)"}


# ---------------------------------------------------------------------------
# Flight MCP Client (async → sync bridge)
# ---------------------------------------------------------------------------

class FlightMCPClient:
    """Wraps the async MCP stdio client as plain synchronous methods."""

    def __init__(self, server_script: str = _MCP_SERVER):
        self.server_script = server_script

    def _run(self, coro) -> str:
        """Execute coroutine in a fresh thread — safe from any async context."""
        with ThreadPoolExecutor(max_workers=1) as ex:
            return ex.submit(asyncio.run, coro).result()

    async def _call(self, tool: str, args: dict) -> str:
        params = StdioServerParameters(command=sys.executable, args=[self.server_script])
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments=args)
                return result.content[0].text if result.content else ""

    def search_flights(self, origin: str, destination: str, date: str) -> str:
        return self._run(self._call("search_flights", {"origin": origin, "destination": destination, "date": date}))

    def get_flight_details(self, flight_id: int) -> str:
        return self._run(self._call("get_flight_details", {"flight_id": flight_id}))


# ---------------------------------------------------------------------------
# Booking Agent
# ---------------------------------------------------------------------------

class BookingAgent:

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini", temperature=0.2)
        self.flight_client = FlightMCPClient()
        self.parser = JsonOutputParser()

        # ── Prompt: extract fields from the latest user message ───────────
        self.extract_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract travel booking information from the customer message.
Return ONLY a JSON object — no markdown — with these keys (null if not mentioned):
{{
  "origin"         : "departure city — use 'Delhi' if they mention only a destination",
  "destination"    : "arrival city e.g. London or Paris",
  "departure_date" : "ISO date YYYY-MM-DD (21/22/23 Feb 2026 → 2026-02-21/22/23)",
  "return_date"    : "ISO date or null",
  "travelers"      : integer or null,
  "cabin_class"    : "Economy or Business or null",
  "flight_number"  : "e.g. AI103 — if user is selecting a specific flight",
  "flight_id"      : integer — if user says 'flight ID 5' or 'book ID 3'
}}"""),
            ("user", "Conversation so far:\n{history}\n\nLatest message: {query}"),
        ])

        # ── Prompt: format flight results into a nice message ─────────────
        self.options_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a friendly travel booking assistant.
The customer wants to fly from {origin} to {destination} on {date}.

Here are the available flights from our database:
{flights}

Write a clear, friendly response that:
1. Confirms the route and date
2. Shows flights as a numbered list: flight number, airline, time, cabin, price, seats left
3. Highlights the best-value Economy option
4. Ends with: "Reply with the flight number (e.g. AI103) or the list number to book."
Keep it concise."""),
            ("user", "Show me the available flights."),
        ])

        # ── Prompt: confirm booking ────────────────────────────────────────
        self.confirm_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are confirming a flight booking. Write a warm, professional confirmation:

Flight details:
{flight_details}

Booking reference: {booking_id}

Include:
- Route, date, time, cabin, price
- Booking reference
- Next steps (check-in opens 24h before, arrive 3h early for international)
- Ask if they need anything else (hotel, return flight, etc.)"""),
            ("user", "Confirm my booking."),
        ])

    # ── Helpers ────────────────────────────────────────────────────────────

    def _history_text(self, state: TravelAgentState) -> str:
        """Format the last 6 messages as plain text for the extraction prompt."""
        lines = []
        for msg in state["messages"][-6:]:
            role = "Customer" if msg["role"] == "user" else "Agent"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines) if lines else "(none)"

    def _extract_intent(self, query: str, state: TravelAgentState) -> dict:
        try:
            chain  = self.extract_prompt | self.llm | self.parser
            result = chain.invoke({"query": query, "history": self._history_text(state)})
            return result if isinstance(result, dict) else {}
        except Exception as e:
            print(f"[BookingAgent] Extract error: {e}")
            return {}

    def _merge_booking(self, existing: TravelBooking, new: dict) -> TravelBooking:
        """Merge newly extracted fields on top of what we already know."""
        updated = existing.copy()
        for field in ("origin", "destination", "departure_date", "return_date", "cabin_class"):
            if new.get(field):
                updated[field] = new[field]
        if new.get("travelers"):
            updated["travelers"] = int(new["travelers"])
        # Default origin to Delhi if still missing
        if not updated.get("origin"):
            updated["origin"] = "Delhi"
        if not updated.get("cabin_class"):
            updated["cabin_class"] = "Economy"
        if not updated.get("travelers"):
            updated["travelers"] = 1
        return updated

    def _missing_fields(self, booking: TravelBooking) -> List[str]:
        missing = []
        if not booking.get("destination"):
            missing.append("destination")
        if not booking.get("departure_date"):
            missing.append("departure_date")
        return missing

    def _ask_for_missing(self, missing: List[str], booking: TravelBooking) -> str:
        """Generate a contextual question for the first missing field."""
        field = missing[0]
        dest  = booking.get("destination", "")
        orig  = booking.get("origin") or "Delhi"

        if field == "destination":
            return (
                f"I'd love to help you book a flight from {orig}!\n\n"
                f"Where would you like to fly to?\n"
                f"  • London\n"
                f"  • Paris"
            )

        if field == "departure_date":
            return (
                f"Great — {orig} to {dest}! Which date would you like to travel?\n\n"
                f"  • 21 Feb 2026 (Saturday)\n"
                f"  • 22 Feb 2026 (Sunday)\n"
                f"  • 23 Feb 2026 (Monday)\n\n"
                f"Also, how many passengers and which cabin — Economy or Business? "
                f"(defaults: 1 passenger, Economy)"
            )

        return f"Could you please tell me your {field.replace('_', ' ')}?"

    def _detect_flight_selection(self, query: str, intent: dict) -> Optional[dict]:
        """
        Return flight selection info if the user is picking a flight.
        Checks extracted intent first, then falls back to regex on the raw query.
        """
        # From LLM extraction
        if intent.get("flight_id"):
            return {"flight_id": int(intent["flight_id"])}
        if intent.get("flight_number"):
            return {"flight_number": intent["flight_number"].upper()}

        # Regex fallback
        q = query.upper().strip()
        fn = re.search(r'\b([A-Z]{2}\d{3,4})\b', q)
        if fn:
            return {"flight_number": fn.group(1)}

        fid = re.search(r'\b(?:ID|NUMBER)?\s*(\d{1,3})\b', q)
        if fid:
            return {"flight_id": int(fid.group(1))}

        return None

    def _format_flights(self, raw_json: str) -> str:
        """Turn the MCP JSON into a numbered human-readable list."""
        try:
            flights = json.loads(raw_json)
            if not isinstance(flights, list) or not flights:
                return raw_json
            lines = []
            for i, f in enumerate(flights, 1):
                seats_warn = " ⚠ Only a few left!" if f["available_seats"] < 15 else ""
                lines.append(
                    f"  {i}. {f['flight_number']} ({f['airline']})  "
                    f"{f['departure_time']}→{f['arrival_time']}  "
                    f"{f['cabin_class']}  "
                    f"{f['currency']} {f['price']:.0f}  "
                    f"[{f['available_seats']} seats{seats_warn}]  "
                    f"(ID: {f['id']})"
                )
            return "\n".join(lines)
        except Exception:
            return raw_json

    def _find_flight_by_number(self, flights_json: str, flight_number: str) -> Optional[dict]:
        try:
            for f in json.loads(flights_json):
                if f["flight_number"].upper() == flight_number.upper():
                    return f
        except Exception:
            pass
        return None

    def _find_flight_by_id(self, flights_json: str, flight_id: int) -> Optional[dict]:
        try:
            for f in json.loads(flights_json):
                if f["id"] == flight_id:
                    return f
        except Exception:
            pass
        return None

    def _find_flight_by_list_number(self, flights_json: str, num: int) -> Optional[dict]:
        """User said '1' or '2' — pick by position in the list."""
        try:
            flights = json.loads(flights_json)
            if 1 <= num <= len(flights):
                return flights[num - 1]
        except Exception:
            pass
        return None

    def _make_booking_id(self) -> str:
        return f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # ── Main entry point ───────────────────────────────────────────────────

    def process_booking_request(self, state: TravelAgentState) -> TravelAgentState:
        """
        Drive the booking conversation through three stages:

          collecting_info  → ask for missing fields one at a time
          showing_options  → search MCP for real flights and present them
          confirmed        → user picked a flight; write the confirmation
        """
        query   = state["current_query"]
        booking = state["booking_info"]
        stage   = booking.get("booking_stage", "collecting_info")

        try:
            # ── Extract any new info the user just provided ────────────────
            intent = self._extract_intent(query, state)
            booking = self._merge_booking(booking, intent)
            state   = update_state_field(state, "booking_info", booking)

            # ── Stage: confirmed — user is picking a flight ────────────────
            if stage == "showing_options":
                selection = self._detect_flight_selection(query, intent)
                if selection:
                    return self._handle_flight_selection(state, booking, selection)

            # ── Stage: collecting_info — ask for missing required fields ───
            missing = self._missing_fields(booking)
            if missing:
                booking["booking_stage"] = "collecting_info"
                state = update_state_field(state, "booking_info", booking)
                response = self._ask_for_missing(missing, booking)
                return add_message_to_state(state, "agent", response, "booking_agent")

            # ── All fields present — search flights via MCP ────────────────
            return self._show_flight_options(state, booking)

        except Exception as exc:
            print(f"[BookingAgent] Error: {exc}")
            return add_message_to_state(
                state, "agent",
                "I'm sorry, something went wrong. Could you repeat your travel details? "
                "(e.g. 'Delhi to London on 22 Feb, 1 passenger, Economy')",
                "booking_agent",
            )

    def _show_flight_options(self, state: TravelAgentState, booking: TravelBooking) -> TravelAgentState:
        """Search MCP for flights and present numbered options to the user."""
        origin = booking["origin"] or "Delhi"
        dest   = booking["destination"]
        date   = booking["departure_date"]

        print(f"[BookingAgent] MCP search: {origin} → {dest} on {date}")
        raw_flights = self.flight_client.search_flights(origin, dest, date)

        # Store raw JSON in agent_responses for the selection step
        state["agent_responses"]["last_flights_json"] = raw_flights

        formatted = self._format_flights(raw_flights)

        # Update stage
        booking = booking.copy()
        booking["booking_stage"] = "showing_options"
        state = update_state_field(state, "booking_info", booking)

        response_chain = self.options_prompt | self.llm
        resp = response_chain.invoke({
            "origin":      origin,
            "destination": dest,
            "date":        DATE_LABELS.get(date, date),
            "flights":     formatted,
        })
        return add_message_to_state(state, "agent", resp.content, "booking_agent")

    def _handle_flight_selection(
        self, state: TravelAgentState, booking: TravelBooking, selection: dict
    ) -> TravelAgentState:
        """User selected a specific flight — confirm the booking."""
        raw_flights = state["agent_responses"].get("last_flights_json", "[]")
        flight = None

        if "flight_number" in selection:
            flight = self._find_flight_by_number(raw_flights, selection["flight_number"])
        elif "flight_id" in selection:
            fid = selection["flight_id"]
            # Try by DB id first, then by list position
            flight = self._find_flight_by_id(raw_flights, fid) or \
                     self._find_flight_by_list_number(raw_flights, fid)

        if not flight:
            return add_message_to_state(
                state, "agent",
                "I couldn't find that flight in the options shown. "
                "Please reply with the flight number (e.g. AI103) or list number (e.g. 1).",
                "booking_agent",
            )

        # Confirm the booking
        booking_id = self._make_booking_id()
        booking = booking.copy()
        booking.update({
            "booking_id":         booking_id,
            "booking_stage":      "confirmed",
            "booking_status":     "confirmed",
            "selected_flight_id": flight["id"],
            "flight_number":      flight["flight_number"],
            "airline":            flight["airline"],
            "price":              flight["price"],
            "currency":           flight["currency"],
        })
        state = update_state_field(state, "booking_info", booking)

        flight_detail_str = (
            f"Flight : {flight['flight_number']} ({flight['airline']})\n"
            f"Route  : {flight['origin']} → {flight['destination']}\n"
            f"Date   : {DATE_LABELS.get(flight['departure_date'], flight['departure_date'])}\n"
            f"Time   : {flight['departure_time']} → {flight['arrival_time']} ({flight['duration']})\n"
            f"Cabin  : {flight['cabin_class']}\n"
            f"Price  : {flight['currency']} {flight['price']:.0f}\n"
            f"Seats  : {flight['available_seats']} remaining"
        )

        confirm_chain = self.confirm_prompt | self.llm
        resp = confirm_chain.invoke({
            "flight_details": flight_detail_str,
            "booking_id":     booking_id,
        })
        return add_message_to_state(state, "agent", resp.content, "booking_agent")

    def confirm_booking(self, state: TravelAgentState) -> TravelAgentState:
        """Legacy method — delegates to process_booking_request."""
        return self.process_booking_request(state)
