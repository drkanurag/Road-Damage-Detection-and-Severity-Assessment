"""
Resilient Service Discovery & Inter-Service HTTP Client with Circuit Breaker.
Supports both distributed TCP HTTP calls (ports 8001-8004) and zero-latency
ASGI Microservice Transport fallback for single-command execution.
"""

import socket
import time
from typing import Any, Dict, Optional, Tuple
from fastapi import FastAPI
import httpx

from services.common.config import (
    MICROSERVICES_MODE,
    SERVICE_REGISTRY,
    SERVICE_TIMEOUT_SECONDS,
)
from services.common.schemas import ServiceTraceStepDTO


class MicroserviceClient:
    """
    Communicates with downstream microservices using standardized HTTP contracts,
    propagating X-Correlation-ID headers and recording hop-by-hop latency telemetry.
    """

    def __init__(self) -> None:
        self._asgi_apps: Dict[str, FastAPI] = {}
        self._port_status_cache: Dict[str, Tuple[bool, float]] = {}
        self._cache_ttl = 5.0  # seconds

    def register_asgi_service(self, service_slug: str, app: FastAPI) -> None:
        """Registers a microservice's FastAPI application for ASGI transport / fallback."""
        self._asgi_apps[service_slug] = app

    def _is_remote_port_open(self, slug: str, host: str, port: int) -> bool:
        """Fast non-blocking check whether a remote TCP microservice port is listening."""
        if MICROSERVICES_MODE == "inprocess":
            return False
        if MICROSERVICES_MODE == "distributed":
            return True

        now = time.time()
        cached = self._port_status_cache.get(slug)
        if cached is not None and (now - cached[1]) < self._cache_ttl:
            return cached[0]

        is_open = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.02)  # 20ms local loopback probe
                is_open = sock.connect_ex((host, port)) == 0
        except OSError:
            is_open = False

        self._port_status_cache[slug] = (is_open, now)
        return is_open

    async def request(
        self,
        service_slug: str,
        method: str,
        path: str,
        correlation_id: str,
        json_payload: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], ServiceTraceStepDTO]:
        """
        Sends an HTTP request to the target microservice over TCP HTTP (if listening)
        or via ASGI Microservice Transport (circuit-breaker / local cluster mode).
        """
        if service_slug not in SERVICE_REGISTRY:
            raise ValueError(f"Unknown microservice '{service_slug}' in registry.")

        cfg = SERVICE_REGISTRY[service_slug]
        headers = {"X-Correlation-ID": correlation_id}
        t_start = time.perf_counter()

        use_remote = self._is_remote_port_open(service_slug, cfg.host, cfg.port)

        if use_remote:
            try:
                async with httpx.AsyncClient(
                    base_url=cfg.base_url, timeout=SERVICE_TIMEOUT_SECONDS
                ) as client:
                    resp = await client.request(
                        method, path, json=json_payload, headers=headers
                    )
                    resp.raise_for_status()
                    elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
                    trace = ServiceTraceStepDTO(
                        service=service_slug,
                        endpoint=f"{method.upper()} {path}",
                        transport=f"HTTP ({cfg.base_url})",
                        status_code=resp.status_code,
                        latency_ms=elapsed_ms,
                    )
                    return resp.json(), trace
            except Exception:
                # Circuit breaker tripped: mark port unavailable and fall back to ASGI service
                self._port_status_cache[service_slug] = (False, time.time())

        asgi_app = self._asgi_apps.get(service_slug)
        if asgi_app is None:
            raise RuntimeError(
                f"Microservice '{service_slug}' is unreachable at {cfg.base_url} and no fallback is registered."
            )

        transport = httpx.ASGITransport(app=asgi_app)
        async with httpx.AsyncClient(
            transport=transport, base_url=cfg.base_url, timeout=SERVICE_TIMEOUT_SECONDS
        ) as client:
            resp = await client.request(method, path, json=json_payload, headers=headers)
            resp.raise_for_status()
            elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
            trace = ServiceTraceStepDTO(
                service=service_slug,
                endpoint=f"{method.upper()} {path}",
                transport="ASGI Microservice Bus",
                status_code=resp.status_code,
                latency_ms=elapsed_ms,
            )
            return resp.json(), trace
