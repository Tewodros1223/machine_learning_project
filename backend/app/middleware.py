import os
import time
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", str(max_requests)))
        self.window = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", str(window_seconds)))
        self.storage = {}  # ip -> list[timestamps]
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        now = time.time()
        async with self._lock:
            lst = self.storage.get(client)
            if not lst:
                lst = []
                self.storage[client] = lst
            # remove old
            cutoff = now - self.window
            while lst and lst[0] < cutoff:
                lst.pop(0)
            if len(lst) >= self.max_requests:
                return JSONResponse({"detail": "Too many requests"}, status_code=429)
            lst.append(now)
        return await call_next(request)


class MaxUploadSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_size: int = 5 * 1024 * 1024):
        super().__init__(app)
        self.max_upload_size = int(os.getenv("MAX_UPLOAD_SIZE", str(max_upload_size)))

    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header first
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_upload_size:
                    return JSONResponse({"detail": "Payload too large"}, status_code=413)
            except Exception:
                pass
        return await call_next(request)
