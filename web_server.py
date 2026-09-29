"""
FastAPI Web Server for Road Damage Detection and Severity Assessment.
Serves the modern interactive web application, REST API endpoints, and sample imagery.
"""

import base64
import io
import os
import time
from typing import Optional
import cv2
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from road_damage_vision import (
    DEFECT_CLASSES,
    RoadDamageDetector,
    RoadDamageVisualizer,
    report_to_dict,
)
from road_damage_vision.config import SEVERITY_COLORS_HEX

app = FastAPI(
    title="Road Damage Detection & Severity Assessment API",
    description="Lightweight computer vision API for road damage localization, classification, and ASTM D6433 severity assessment.",
    version="1.0.0",
)

# Enable CORS for local development and integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detector instances in memory
print("[*] Initializing ONNX Road Damage Detector...")
detector_onnx = RoadDamageDetector(backend="onnx")
detector_pt: Optional[RoadDamageDetector] = None

try:
    print("[*] Initializing PyTorch Road Damage Detector...")
    detector_pt = RoadDamageDetector(backend="pytorch")
except Exception as e:
    print(f"[!] PyTorch detector init warning: {e}")

visualizer = RoadDamageVisualizer(show_hud=True)

# Curated sample files metadata
SAMPLES_METADATA = [
    {
        "id": "india_pothole_cracks",
        "title": "Roadway Pothole & Alligator Distress (Your Photo)",
        "category": "Pothole & Alligator",
        "description": "Complex Indian road distress with localized potholes and base fatigue.",
        "filename": "india_pothole_cracks.jpg",
    },
    {
        "id": "india_barricade_potholes",
        "title": "Barricade Road Cavities (Your Photo)",
        "category": "Potholes (D40)",
        "description": "Fine-tuned detection of subtle pothole depressions along corridor.",
        "filename": "india_barricade_potholes.jpg",
    },
    {
        "id": "india_highway_distress",
        "title": "Highway Mid-Lane Pothole Cluster (Your Photo)",
        "category": "Potholes & Fatigue",
        "description": "Accurately localized multiple pothole cavities across traffic lane.",
        "filename": "india_highway_distress.jpg",
    },
    {
        "id": "india_corridor_worn_road",
        "title": "Suburban Corridor Pothole Field (Your Photo)",
        "category": "Multiple Potholes",
        "description": "Severe road deterioration with foreground and midground pothole depressions.",
        "filename": "india_corridor_worn_road.jpg",
    },
    {
        "id": "pothole_sample",
        "title": "Severe Potholes & Transverse Fracture",
        "category": "Pothole & Transverse",
        "description": "Depression cavities with sharp edges and thermal cracking.",
        "filename": "pothole_sample.jpg",
    },
    {
        "id": "alligator_crack_sample",
        "title": "Alligator Fatigue Cracking",
        "category": "Alligator crack",
        "description": "Interconnected polygonal pattern signaling sub-base failure.",
        "filename": "alligator_crack_sample.jpg",
    },
    {
        "id": "longitudinal_crack_sample",
        "title": "Longitudinal Wheel-Path Crack",
        "category": "Longitudinal crack",
        "description": "Linear crack running parallel to traffic direction.",
        "filename": "longitudinal_crack_sample.jpg",
    },
]


def image_to_base64_jpeg(img_bgr: np.ndarray, quality: int = 90) -> str:
    """Encodes BGR numpy image to base64 data URI string."""
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, buffer = cv2.imencode(".jpg", img_bgr, encode_params)
    if not success:
        return ""
    b64 = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


