#!/usr/bin/env python3
"""
Travel Customer Management Multi-Agent System
Main application entry point with FastAPI interface.

Session state is persisted in SQLite (sessions.db) via db/session_store.py
so that multi-turn conversations survive server restarts.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

from graph import TravelMultiAgentGraph
from models.state import TravelAgentState, ConversationMessage
from db.session_store import init_db, load_session, save_session, delete_session, list_sessions, cleanup_old_sessions

load_dotenv()

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Travel Customer Management System",
    description="Multi-agent system for handling travel customer queries using LangGraph",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    graph = TravelMultiAgentGraph()
except ValueError as e:
    print(f"Error initialising graph: {e}")
    print("Please set your OPENAI_API_KEY environment variable")
    exit(1)


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message:    str            = Field(..., description="Customer's message or query")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    response:     str                      = Field(..., description="Agent's response")
    session_id:   str                      = Field(..., description="Session ID — pass this back on the next turn")
    agent_used:   Optional[str]            = Field(None, description="Which agent handled the request")
    is_complete:  bool                     = Field(..., description="Whether this booking flow is complete")
    booking_info: Optional[Dict[str, Any]] = Field(None, description="Current booking state")
    booking_stage: Optional[str]           = Field(None, description="collecting_info | showing_options | confirmed")


class ConversationHistory(BaseModel):
    session_id: str
    messages:   List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status:    str = "healthy"
    timestamp: datetime
    version:   str = "2.0.0"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", timestamp=datetime.now(), version="2.0.0")


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Main chat endpoint.

    On the first turn omit session_id (or pass null).
    On follow-up turns pass the session_id returned from the previous response
    — the agent will remember everything collected so far.
    """
    try:
        # ── Resolve session ────────────────────────────────────────────────
        session_id       = request.session_id
        previous_session = None

        if session_id:
            previous_session = load_session(session_id)

        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # ── Run the graph ──────────────────────────────────────────────────
        result_state = graph.process_query(
            query=request.message,
            session_id=session_id,
            previous_session=previous_session,
        )

        # ── Persist updated state to SQLite ────────────────────────────────
        created_at = previous_session["created_at"] if previous_session else None
        save_session(session_id, result_state, created_at=created_at)

        # ── Build response — skip internal router messages ─────────────────
        agent_msgs = [
            m for m in result_state["messages"]
            if m["role"] == "agent" and m.get("agent_name") != "router"
        ]
        latest_response = agent_msgs[-1]["content"] if agent_msgs else "I couldn't process your request."

        booking      = result_state["booking_info"]
        booking_info = {k: v for k, v in booking.items() if v is not None} or None

        background_tasks.add_task(cleanup_old_sessions)

        return ChatResponse(
            response=latest_response,
            session_id=session_id,
            agent_used=result_state.get("current_agent"),
            is_complete=result_state["is_complete"],
            booking_info=booking_info,
            booking_stage=booking.get("booking_stage"),
        )

    except Exception as e:
        print(f"[main] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{session_id}", response_model=ConversationHistory)
async def get_conversation_history(session_id: str):
    """Retrieve the full message history for a session."""
    session = load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return ConversationHistory(
        session_id=session_id,
        messages=[
            {
                "role":       m["role"],
                "content":    m["content"],
                "timestamp":  m["timestamp"].isoformat(),
                "agent_name": m.get("agent_name"),
            }
            for m in session["messages"]
        ],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
    )


@app.delete("/conversation/{session_id}")
async def delete_conversation(session_id: str):
    """Delete a session and all its messages from SQLite."""
    if not delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Conversation deleted successfully"}


@app.get("/sessions")
async def list_all_sessions():
    """List all active sessions stored in SQLite."""
    rows = list_sessions()
    return {"sessions": rows, "total": len(rows)}


# ---------------------------------------------------------------------------
# Lifecycle events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    init_db()   # creates sessions.db tables if they don't exist
    print("Travel Customer Management Multi-Agent System — ready")
    print("SQLite session store active (sessions.db)")


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 9090))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    print(f"Starting server on port {port}")
    print(f"API docs: http://localhost:{port}/docs")

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug, log_level="info")
