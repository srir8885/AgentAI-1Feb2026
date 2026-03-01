"""Langfuse tracing integration — every agent call is traced end-to-end."""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator

from langfuse import Langfuse
from langfuse.callback import CallbackHandler as LangfuseCallbackHandler

from hotel_agent.config import settings

logger = logging.getLogger(__name__)

_langfuse: Langfuse | None = None


def get_langfuse() -> Langfuse:
    """Singleton Langfuse client."""
    global _langfuse
    if _langfuse is None:
        _langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
    return _langfuse


def create_langfuse_handler(
    trace_id: str,
    session_id: str = "",
    user_id: str = "",
) -> LangfuseCallbackHandler:
    """Create a LangChain callback handler that sends spans to Langfuse."""
    return LangfuseCallbackHandler(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
        trace_id=trace_id,
        session_id=session_id or None,
        user_id=user_id or None,
    )


def create_trace(
    name: str,
    session_id: str = "",
    user_id: str = "",
    input_data: Any = None,
    metadata: dict | None = None,
) -> Any:
    """Create a new Langfuse trace for a customer query."""
    lf = get_langfuse()
    trace = lf.trace(
        name=name,
        session_id=session_id or None,
        user_id=user_id or None,
        input=input_data,
        metadata=metadata or {},
    )
    logger.info("Created trace %s for session=%s", trace.id, session_id)
    return trace


def score_trace(trace_id: str, name: str, value: float, comment: str = "") -> None:
    """Attach a score to a trace (e.g. evaluation result)."""
    lf = get_langfuse()
    lf.score(
        trace_id=trace_id,
        name=name,
        value=value,
        comment=comment,
    )


@contextmanager
def traced_span(
    trace: Any,
    name: str,
    input_data: Any = None,
    metadata: dict | None = None,
) -> Generator[dict, None, None]:
    """Context manager that creates a Langfuse span and auto-closes it with timing.

    Usage:
        with traced_span(trace, "router") as span_ctx:
            result = do_work()
            span_ctx["output"] = result
    """
    span = trace.span(
        name=name,
        input=input_data,
        metadata=metadata or {},
    )
    ctx: dict[str, Any] = {"span": span, "output": None, "error": None}
    start = time.perf_counter()
    try:
        yield ctx
    except Exception as exc:
        ctx["error"] = str(exc)
        span.end(
            output={"error": str(exc)},
            metadata={"duration_ms": _elapsed_ms(start), "status": "error"},
        )
        raise
    else:
        span.end(
            output=ctx.get("output"),
            metadata={"duration_ms": _elapsed_ms(start), "status": "ok"},
        )


def flush() -> None:
    """Flush pending events to Langfuse. Call before shutdown."""
    lf = get_langfuse()
    lf.flush()


def check_health() -> bool:
    """Return True if Langfuse is reachable."""
    try:
        lf = get_langfuse()
        lf.auth_check()
        return True
    except Exception:
        logger.warning("Langfuse health check failed", exc_info=True)
        return False


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
