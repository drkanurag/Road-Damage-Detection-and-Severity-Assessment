"""
API Gateway & Orchestrator Microservice (Port 8000)
Bounded Context: Edge Routing, Request Validation, Multi-Service Pipeline Orchestration,
Distributed Tracing (X-Correlation-ID), Circuit-Breaker Fallback, and Web UI Hosting.
"""

import os
import time
from typing import Any, Dict, List, Optional
import uuid
import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.staticfiles import StaticFiles

from road_damage_vision.config import DEFECT_CLASSES
from services.common.client import MicroserviceClient
from services.common.config import GATEWAY_HOST, GATEWAY_PORT, SERVICE_REGISTRY
from services.common.middleware import attach_microservice_middleware
from services.common.schemas import ServiceTraceStepDTO
from services.common.utils import encode_bgr_to_base64
from services.detection_service.app import app as detection_app
from services.reporting_service.app import app as reporting_app
from services.severity_service.app import app as severity_app
from services.visualization_service.app import app as visualization_app

SERVICE_NAME = "api-gateway"
START_TIME = time.time()

app = FastAPI(
    title="RoadVision AI - API Gateway & Microservices Orchestrator",
    description=(
        "Unified API Gateway orchestrating the Detection, ASTM D6433 Severity, "
        "Visualization, and Reporting microservices."
    ),
    version="2.0.0",
)
attach_microservice_middleware(app, SERVICE_NAME)

# Initialize Resilient Microservice Client & register local ASGI fallback instances
ms_client = MicroserviceClient()
ms_client.register_asgi_service("detection-service", detection_app)
ms_client.register_asgi_service("severity-service", severity_app)
ms_client.register_asgi_service("visualization-service", visualization_app)
ms_client.register_asgi_service("reporting-service", reporting_app)

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
    {
        "id": "multi_defect_pavement",
        "title": "Multi-Defect Distressed Roadway",
        "category": "Multi-Defect",
        "description": "Combined potholes, longitudinal cracks, and fatigue cracking.",
        "filename": "multi_defect_pavement.jpg",
    },
    {
        "id": "transverse_longitudinal_crack",
        "title": "Transverse & Longitudinal Joints",
        "category": "Transverse & Longitudinal",
        "description": "Intersecting thermal and wheel-path cracks across asphalt lane.",
        "filename": "transverse_longitudinal_crack.jpg",
    },
]


@app.get("/api/health")
async def gateway_health_check(request: Request) -> Dict[str, Any]:
    """
    Aggregated health check querying all downstream microservices.
    """
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    services_health: Dict[str, Any] = {}
    all_healthy = True

    for slug in SERVICE_REGISTRY:
        try:
            data, trace = await ms_client.request(slug, "GET", "/health", correlation_id)
            services_health[slug] = {
                "status": data.get("status", "healthy"),
                "transport": trace.transport,
                "latency_ms": trace.latency_ms,
                "details": data.get("details", {}),
            }
            if data.get("status") != "healthy":
                all_healthy = False
        except Exception as exc:
            all_healthy = False
            services_health[slug] = {"status": "unhealthy", "error": str(exc)}

    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": SERVICE_NAME,
        "architecture": "microservices",
        "version": "2.0.0",
        "timestamp": time.time(),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "engines": {
            "onnx": "ready (CPU-optimized)",
            "pytorch": "ready",
        },
        "default_engine": "onnx",
        "classes": list(DEFECT_CLASSES.values()),
        "microservices": services_health,
    }


