"""
monitoring.py - Production Monitoring, Request Latency Logging, and Token Usage Tracking

Provides:
  - Request-level latency and performance logging via FastAPI middleware
  - Standardized request ID propagation (X-Request-ID, X-Process-Time-Ms)
  - Token usage measurement with provider-actual extraction and fallback estimation
"""

import logging
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure production logger
logger = logging.getLogger("shellsathi.production")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class RequestLatencyLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware capturing request-level performance:
      - Request ID (from header X-Request-ID or auto-generated UUID4)
      - HTTP Method
      - Endpoint path
      - Response status code
      - Processing latency in milliseconds
      - UTC Timestamp
    Attaches X-Request-ID and X-Process-Time-Ms headers to responses.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        start_time = time.perf_counter()
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        timestamp = datetime.now(timezone.utc).isoformat()

        # Attach request_id to request state for downstream handlers
        request.state.request_id = request_id

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"request_id={request_id} endpoint={request.url.path} "
                f"method={request.method} status=500 latency_ms={duration_ms:.2f} "
                f"timestamp={timestamp} error={exc.__class__.__name__}"
            )
            raise exc

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Log performance metric without exposing sensitive payload data
        logger.info(
            f"request_id={request_id} endpoint={request.url.path} "
            f"method={request.method} status={status_code} latency_ms={duration_ms:.2f} "
            f"timestamp={timestamp}"
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(duration_ms)
        return response


# --- Token Usage Tracking ---

@dataclass
class TokenUsage:
    """Structure storing token metrics for LLM and RAG interactions."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model_name: str
    estimated: bool = False
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def estimate_token_count(text: str) -> int:
    """
    Standard token estimation heuristic (~4 characters per token or 0.75 words per token)
    used when provider token counts are unavailable or during offline testing.
    """
    if not text:
        return 0
    clean = text.strip()
    words = len(clean.split())
    chars = len(clean)
    # Average of word-based heuristic (words * 1.33) and char-based (chars / 4)
    estimated = max(1, round((words * 1.33 + chars / 4.0) / 2.0))
    return estimated


def track_tokens(
    model_name: str,
    input_text: str,
    output_text: str,
    actual_usage: Optional[Dict[str, int]] = None,
    request_id: Optional[str] = None,
) -> TokenUsage:
    """
    Track token usage for an LLM interaction.
    Prefers actual provider usage if supplied; otherwise calculates a clearly labelled estimate.
    Logs token metrics to the production logger.
    """
    if actual_usage and "prompt_tokens" in actual_usage and "completion_tokens" in actual_usage:
        inp = int(actual_usage["prompt_tokens"])
        out = int(actual_usage["completion_tokens"])
        tot = actual_usage.get("total_tokens", inp + out)
        estimated = False
    elif actual_usage and "promptTokenCount" in actual_usage and "candidatesTokenCount" in actual_usage:
        inp = int(actual_usage["promptTokenCount"])
        out = int(actual_usage["candidatesTokenCount"])
        tot = actual_usage.get("totalTokenCount", inp + out)
        estimated = False
    else:
        inp = estimate_token_count(input_text)
        out = estimate_token_count(output_text)
        tot = inp + out
        estimated = True

    usage = TokenUsage(
        input_tokens=inp,
        output_tokens=out,
        total_tokens=tot,
        model_name=model_name,
        estimated=estimated,
        request_id=request_id,
    )

    logger.info(
        f"token_usage request_id={request_id or 'none'} model={model_name} "
        f"input_tokens={inp} output_tokens={out} total_tokens={tot} "
        f"estimated={estimated}"
    )

    return usage
