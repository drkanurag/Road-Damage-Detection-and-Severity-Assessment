"""
Severity & PCI Assessment Microservice (Port 8002)
Bounded Context: Civil Engineering Distress Grading (ASTM D6433) and
Pavement Condition Index (PCI 0-100) Computation.
"""

import time
from typing import Any, Dict, List, Tuple
from fastapi import FastAPI

from road_damage_vision.config import (
    DEDUCT_POINTS,
    DEFECT_CLASSES,
    MAINTENANCE_ACTIONS,
    SEVERITY_COLORS_HEX,
    SEVERITY_LEVELS,
)
from road_damage_vision.severity import SeverityEstimator
from services.common.config import SEVERITY_HOST, SEVERITY_PORT
from services.common.middleware import attach_microservice_middleware
from services.common.schemas import (
    AssessedDetectionDTO,
    RoadHealthSummaryDTO,
    ServiceHealthResponse,
    SeverityAssessRequestDTO,
    SeverityAssessResponseDTO,
    SeverityMetricsDTO,
)
from services.common.utils import decode_base64_to_bgr

SERVICE_NAME = "severity-service"
START_TIME = time.time()

app = FastAPI(
    title="RoadVision - ASTM D6433 Severity & PCI Microservice",
    description="Dedicated microservice for multi-factor defect severity grading and Pavement Condition Index (PCI) scoring.",
    version="2.0.0",
)
attach_microservice_middleware(app, SERVICE_NAME)

estimator = SeverityEstimator()


@app.get("/health", response_model=ServiceHealthResponse)
async def health_check() -> ServiceHealthResponse:
    """Health and readiness probe for the Severity Microservice."""
    return ServiceHealthResponse(
        service=SERVICE_NAME,
        status="healthy",
        timestamp=time.time(),
        uptime_seconds=round(time.time() - START_TIME, 2),
        details={
            "port": SEVERITY_PORT,
            "standard": "ASTM D6433 / FHWA Distress Identification Manual",
            "severity_levels": SEVERITY_LEVELS,
        },
    )


@app.get("/v1/standards")
async def get_astm_standards() -> Dict[str, Any]:
    """Returns ASTM D6433 defect classes, PCI deduct points, and maintenance actions."""
    return {
        "service": SERVICE_NAME,
        "standard": "ASTM D6433",
        "classes": DEFECT_CLASSES,
        "severity_levels": SEVERITY_LEVELS,
        "severity_colors": SEVERITY_COLORS_HEX,
        "pci_deduct_points": DEDUCT_POINTS,
        "maintenance_actions": MAINTENANCE_ACTIONS,
    }


@app.post("/v1/assess", response_model=SeverityAssessResponseDTO)
async def assess_severity_and_pci(req: SeverityAssessRequestDTO) -> SeverityAssessResponseDTO:
    """
    Evaluates ASTM D6433 severity for each localized defect and computes
    the composite Pavement Condition Index (PCI 0-100).
    """
    t_start = time.perf_counter()

    img_bgr = None
    if req.image_b64:
        try:
            img_bgr = decode_base64_to_bgr(req.image_b64)
        except ValueError:
            img_bgr = None

    assessed_list: List[AssessedDetectionDTO] = []
    summary_tuples: List[Tuple[str, str]] = []

    for det in req.detections:
        sev = estimator.estimate(
            class_name=det.class_name,
            bbox=(det.bbox.x1, det.bbox.y1, det.bbox.x2, det.bbox.y2),
            img_shape=(req.image_height, req.image_width),
            confidence=det.confidence,
            image_bgr=img_bgr,
        )

        sev_dto = SeverityMetricsDTO(
            level=sev.level,
            score=sev.score,
            color_hex=SEVERITY_COLORS_HEX.get(sev.level, "#22c55e"),
            area_pixels=sev.area_pixels,
            area_pct=sev.area_pct,
            aspect_ratio=sev.aspect_ratio,
            extent_norm=sev.extent_norm,
            edge_density=sev.edge_density,
            contrast_delta=sev.contrast_delta,
            rationale=sev.rationale,
            recommended_action=sev.recommended_action,
        )

        assessed_list.append(
            AssessedDetectionDTO(
                id=det.id,
                class_id=det.class_id,
                class_name=det.class_name,
                confidence=det.confidence,
                bbox=det.bbox,
                bbox_normalized=det.bbox_normalized,
                severity=sev_dto,
            )
        )
        summary_tuples.append((det.class_name, sev.level))

    # Rank defects by severity (High -> Medium -> Low) then confidence
    sev_rank = {"High": 0, "Medium": 1, "Low": 2}
    assessed_list.sort(key=lambda d: (sev_rank.get(d.severity.level, 3), -d.confidence))
    for idx, d in enumerate(assessed_list, start=1):
        d.id = idx

    health = estimator.compute_road_health(summary_tuples)
    summary_dto = RoadHealthSummaryDTO(
        health_score=health.health_score,
        status=health.status,
        total_defects=health.total_defects,
        critical_defects_count=health.critical_defects_count,
        severity_counts=health.severity_counts,
        class_counts=health.class_counts,
        urgency=health.estimated_maintenance_urgency,
        action_items=health.action_items,
    )

    elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
    return SeverityAssessResponseDTO(
        service=SERVICE_NAME,
        processing_time_ms=elapsed_ms,
        detections=assessed_list,
        summary=summary_dto,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.severity_service.app:app",
        host=SEVERITY_HOST,
        port=SEVERITY_PORT,
        reload=False,
    )