@app.get("/api/services/status")
async def get_microservices_topology(request: Request) -> Dict[str, Any]:
    """Returns detailed topology and live probe status for all microservices."""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    nodes = [
        {
            "slug": "api-gateway",
            "name": "API Gateway & Orchestrator",
            "port": GATEWAY_PORT,
            "status": "healthy",
            "transport": "Edge Entrypoint",
            "latency_ms": 0.1,
            "description": "Routes client traffic, manages correlation IDs, and orchestrates the 4-stage inspection pipeline.",
            "endpoints": ["/api/detect", "/api/health", "/api/services/status", "/api/reports/history"],
        }
    ]

    endpoint_map = {
        "detection-service": ["/v1/detect", "/health"],
        "severity-service": ["/v1/assess", "/v1/standards", "/health"],
        "visualization-service": ["/v1/render", "/health"],
        "reporting-service": ["/v1/reports/generate", "/v1/reports/history", "/health"],
    }

    for slug, cfg in SERVICE_REGISTRY.items():
        try:
            data, trace = await ms_client.request(slug, "GET", "/health", correlation_id)
            nodes.append(
                {
                    "slug": slug,
                    "name": cfg.name,
                    "port": cfg.port,
                    "base_url": cfg.base_url,
                    "status": data.get("status", "healthy"),
                    "transport": trace.transport,
                    "latency_ms": trace.latency_ms,
                    "description": cfg.description,
                    "endpoints": endpoint_map.get(slug, ["/health"]),
                }
            )
        except Exception as exc:
            nodes.append(
                {
                    "slug": slug,
                    "name": cfg.name,
                    "port": cfg.port,
                    "base_url": cfg.base_url,
                    "status": "unhealthy",
                    "transport": "error",
                    "latency_ms": 0.0,
                    "description": str(exc),
                    "endpoints": endpoint_map.get(slug, ["/health"]),
                }
            )

    return {
        "architecture": "RoadVision Microservices Mesh v2.0",
        "total_services": len(nodes),
        "services": nodes,
    }


@app.get("/api/samples")
async def get_samples() -> Dict[str, Any]:
    """Returns list of curated test samples available for instant testing."""
    samples_list = []
    for s in SAMPLES_METADATA:
        path = os.path.join("samples", s["filename"])
        if os.path.exists(path):
            samples_list.append(
                {
                    **s,
                    "url": f"/samples/{s['filename']}",
                }
            )
    return {"samples": samples_list}


@app.get("/api/standards")
async def get_standards(request: Request) -> Dict[str, Any]:
    """Proxies ASTM D6433 engineering standards from the Severity Microservice."""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    data, _ = await ms_client.request("severity-service", "GET", "/v1/standards", correlation_id)
    return data


@app.get("/api/reports/history")
async def get_reports_history(request: Request) -> Dict[str, Any]:
    """Proxies inspection audit log from the Reporting Microservice."""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    data, _ = await ms_client.request(
        "reporting-service", "GET", "/v1/reports/history", correlation_id
    )
    return data


