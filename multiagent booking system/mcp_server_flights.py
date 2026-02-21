"""
MCP Flights Server — SQLite-backed flight search for the Travel Agent demo.

Exposes three tools:
  search_flights       — find flights by origin / destination / date
  get_flight_details   — full record for a specific flight ID
  check_seat_availability — remaining seats for a flight

Run standalone:
  python mcp_server_flights.py          # stdio (used by booking agent)
  MCP_TRANSPORT=sse python mcp_server_flights.py   # SSE on port 9001
"""

import json
import os
import sqlite3
from pathlib import Path

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# FastMCP instance
# ---------------------------------------------------------------------------

mcp = FastMCP("Flight Database")
DEFAULT_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")

DB_PATH = Path(__file__).parent / "flights.db"


# ---------------------------------------------------------------------------
# Database setup — creates and seeds the DB on every server start
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create the flights table and insert sample data."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS flights")

    cur.execute("""
        CREATE TABLE flights (
            id               INTEGER PRIMARY KEY,
            flight_number    TEXT    NOT NULL,
            airline          TEXT    NOT NULL,
            origin           TEXT    NOT NULL,
            destination      TEXT    NOT NULL,
            departure_date   TEXT    NOT NULL,   -- YYYY-MM-DD
            departure_time   TEXT    NOT NULL,   -- HH:MM
            arrival_time     TEXT    NOT NULL,   -- HH:MM (next-day if +1)
            duration         TEXT    NOT NULL,
            cabin_class      TEXT    NOT NULL,   -- Economy | Business
            price            REAL    NOT NULL,
            currency         TEXT    NOT NULL,
            total_seats      INTEGER NOT NULL,
            available_seats  INTEGER NOT NULL
        )
    """)

    # ------------------------------------------------------------------
    # Sample data — Delhi → London (21, 22, 23 Feb 2026)
    # ------------------------------------------------------------------
    flights = [
        # --- Delhi → London ---
        # 21 Feb
        ("AI101", "Air India",       "Delhi", "London", "2026-02-21", "08:00", "14:30", "9h 30m", "Economy",  650.00, "GBP", 180,  45),
        ("AI101", "Air India",       "Delhi", "London", "2026-02-21", "08:00", "14:30", "9h 30m", "Business",1200.00, "GBP",  60,  12),
        ("BA307", "British Airways", "Delhi", "London", "2026-02-21", "14:00", "20:30", "9h 30m", "Economy",  780.00, "GBP", 200,  67),
        ("BA307", "British Airways", "Delhi", "London", "2026-02-21", "14:00", "20:30", "9h 30m", "Business",1800.00, "GBP",  40,   5),
        # 22 Feb
        ("AI103", "Air India",       "Delhi", "London", "2026-02-22", "10:00", "16:30", "9h 30m", "Economy",  580.00, "GBP", 180, 112),
        ("BA309", "British Airways", "Delhi", "London", "2026-02-22", "16:00", "22:30", "9h 30m", "Economy",  695.00, "GBP", 200,  88),
        ("BA309", "British Airways", "Delhi", "London", "2026-02-22", "16:00", "22:30", "9h 30m", "Business",1650.00, "GBP",  40,  18),
        # 23 Feb
        ("AI105", "Air India",       "Delhi", "London", "2026-02-23", "21:00", "03:30", "9h 30m", "Economy",  720.00, "GBP", 180,   8),
        ("BA311", "British Airways", "Delhi", "London", "2026-02-23", "09:00", "15:30", "9h 30m", "Economy",  850.00, "GBP", 200, 134),
        ("BA311", "British Airways", "Delhi", "London", "2026-02-23", "09:00", "15:30", "9h 30m", "Business",1950.00, "GBP",  40,  22),

        # --- Delhi → Paris ---
        # 21 Feb
        ("AF201", "Air France", "Delhi", "Paris", "2026-02-21", "09:30", "15:00", "8h 30m", "Economy",   590.00, "EUR", 160,  34),
        ("AF201", "Air France", "Delhi", "Paris", "2026-02-21", "09:30", "15:00", "8h 30m", "Business", 1400.00, "EUR",  45,   7),
        ("AI301", "Air India",  "Delhi", "Paris", "2026-02-21", "13:00", "18:30", "8h 30m", "Economy",   520.00, "EUR", 160,  56),
        # 22 Feb
        ("AF203", "Air France", "Delhi", "Paris", "2026-02-22", "11:00", "16:30", "8h 30m", "Economy",   540.00, "EUR", 160,  89),
        ("AF203", "Air France", "Delhi", "Paris", "2026-02-22", "11:00", "16:30", "8h 30m", "Business", 1350.00, "EUR",  45,  14),
        ("AI303", "Air India",  "Delhi", "Paris", "2026-02-22", "20:00", "01:30", "8h 30m", "Economy",   480.00, "EUR", 160, 102),
        # 23 Feb
        ("AF205", "Air France", "Delhi", "Paris", "2026-02-23", "22:30", "04:00", "8h 30m", "Economy",   610.00, "EUR", 160,  21),
        ("AI305", "Air India",  "Delhi", "Paris", "2026-02-23", "07:00", "12:30", "8h 30m", "Economy",   560.00, "EUR", 160,  45),
        ("AI305", "Air India",  "Delhi", "Paris", "2026-02-23", "07:00", "12:30", "8h 30m", "Business", 1250.00, "EUR",  45,   9),
    ]

    cur.executemany("""
        INSERT INTO flights
            (flight_number, airline, origin, destination, departure_date,
             departure_time, arrival_time, duration, cabin_class,
             price, currency, total_seats, available_seats)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, flights)

    conn.commit()
    conn.close()
    print(f"[MCP Flights] Database initialised at {DB_PATH} with {len(flights)} flights.")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# Seed on import so the DB is ready before any tool is called
init_db()


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search for available flights between two cities on a given date.

    Args:
        origin     : Departure city (e.g. 'Delhi').
        destination: Arrival city   (e.g. 'London' or 'Paris').
        date       : Travel date in YYYY-MM-DD format (e.g. '2026-02-21').

    Returns:
        JSON list of matching flights with prices and seat availability.
    """
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT id, flight_number, airline, origin, destination,
                   departure_date, departure_time, arrival_time, duration,
                   cabin_class, price, currency, available_seats
            FROM   flights
            WHERE  LOWER(origin)       = LOWER(?)
            AND    LOWER(destination)  = LOWER(?)
            AND    departure_date      = ?
            AND    available_seats     > 0
            ORDER  BY cabin_class, price
        """, (origin, destination, date))

        rows = [dict(r) for r in cur.fetchall()]
        conn.close()

        if not rows:
            return (
                f"No flights found from {origin} to {destination} on {date}. "
                f"Available routes: Delhi→London, Delhi→Paris. "
                f"Available dates: 2026-02-21, 2026-02-22, 2026-02-23."
            )

        return json.dumps(rows, indent=2)

    except Exception as exc:
        return f"Error searching flights: {exc}"


@mcp.tool()
def get_flight_details(flight_id: int) -> str:
    """Get complete details for a specific flight by its database ID.

    Args:
        flight_id: The numeric flight ID returned by search_flights.

    Returns:
        Full flight record as JSON, including total and available seats.
    """
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return f"No flight found with ID {flight_id}."

        return json.dumps(dict(row), indent=2)

    except Exception as exc:
        return f"Error fetching flight details: {exc}"


@mcp.tool()
def check_seat_availability(flight_id: int) -> str:
    """Check how many seats are still available on a specific flight.

    Args:
        flight_id: The numeric flight ID.

    Returns:
        Seat availability summary.
    """
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT flight_number, airline, departure_date, departure_time,
                   cabin_class, total_seats, available_seats
            FROM   flights
            WHERE  id = ?
        """, (flight_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return f"No flight found with ID {flight_id}."

        r = dict(row)
        booked = r["total_seats"] - r["available_seats"]
        pct    = round(booked / r["total_seats"] * 100)

        return (
            f"Flight {r['flight_number']} ({r['airline']}) — "
            f"{r['departure_date']} {r['departure_time']} — {r['cabin_class']}\n"
            f"  Total seats    : {r['total_seats']}\n"
            f"  Booked         : {booked} ({pct}% full)\n"
            f"  Available      : {r['available_seats']}\n"
            f"  Status         : {'Almost full — book soon!' if r['available_seats'] < 15 else 'Good availability'}"
        )

    except Exception as exc:
        return f"Error checking availability: {exc}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if DEFAULT_TRANSPORT == "sse":
        mcp.run(transport="sse", port=9001)
    else:
        mcp.run()
