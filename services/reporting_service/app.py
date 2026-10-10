"""
Reporting & Audit Microservice (Port 8004)
Bounded Context: Multi-Format Report Generation (JSON, CSV, Executive Markdown)
and Inspection Audit Trail Management.
"""

from collections import deque
import csv
import io
import time
from typing import Any, Deque, Dict, List
import uuid
from fastapi import FastAPI

from road_damage_vision.detector import Detection, RoadDamageReport
from road_damage_vision.report import generate_markdown_summary, report_to_dict
from road_damage_vision.severity import RoadHealthSummary, SeverityAssessment
from services.common.config import REPORTING_HOST, REPORTING_PORT
from services.common.middleware import attach_microservice_middleware
from services.common.schemas import (
    ReportGenerateRequestDTO,
    ReportGenerateResponseDTO,
    ServiceHealthResponse,
)

SERVICE_NAME = "reporting-service"
START_TIME = time.time()

app = FastAPI(
    title="RoadVision - Reporting & Audit Microservice",
    description="Dedicated microservice for exporting JSON, CSV, and Executive Markdown reports and maintaining inspection audit history.",
    version="2.0.0",
)
attach_microservice_middleware(app, SERVICE_NAME)

# Bounded in-memory audit history store (Database-per-Service pattern)
_AUDIT_HISTORY: Deque[Dict[str, Any]] = deque(maxlen=100)


def _to_domain_report(req: ReportGenerateRequestDTO) -> RoadDamageReport:
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
    """Health and readiness probe for the Reporting Microservice."""
    return ServiceHealthResponse(
        service=SERVICE_NAME,
        status="healthy",
        timestamp=time.time(),
        uptime_seconds=round(time.time() - START_TIME, 2),
        details={
            "port": REPORTING_PORT,
            "formats": ["json", "csv", "markdown"],
            "audit_records_count": len(_AUDIT_HISTORY),
        },
    )


@app.post("/v1/reports/generate", response_model=ReportGenerateResponseDTO)
async def generate_reports(req: ReportGenerateRequestDTO) -> ReportGenerateResponseDTO:
    """Generates JSON, CSV, and Executive Markdown reports and records an audit entry."""
    t_start = time.perf_counter()
    report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
    created_at = time.time()

    domain_report = _to_domain_report(req)
    json_dict = report_to_dict(domain_report)
    md_summary = generate_markdown_summary(domain_report)

    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf)
    writer.writerow(
        [
            "defect_id",
            "class_name",
            "confidence",
            "severity_level",
            "severity_score",
            "bbox_x1",
            "bbox_y1",
            "bbox_x2",
            "bbox_y2",
            "area_pct",
            "aspect_ratio",
            "edge_density",
            "contrast_delta",
            "rationale",
            "recommended_action",
        ]
    )
    for d in domain_report.detections:
        writer.writerow(
            [
                d.id,
                d.class_name,
                d.confidence,
                d.severity.level,
                d.severity.score,
                d.bbox[0],
                d.bbox[1],
                d.bbox[2],
                d.bbox[3],
                d.severity.area_pct,
                d.severity.aspect_ratio,
                d.severity.edge_density,
                d.severity.contrast_delta,
                d.severity.rationale,
                d.severity.recommended_action,
            ]
        )

    csv_str = csv_buf.getvalue()
    elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

    _AUDIT_HISTORY.appendleft(
        {
            "report_id": report_id,
            "timestamp": created_at,
            "source_info": req.source_info,
            "health_score": req.summary.health_score,
            "status": req.summary.status,
            "total_defects": req.summary.total_defects,
            "critical_defects_count": req.summary.critical_defects_count,
            "inference_time_ms": req.inference_time_ms,
        }
    )

    return ReportGenerateResponseDTO(
        service=SERVICE_NAME,
        report_id=report_id,
        created_at=created_at,
        processing_time_ms=elapsed_ms,
        json_report=json_dict,
        csv_content=csv_str,
        markdown_summary=md_summary,
    )


@app.get("/v1/reports/history")
async def get_inspection_history() -> Dict[str, Any]:
    """Returns recent inspection audit records stored by the Reporting Microservice."""
    return {
        "service": SERVICE_NAME,
        "total_records": len(_AUDIT_HISTORY),
        "history": list(_AUDIT_HISTORY),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.reporting_service.app:app",
        host=REPORTING_HOST,
        port=REPORTING_PORT,
        reload=False,
    )
