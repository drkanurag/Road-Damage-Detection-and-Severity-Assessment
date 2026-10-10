"""
Detection Microservice (Port 8001)
Bounded Context: Computer Vision Inference, Bounding Box Localization, and Defect Classification.
Supports CPU-optimized ONNX Runtime and PyTorch Ultralytics YOLOv8 engines.
"""

import time
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException

from road_damage_vision.config import DEFECT_CLASSES
from road_damage_vision.detector import RoadDamageDetector
from services.common.config import DETECTION_HOST, DETECTION_PORT
from services.common.middleware import attach_microservice_middleware
from services.common.schemas import (
    BoundingBoxNormalized,
    BoundingBoxPixels,
    DetectionRequestDTO,
    DetectionResponseDTO,
    RawDetectionDTO,
    ServiceHealthResponse,
)
from services.common.utils import decode_base64_to_bgr

SERVICE_NAME = "detection-service"
START_TIME = time.time()

app = FastAPI(
    title="RoadVision - Detection Microservice",
    description="Dedicated Computer Vision microservice for YOLOv8 road defect localization and classification.",
    version="2.0.0",
)
attach_microservice_middleware(app, SERVICE_NAME)

# Lazy/Singleton model registry inside the Detection Microservice
_DETECTORS: Dict[str, Optional[RoadDamageDetector]] = {
    "onnx": None,
    "pytorch": None,
}


def get_detector(backend: str = "onnx") -> RoadDamageDetector:
    """Retrieves or initializes the requested inference engine."""
    b = backend.lower()
    if b not in ("onnx", "pytorch"):
        b = "onnx"
    if _DETECTORS.get(b) is None:
        _DETECTORS[b] = RoadDamageDetector(backend=b)
    return _DETECTORS[b]  # type: ignore[return-value]


@app.get("/health", response_model=ServiceHealthResponse)
async def health_check() -> ServiceHealthResponse:
    """Health and readiness probe for the Detection Microservice."""
    onnx_ready = True
    try:
        get_detector("onnx")
    except Exception:
        onnx_ready = False

    return ServiceHealthResponse(
        service=SERVICE_NAME,
        status="healthy" if onnx_ready else "degraded",
        timestamp=time.time(),
        uptime_seconds=round(time.time() - START_TIME, 2),
        details={
            "port": DETECTION_PORT,
            "engines": {
                "onnx": "ready (CPU-optimized)" if onnx_ready else "unavailable",
                "pytorch": "available",
            },
            "classes": DEFECT_CLASSES,
        },
    )


@app.post("/v1/detect", response_model=DetectionResponseDTO)
async def detect_road_defects(req: DetectionRequestDTO) -> DetectionResponseDTO:
    """
    Executes YOLOv8 object detection and NMS filtering on a base64-encoded road image.
    Returns localized bounding boxes and class predictions without severity coupling.
    """
    try:
        img_bgr = decode_base64_to_bgr(req.image_b64)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    orig_h, orig_w = img_bgr.shape[:2]

    try:
        detector = get_detector(req.backend)
    except Exception:
        detector = get_detector("onnx")

    t_start = time.perf_counter()
    raw_boxes = detector.detect_raw(
        img_bgr, conf_threshold=req.conf_threshold, iou_threshold=req.iou_threshold
    )
    inference_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

    dtos = []
    for idx, (cid, score, (x1, y1, x2, y2)) in enumerate(raw_boxes, start=1):
        cname = DEFECT_CLASSES.get(cid, "Pothole")
        rx1, ry1, rx2, ry2 = round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)
        dtos.append(
            RawDetectionDTO(
                id=idx,
                class_id=cid,
                class_name=cname,
                confidence=round(score, 3),
                bbox=BoundingBoxPixels(
                    x1=rx1,
                    y1=ry1,
                    x2=rx2,
                    y2=ry2,
                    width=round(rx2 - rx1, 1),
                    height=round(ry2 - ry1, 1),
                ),
                bbox_normalized=BoundingBoxNormalized(
                    x1=round(x1 / orig_w, 4),
                    y1=round(y1 / orig_h, 4),
                    x2=round(x2 / orig_w, 4),
                    y2=round(y2 / orig_h, 4),
                ),
            )
        )

    ensemble_tag = "Dual-Model WBF Ensemble, CPU-optimized" if detector.use_ensemble else "CPU-optimized"
    return DetectionResponseDTO(
        service=SERVICE_NAME,
        image_width=orig_w,
        image_height=orig_h,
        inference_time_ms=inference_ms,
        backend_used=f"{detector.backend.upper()} ({ensemble_tag})",
        source_info=req.source_info,
        detections=dtos,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.detection_service.app:app",
        host=DETECTION_HOST,
        port=DETECTION_PORT,
        reload=False,
    )
