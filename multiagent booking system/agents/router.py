"""
Router Agent — classifies the customer's intent and sets current_agent.

Design decisions
────────────────
1. booking_stage takes priority — if a booking flow is already in progress
   (collecting_info or showing_options), always route to the booking agent
   without calling the LLM.

2. The router passes recent conversation history to the LLM so that
   short follow-up replies like "London" or "22nd Feb" are classified
   correctly in context.

3. The router does NOT add a visible message to the conversation.
   It only updates query_type and current_agent in the state.
   Users should only see messages from specialist agents.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from models.state import TravelAgentState
from utils.graph_utils import update_state_field


class RouterAgent:

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini", temperature=0.0)

        self.routing_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a travel customer service router.

Given the conversation history and the latest customer message, choose ONE agent:

  booking     — customer wants to search, book, or select a flight or hotel
  complaint   — customer has a complaint, cancellation, refund, or service issue
  information — customer only wants general travel information with no booking intent

IMPORTANT RULES:
- If the customer mentions a city, date, or number of passengers → booking
- If the customer says yes/ok/confirm/sounds good after seeing options → booking
- When in doubt between booking and information → choose booking
- Default to booking for short or ambiguous replies if the history is about flights

Return ONLY valid JSON, no markdown:
{{"agent": "booking"|"complaint"|"information", "confidence": 0.0-1.0}}"""),
            ("user", "Recent conversation:\n{history}\n\nLatest message: {query}"),
        ])

        self.parser = JsonOutputParser()

    # ── helpers ────────────────────────────────────────────────────────────

    def _recent_history(self, state: TravelAgentState) -> str:
        """Return the last 4 messages as plain text for routing context."""
        lines = []
        for msg in state["messages"][-4:]:
            role = "Customer" if msg["role"] == "user" else "Agent"
            lines.append(f"{role}: {msg['content'][:120]}")
        return "\n".join(lines) if lines else "(start of conversation)"

    def _keyword_route(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["book", "reserve", "flight", "fly", "ticket", "hotel", "trip", "travel", "seat", "passenger"]):
            return "booking"
        if any(w in q for w in ["complaint", "problem", "cancel", "refund", "delay", "wrong", "issue"]):
            return "complaint"
        return "booking"   # safer default than information

    # ── main ──────────────────────────────────────────────────────────────

    def route_query(self, state: TravelAgentState) -> TravelAgentState:
        """
        Determine which specialist agent should handle this turn.

        Priority order:
          1. booking_stage — if mid-booking flow, always route to booking
          2. LLM classification with conversation history
          3. Keyword fallback if LLM fails
        """
        booking_stage = state["booking_info"].get("booking_stage", "collecting_info")

        # ── Rule 1: honour in-progress booking flows ───────────────────────
        if booking_stage in ("collecting_info", "showing_options"):
            agent = "booking"

        else:
            # ── Rule 2: LLM classification with history ────────────────────
            try:
                chain  = self.routing_prompt | self.llm | self.parser
                result = chain.invoke({
                    "query":   state["current_query"],
                    "history": self._recent_history(state),
                })
                agent = result.get("agent", "booking")
                if agent not in ("booking", "complaint", "information"):
                    agent = "booking"
            except Exception as e:
                print(f"[Router] LLM error: {e} — falling back to keywords")
                agent = self._keyword_route(state["current_query"])

        # Update routing fields in state — NO visible message added
        state = update_state_field(state, "query_type",    agent)
        state = update_state_field(state, "current_agent", agent)

        print(f"[Router] stage={booking_stage!r} → agent={agent!r}")
        return state
