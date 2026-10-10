"""
Observability, Correlation-ID Distributed Tracing, and Error-Handling Middleware
applied uniformly across all RoadVision AI Microservices.
"""

import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


def attach_microservice_middleware(app: FastAPI, service_name: str) -> None:
    """
    Attaches CORS, Correlation-ID propagation (X-Correlation-ID),
    execution latency headers (X-Process-Time-Ms, X-Service-Name),
    and standardized exception handling to a FastAPI microservice.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def trace_and_timing_middleware(request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        t_start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "service": service_name,
                    "correlation_id": correlation_id,
                    "error": str(exc),
                },
                headers={
                    "X-Correlation-ID": correlation_id,
                    "X-Service-Name": service_name,
                    "X-Process-Time-Ms": str(elapsed_ms),
                },
            )

        elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Service-Name"] = service_name
        response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
        return response
