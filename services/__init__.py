"""
RoadVision AI Microservices Package.
Decomposes Road Damage Detection and Severity Assessment into independent,
loosely-coupled microservices following Domain-Driven Design (DDD) and 12-Factor App principles:
  1. detection-service     (Port 8001): YOLOv8 ONNX / PyTorch Defect Localization & Classification
  2. severity-service      (Port 8002): ASTM D6433 Multi-Factor Severity & PCI Health Engine
  3. visualization-service (Port 8003): Bounding Box Annotation, Executive HUD & Forensic Cropping
  4. reporting-service     (Port 8004): Multi-Format Exports (JSON/CSV/Markdown) & Inspection Audit Log
  5. api-gateway           (Port 8000): Unified API Gateway, Orchestrator, Circuit Breaker & Web UI
"""

__version__ = "2.0.0"