@app.post("/api/detect")
async def detect_defects_orchestrator(
    request: Request,
    file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
    conf_threshold: float = Form(0.25),
    iou_threshold: float = Form(0.45),
    backend: str = Form("onnx"),
    show_hud: bool = Form(True),
    show_badges: bool = Form(True),
    show_conf: bool = Form(True),
) -> Dict[str, Any]:
    """
    Orchestrates the end-to-end road damage inspection workflow across 4 microservices:
      1. Detection Microservice      (/v1/detect)
      2. Severity & PCI Microservice (/v1/assess)
      3. Visualization Microservice  (/v1/render)
      4. Reporting Microservice      (/v1/reports/generate)
    """
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    pipeline_t0 = time.perf_counter()
    trace_steps: List[ServiceTraceStepDTO] = []

    # 0. Load input image from sample ID or file upload
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

    image_b64 = encode_bgr_to_base64(img_bgr, quality=92, include_prefix=False)

    # 1. Invoke Detection Microservice (/v1/detect)
    det_payload = {
        "image_b64": image_b64,
        "conf_threshold": conf_threshold,
        "iou_threshold": iou_threshold,
        "backend": backend,
        "source_info": source_name,
    }
    det_resp, det_trace = await ms_client.request(
        "detection-service", "POST", "/v1/detect", correlation_id, json_payload=det_payload
    )
    trace_steps.append(det_trace)

    orig_w = det_resp["image_width"]
    orig_h = det_resp["image_height"]
    inference_ms = det_resp["inference_time_ms"]
    backend_used = det_resp["backend_used"]

    # 2. Invoke Severity & PCI Microservice (/v1/assess)
    sev_payload = {
        "image_width": orig_w,
        "image_height": orig_h,
        "detections": det_resp["detections"],
        "image_b64": image_b64,
    }
    sev_resp, sev_trace = await ms_client.request(
        "severity-service", "POST", "/v1/assess", correlation_id, json_payload=sev_payload
    )
    trace_steps.append(sev_trace)

    assessed_detections = sev_resp["detections"]
    summary_data = sev_resp["summary"]

    # 3. Invoke Visualization & Media Microservice (/v1/render)
    vis_payload = {
        "image_b64": image_b64,
        "image_width": orig_w,
        "image_height": orig_h,
        "inference_time_ms": inference_ms,
        "backend_used": backend_used,
        "source_info": source_name,
        "detections": assessed_detections,
        "summary": summary_data,
        "show_hud": show_hud,
        "show_badges": show_badges,
        "show_conf": show_conf,
        "extract_thumbnails": True,
        "thumb_size": 200,
    }
    vis_resp, vis_trace = await ms_client.request(
        "visualization-service", "POST", "/v1/render", correlation_id, json_payload=vis_payload
    )
    trace_steps.append(vis_trace)

    thumb_map = vis_resp.get("thumbnails_uri_map", {})
    for d in assessed_detections:
        did = d["id"]
        d["crop_base64"] = thumb_map.get(str(did)) or thumb_map.get(did, "")

    # 4. Invoke Reporting & Audit Microservice (/v1/reports/generate)
    rep_payload = {
        "source_info": source_name,
        "image_width": orig_w,
        "image_height": orig_h,
        "inference_time_ms": inference_ms,
        "backend_used": backend_used,
        "summary": summary_data,
        "detections": assessed_detections,
    }
    rep_resp, rep_trace = await ms_client.request(
        "reporting-service",
        "POST",
        "/v1/reports/generate",
        correlation_id,
        json_payload=rep_payload,
    )
    trace_steps.append(rep_trace)

    total_pipeline_ms = round((time.perf_counter() - pipeline_t0) * 1000.0, 1)

    return {
        "success": True,
        "report_id": rep_resp["report_id"],
        "metadata": {
            "source": source_name,
            "width": orig_w,
            "height": orig_h,
            "inference_time_ms": round(inference_ms, 1),
            "pipeline_total_ms": total_pipeline_ms,
            "backend": backend_used,
            "correlation_id": correlation_id,
        },
        "summary": summary_data,
        "defects": assessed_detections,
        "images": {
            "raw": vis_resp["raw_image_uri"],
            "annotated": vis_resp["annotated_image_uri"],
        },
        "reports": {
            "report_id": rep_resp["report_id"],
            "markdown_summary": rep_resp["markdown_summary"],
            "csv_content": rep_resp["csv_content"],
        },
        "microservices_trace": {
            "correlation_id": correlation_id,
            "total_pipeline_ms": total_pipeline_ms,
            "steps": [step.model_dump() for step in trace_steps],
        },
    }


# Mount sub-service ASGI apps under /services/* for direct Swagger / OpenAPI inspection
app.mount("/services/detection", detection_app, name="detection-service")
app.mount("/services/severity", severity_app, name="severity-service")
app.mount("/services/visualization", visualization_app, name="visualization-service")
app.mount("/services/reporting", reporting_app, name="reporting-service")

# Mount sample images directory for direct preview
os.makedirs("samples", exist_ok=True)
app.mount("/samples", StaticFiles(directory="samples"), name="samples")

# Mount static directory for frontend assets
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