@app.get("/api/health")
async def health_check():
    """System health check and engine status."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "engines": {
            "onnx": "ready (CPU-optimized)",
            "pytorch": "ready" if detector_pt else "unavailable",
        },
        "default_engine": "onnx",
        "classes": list(DEFECT_CLASSES.values()),
    }


@app.get("/api/samples")
async def get_samples():
    """Returns list of curated test samples available for instant testing."""
    samples_list = []
    for s in SAMPLES_METADATA:
        path = os.path.join("samples", s["filename"])
        if os.path.exists(path):
            samples_list.append({
                **s,
                "url": f"/samples/{s['filename']}",
            })
    return {"samples": samples_list}


@app.post("/api/detect")
async def detect_defects(
    file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
    conf_threshold: float = Form(0.25),
    iou_threshold: float = Form(0.45),
    backend: str = Form("onnx"),
    show_hud: bool = Form(True),
):
    """
    Main detection endpoint: analyzes road image, localizes defects,
    classifies into the 4 types, estimates ASTM severity, and returns
    annotated image, defect crops, and full metrics.
    """
    # 1. Load image from upload or sample ID
    img_bgr = None
    source_name = "Uploaded Image"

    if sample_id:
        matching = [s for s in SAMPLES_METADATA if s["id"] == sample_id]
        if matching:
            sample_path = os.path.join("samples", matching[0]["filename"])
            if os.path.exists(sample_path):
                img_bgr = cv2.imread(sample_path)
                source_name = matching[0]["title"]

    if img_bgr is None and file:
        source_name = file.filename or "uploaded_photo.jpg"
        content = await file.read()
        nparr = np.frombuffer(content, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_bgr is None:
        raise HTTPException(
            status_code=400,
            detail="No valid image provided. Please upload a file or choose a sample ID.",
        )

    orig_h, orig_w = img_bgr.shape[:2]

    # 2. Select detector engine
    engine = detector_onnx
    if backend == "pytorch" and detector_pt is not None:
        engine = detector_pt

    # 3. Run prediction & severity assessment
    t0 = time.perf_counter()
    report = engine.predict(
        img_bgr,
        conf_threshold=conf_threshold,
        iou_threshold=iou_threshold,
    )
    report.source_info = source_name
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # 4. Render visual annotations
    vis = RoadDamageVisualizer(show_hud=show_hud)
    annotated_bgr = vis.draw(img_bgr, report)

    # 5. Extract forensic thumbnail crops for each defect
    thumbs = vis.create_thumbnail_grid(img_bgr, report, thumb_size=200)
    thumb_map = {det.id: image_to_base64_jpeg(crop, quality=85) for det, crop in thumbs}

    # 6. Format response data
    base64_annotated = image_to_base64_jpeg(annotated_bgr, quality=88)
    base64_raw = image_to_base64_jpeg(img_bgr, quality=85)

    defects_data = []
    for d in report.detections:
        defects_data.append({
            "id": d.id,
            "class_id": d.class_id,
            "class_name": d.class_name,
            "confidence": d.confidence,
            "bbox": {
                "x1": d.bbox[0],
                "y1": d.bbox[1],
                "x2": d.bbox[2],
                "y2": d.bbox[3],
                "width": round(d.bbox[2] - d.bbox[0], 1),
                "height": round(d.bbox[3] - d.bbox[1], 1),
            },
            "bbox_normalized": {
                "x1": d.bbox_normalized[0],
                "y1": d.bbox_normalized[1],
                "x2": d.bbox_normalized[2],
                "y2": d.bbox_normalized[3],
            },
            "severity": {
                "level": d.severity.level,
                "score": d.severity.score,
                "color_hex": SEVERITY_COLORS_HEX.get(d.severity.level, "#22c55e"),
                "area_pixels": d.severity.area_pixels,
                "area_pct": d.severity.area_pct,
                "aspect_ratio": d.severity.aspect_ratio,
                "edge_density": d.severity.edge_density,
                "contrast_delta": d.severity.contrast_delta,
                "rationale": d.severity.rationale,
                "recommended_action": d.severity.recommended_action,
            },
            "crop_base64": thumb_map.get(d.id, ""),
        })

    return {
        "success": True,
        "metadata": {
            "source": source_name,
            "width": orig_w,
            "height": orig_h,
            "inference_time_ms": round(elapsed_ms, 1),
            "backend": report.backend_used,
        },
        "summary": {
            "health_score": report.summary.health_score,
            "status": report.summary.status,
            "total_defects": report.summary.total_defects,
            "critical_defects_count": report.summary.critical_defects_count,
            "severity_counts": report.summary.severity_counts,
            "class_counts": report.summary.class_counts,
            "urgency": report.summary.estimated_maintenance_urgency,
            "action_items": report.summary.action_items,
        },
        "defects": defects_data,
        "images": {
            "raw": base64_raw,
            "annotated": base64_annotated,
        },
    }


# Mount sample images directory for direct preview
os.makedirs("samples", exist_ok=True)
app.mount("/samples", StaticFiles(directory="samples"), name="samples")

# Mount static directory for frontend assets
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🚀 ROAD DAMAGE DETECTION & SEVERITY ASSESSMENT WEB APP")
    print("👉 Serving at: http://127.0.0.1:8000")
    print("=" * 60 + "\n")
    uvicorn.run("web_server:app", host="0.0.0.0", port=8000, reload=False)
