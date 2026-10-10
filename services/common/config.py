"""
12-Factor App Environment Configuration & Service Registry for Microservices.
All ports, hostnames, timeouts, and execution modes are configurable via environment variables.
"""

from dataclasses import dataclass
import os
from typing import Dict


@dataclass(frozen=True)
class ServiceEndpointConfig:
    """Configuration metadata for an individual microservice."""
    name: str
    slug: str
    host: str
    port: int
    base_url: str
    version: str = "2.0.0"
    description: str = ""


# Execution mode: 'auto' (tries remote HTTP first or uses ASGI transport seamlessly),
# 'distributed' (strict remote TCP HTTP), or 'inprocess' (ASGI microservice transport)
MICROSERVICES_MODE: str = os.getenv("ROADVISION_MS_MODE", "auto").lower()

GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))

DETECTION_HOST: str = os.getenv("DETECTION_SERVICE_HOST", "127.0.0.1")
DETECTION_PORT: int = int(os.getenv("DETECTION_SERVICE_PORT", "8001"))
DETECTION_URL: str = os.getenv(
    "DETECTION_SERVICE_URL", f"http://{DETECTION_HOST}:{DETECTION_PORT}"
)

SEVERITY_HOST: str = os.getenv("SEVERITY_SERVICE_HOST", "127.0.0.1")
SEVERITY_PORT: int = int(os.getenv("SEVERITY_SERVICE_PORT", "8002"))
SEVERITY_URL: str = os.getenv(
    "SEVERITY_SERVICE_URL", f"http://{SEVERITY_HOST}:{SEVERITY_PORT}"
)

VISUALIZATION_HOST: str = os.getenv("VISUALIZATION_SERVICE_HOST", "127.0.0.1")
VISUALIZATION_PORT: int = int(os.getenv("VISUALIZATION_SERVICE_PORT", "8003"))
VISUALIZATION_URL: str = os.getenv(
    "VISUALIZATION_SERVICE_URL", f"http://{VISUALIZATION_HOST}:{VISUALIZATION_PORT}"
)

REPORTING_HOST: str = os.getenv("REPORTING_SERVICE_HOST", "127.0.0.1")
REPORTING_PORT: int = int(os.getenv("REPORTING_SERVICE_PORT", "8004"))
REPORTING_URL: str = os.getenv(
    "REPORTING_SERVICE_URL", f"http://{REPORTING_HOST}:{REPORTING_PORT}"
)

SERVICE_TIMEOUT_SECONDS: float = float(os.getenv("SERVICE_TIMEOUT_SECONDS", "15.0"))

SERVICE_REGISTRY: Dict[str, ServiceEndpointConfig] = {
    "detection-service": ServiceEndpointConfig(
        name="Detection Microservice",
        slug="detection-service",
        host=DETECTION_HOST,
        port=DETECTION_PORT,
        base_url=DETECTION_URL,
        description="YOLOv8 ONNX & PyTorch object detection, localization, and NMS filtering.",
    ),
    "severity-service": ServiceEndpointConfig(
        name="Severity & PCI Microservice",
        slug="severity-service",
        host=SEVERITY_HOST,
        port=SEVERITY_PORT,
        base_url=SEVERITY_URL,
        description="ASTM D6433 multi-factor severity classification and Pavement Condition Index (PCI) calculation.",
    ),
    "visualization-service": ServiceEndpointConfig(
        name="Visualization & Media Microservice",
        slug="visualization-service",
        host=VISUALIZATION_HOST,
        port=VISUALIZATION_PORT,
        base_url=VISUALIZATION_URL,
        description="Bounding box annotation, Executive HUD rendering, and forensic defect thumbnail extraction.",
    ),
    "reporting-service": ServiceEndpointConfig(
        name="Reporting & Audit Microservice",
        slug="reporting-service",
        host=REPORTING_HOST,
        port=REPORTING_PORT,
        base_url=REPORTING_URL,
        description="JSON, CSV, and Executive Markdown report generation and inspection history tracking.",
    ),
}
