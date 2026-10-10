"""
Visualization & Media Microservice (Port 8003)
Bounded Context: OpenCV Bounding Box Rendering, Executive PCI HUD Overlay,
and Forensic Defect Thumbnail Cropping.
"""

import time
from typing import Dict, List
from fastapi import FastAPI, HTTPException

from road_damage_vision.detector import Detection, RoadDamageReport
from road_damage_vision.severity import RoadHealthSummary, SeverityAssessment
from road_damage_vision.visualizer import RoadDamageVisualizer
from services.common.config import VISUALIZATION_HOST, VISUALIZATION_PORT
from services.common.middleware import attach_microservice_middleware
from services.common.schemas import (
    AssessedDetectionDTO,
    RoadHealthSummaryDTO,
    ServiceHealthResponse,
    VisualizationRenderRequestDTO,
    VisualizationRenderResponseDTO,
)
from services.common.utils import decode_base64_to_bgr, encode_bgr_to_base64

SERVICE_NAME = "visualization-service"
START_TIME = time.time()

app = FastAPI(
    title="RoadVision - Visualization & Media Microservice",
    description="Dedicated microservice for rendering annotated road damage overlays, HUD banners, and defect thumbnail crops.",
    version="2.0.0",
)
attach_microservice_middleware(app, SERVICE_NAME)


def _reconstruct_domain_report(req: VisualizationRenderRequestDTO) -> RoadDamageReport:
    """Maps incoming DTOs to domain dataclasses for RoadDamageVisualizer."""
    detections: List[Detection] = []
    for d in req.detections:
        s = d.severity
        detections.append(
            Detection(
                id=d.id,
                class_id=d.class_id,
                class_name=d.class_name,
                confidence=d.confidence,
                bbox=(d.bbox.x1, d.bbox.y1, d.bbox.x2, d.bbox.y2),
                bbox_normalized=(
                    d.bbox_normalized.x1,
                    d.bbox_normalized.y1,
                    d.bbox_normalized.x2,
                    d.bbox_normalized.y2,
                ),
                severity=SeverityAssessment(
                    level=s.level,
                    score=s.score,
                    area_pixels=s.area_pixels,
                    area_pct=s.area_pct,
                    aspect_ratio=s.aspect_ratio,
                    extent_norm=s.extent_norm,
                    edge_density=s.edge_density,
                    contrast_delta=s.contrast_delta,
                    rationale=s.rationale,
                    recommended_action=s.recommended_action,
                ),
            )
        )

    summary = RoadHealthSummary(
        health_score=req.summary.health_score,
        status=req.summary.status,
        total_defects=req.summary.total_defects,
        severity_counts=req.summary.severity_counts,
        class_counts=req.summary.class_counts,
        critical_defects_count=req.summary.critical_defects_count,
        estimated_maintenance_urgency=req.summary.urgency,
        action_items=req.summary.action_items,
    )

    return RoadDamageReport(
        image_shape=(req.image_height, req.image_width),
        detections=detections,
        summary=summary,
        inference_time_ms=req.inference_time_ms,
        backend_used=req.backend_used,
        source_info=req.source_info,
    )


@app.get("/health", response_model=ServiceHealthResponse)
async def health_check() -> ServiceHealthResponse:
    """Health and readiness probe for the Visualization Microservice."""
    return ServiceHealthResponse(
        service=SERVICE_NAME,
        status="healthy",
        timestamp=time.time(),
        uptime_seconds=round(time.time() - START_TIME, 2),
        details={
            "port": VISUALIZATION_PORT,
            "capabilities": ["bbox_overlay", "executive_hud", "forensic_thumbnails"],
        },
    )


@app.post("/v1/render", response_model=VisualizationRenderResponseDTO)
async def render_annotations(req: VisualizationRenderRequestDTO) -> VisualizationRenderResponseDTO:
    """
    Renders color-coded defect bounding boxes, severity badges, confidence scores,
    Executive PCI HUD, and individual forensic defect crops.
    """
    t_start = time.perf_counter()

    try:
        img_bgr = decode_base64_to_bgr(req.image_b64)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    domain_report = _reconstruct_domain_report(req)

    visualizer = RoadDamageVisualizer(
        show_hud=req.show_hud,
        show_severity_badge=req.show_badges,
        show_confidence=req.show_conf,
    )

    annotated_bgr = visualizer.draw(img_bgr, domain_report)
    annotated_uri = encode_bgr_to_base64(annotated_bgr, quality=88, include_prefix=True)
    raw_uri = encode_bgr_to_base64(img_bgr, quality=85, include_prefix=True)

    thumb_map: Dict[int, str] = {}
    if req.extract_thumbnails and domain_report.detections:
        thumbs = visualizer.create_thumbnail_grid(
            img_bgr, domain_report, thumb_size=req.thumb_size
        )
        for det, crop_bgr in thumbs:
            thumb_map[det.id] = encode_bgr_to_base64(
                crop_bgr, quality=85, include_prefix=True
            )

    elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
    return VisualizationRenderResponseDTO(
        service=SERVICE_NAME,
        processing_time_ms=elapsed_ms,
        raw_image_uri=raw_uri,
        annotated_image_uri=annotated_uri,
        thumbnails_uri_map=thumb_map,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.visualization_service.app:app",
        host=VISUALIZATION_HOST,
        port=VISUALIZATION_PORT,
        reload=False,
    )
