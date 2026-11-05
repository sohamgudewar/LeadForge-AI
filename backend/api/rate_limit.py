"""In-memory sliding-window rate limiting for the expensive LLM endpoints.

Every call to /run-agent, /run-agent-with-pdf or /upload-pdf spends Gemini,
Tavily or embedding quota. The public demo has no user accounts, so we limit:

* per client: at most RUN_LIMIT_PER_CLIENT_HOUR calls per IP per hour, and
* globally: at most RUN_LIMIT_GLOBAL_HOUR calls per hour in total.

The global cap is the real cost guarantee: client IPs can be spoofed or rotated,
but the total spend per hour stays bounded either way.

State lives in process memory, which is fine for a single instance. With
several instances you'd move it to Redis (same algorithm, a sorted set per key).
"""

import math
import os
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request

WINDOW_SECONDS = 3600


class SlidingWindowLimiter:
    def __init__(self, per_client: int, global_limit: int, window: int = WINDOW_SECONDS):
        self.per_client = per_client
        self.global_limit = global_limit
        self.window = window
        self._clients: dict[str, deque[float]] = defaultdict(deque)
        self._global: deque[float] = deque()
        self._lock = Lock()

    def _prune(self, hits: deque[float], now: float) -> None:
        while hits and hits[0] <= now - self.window:
            hits.popleft()

    def _retry_after(self, hits: deque[float], now: float) -> int:
        return max(1, math.ceil(hits[0] + self.window - now))

    def check(self, client_key: str, now: float | None = None) -> None:
        """Record a hit, or raise HTTP 429 if a limit is exceeded."""
        now = time.monotonic() if now is None else now
        with self._lock:
            client_hits = self._clients[client_key]
            self._prune(client_hits, now)
            self._prune(self._global, now)

            if len(client_hits) >= self.per_client:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit reached for this demo. Please try again later.",
                    headers={"Retry-After": str(self._retry_after(client_hits, now))},
                )
            if len(self._global) >= self.global_limit:
                raise HTTPException(
                    status_code=429,
                    detail="The demo is busy right now. Please try again later.",
                    headers={"Retry-After": str(self._retry_after(self._global, now))},
                )

            client_hits.append(now)
            self._global.append(now)

    def reset(self) -> None:
        with self._lock:
            self._clients.clear()
            self._global.clear()


limiter = SlidingWindowLimiter(
    per_client=int(os.getenv("RUN_LIMIT_PER_CLIENT_HOUR", "10")),
    global_limit=int(os.getenv("RUN_LIMIT_GLOBAL_HOUR", "100")),
)


def enforce_run_limit(request: Request) -> None:
    """FastAPI dependency for endpoints that spend LLM / search quota."""
    client_key = request.client.host if request.client else "unknown"
    limiter.check(client_key)
