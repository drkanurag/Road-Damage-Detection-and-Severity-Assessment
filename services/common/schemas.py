"""
Shared Pydantic API Contracts (DTOs) for Inter-Service Communication.
Enforces strict schema validation across all microservice boundaries.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ServiceHealthResponse(BaseModel):
    """Standardized health check response returned by every microservice."""
    service: str
    version: str = "2.0.0"
    status: str = "healthy"
    timestamp: float
    uptime_seconds: float
    details: Dict[str, Any] = Field(default_factory=dict)


class BoundingBoxPixels(BaseModel):
    """Pixel-space bounding box coordinates."""
    x1: float
    y1: float
    x2: float
    y2: float
    width: Optional[float] = None
    height: Optional[float] = None


class BoundingBoxNormalized(BaseModel):
    """Normalized [0.0, 1.0] bounding box coordinates."""
    x1: float
    y1: float
    x2: float
    y2: float


class RawDetectionDTO(BaseModel):
    """Raw localized defect emitted by the Detection Microservice."""
    id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBoxPixels
    bbox_normalized: BoundingBoxNormalized


class DetectionRequestDTO(BaseModel):
    """Request contract for Detection Microservice (/v1/detect)."""
    image_b64: str = Field(..., description="Base64-encoded BGR/RGB image")
    conf_threshold: float = Field(default=0.25, ge=0.05, le=0.95)
    iou_threshold: float = Field(default=0.45, ge=0.05, le=0.95)
    backend: str = Field(default="onnx", description="'onnx' or 'pytorch'")
    source_info: str = Field(default="Uploaded Image")


class DetectionResponseDTO(BaseModel):
    """Response contract from Detection Microservice (/v1/detect)."""
    service: str = "detection-service"
    image_width: int
    image_height: int
    inference_time_ms: float
    backend_used: str
    source_info: str
    detections: List[RawDetectionDTO]


class SeverityMetricsDTO(BaseModel):
    """ASTM D6433 severity assessment metrics for a single defect."""
    level: str
    score: float
    color_hex: str
    area_pixels: int
    area_pct: float
    aspect_ratio: float
    extent_norm: float
    edge_density: float
    contrast_delta: float
    rationale: str
    recommended_action: str


class AssessedDetectionDTO(BaseModel):
    """Defect enriched with ASTM D6433 severity metrics."""
    id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBoxPixels
    bbox_normalized: BoundingBoxNormalized
    severity: SeverityMetricsDTO
    crop_base64: str = ""


class RoadHealthSummaryDTO(BaseModel):
    """Composite Pavement Condition Index (PCI 0-100) and roadway summary."""
    health_score: float
    status: str
    total_defects: int
    critical_defects_count: int
    severity_counts: Dict[str, int]
    class_counts: Dict[str, int]
    urgency: str
    action_items: List[str]


class SeverityAssessRequestDTO(BaseModel):
    """Request contract for Severity Microservice (/v1/assess)."""
    image_width: int
    image_height: int
    detections: List[RawDetectionDTO]
    image_b64: Optional[str] = Field(
        default=None,
        description="Optional base64 image for Canny edge density and photometric depression contrast analysis",
    )


class SeverityAssessResponseDTO(BaseModel):
    """Response contract from Severity Microservice (/v1/assess)."""
    service: str = "severity-service"
    processing_time_ms: float
    detections: List[AssessedDetectionDTO]
    summary: RoadHealthSummaryDTO


class VisualizationRenderRequestDTO(BaseModel):
    """Request contract for Visualization Microservice (/v1/render)."""
    image_b64: str
    image_width: int
    image_height: int
    inference_time_ms: float
    backend_used: str
    source_info: str = ""
    detections: List[AssessedDetectionDTO]
    summary: RoadHealthSummaryDTO
    show_hud: bool = True
    show_badges: bool = True
    show_conf: bool = True
    extract_thumbnails: bool = True
    thumb_size: int = 200


class VisualizationRenderResponseDTO(BaseModel):
    """Response contract from Visualization Microservice (/v1/render)."""
    service: str = "visualization-service"
    processing_time_ms: float
    raw_image_uri: str
    annotated_image_uri: str
    thumbnails_uri_map: Dict[int, str]


class ReportGenerateRequestDTO(BaseModel):
    """Request contract for Reporting Microservice (/v1/reports/generate)."""
    source_info: str
    image_width: int
    image_height: int
    inference_time_ms: float
    backend_used: str
    summary: RoadHealthSummaryDTO
    detections: List[AssessedDetectionDTO]


class ReportGenerateResponseDTO(BaseModel):
    """Response contract from Reporting Microservice (/v1/reports/generate)."""
    service: str = "reporting-service"
    report_id: str
    created_at: float
    processing_time_ms: float
    json_report: Dict[str, Any]
    csv_content: str
    markdown_summary: str


class ServiceTraceStepDTO(BaseModel):
    """Telemetry record for a single microservice hop in the orchestrated pipeline."""
    service: str
    endpoint: str
    transport: str
    status_code: int
    latency_ms: float
