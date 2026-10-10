"""
Automated Unit & Integration Test Suite for RoadVision AI Microservices Architecture.
Tests each microservice independently (Detection, Severity, Visualization, Reporting)
as well as end-to-end API Gateway orchestration and distributed tracing headers.
"""

import unittest
import cv2
import httpx

from services.api_gateway.app import app as gateway_app
from services.common.utils import encode_bgr_to_base64
from services.detection_service.app import app as detection_app
from services.reporting_service.app import app as reporting_app
from services.severity_service.app import app as severity_app
from services.visualization_service.app import app as visualization_app


class TestMicroservicesArchitecture(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_path = "samples/pothole_sample.jpg"
        img_bgr = cv2.imread(cls.sample_path)
        assert img_bgr is not None, f"Sample image missing: {cls.sample_path}"
        cls.img_h, cls.img_w = img_bgr.shape[:2]
        cls.image_b64 = encode_bgr_to_base64(img_bgr, quality=90, include_prefix=False)

    async def test_1_detection_microservice_contract(self):
        """Verify standalone Detection Microservice (/health and /v1/detect)."""
        transport = httpx.ASGITransport(app=detection_app)
        async with httpx.AsyncClient(transport=transport, base_url="http://detection") as client:
            h_res = await client.get("/health", headers={"X-Correlation-ID": "test-corr-001"})
            self.assertEqual(h_res.status_code, 200)
            self.assertEqual(h_res.headers.get("X-Correlation-ID"), "test-corr-001")
            self.assertEqual(h_res.headers.get("X-Service-Name"), "detection-service")
            self.assertEqual(h_res.json()["service"], "detection-service")

            det_res = await client.post(
                "/v1/detect",
                json={
                    "image_b64": self.image_b64,
                    "conf_threshold": 0.20,
                    "iou_threshold": 0.45,
                    "backend": "onnx",
                    "source_info": "unit_test.jpg",
                },
            )
            self.assertEqual(det_res.status_code, 200)
            payload = det_res.json()
            self.assertEqual(payload["service"], "detection-service")
            self.assertEqual(payload["image_width"], self.img_w)
            self.assertEqual(payload["image_height"], self.img_h)
            self.assertGreater(len(payload["detections"]), 0)

    async def test_2_severity_microservice_contract(self):
        """Verify standalone Severity & PCI Microservice (/health, /v1/standards, /v1/assess)."""
        transport = httpx.ASGITransport(app=severity_app)
        async with httpx.AsyncClient(transport=transport, base_url="http://severity") as client:
            std_res = await client.get("/v1/standards")
            self.assertEqual(std_res.status_code, 200)
            self.assertEqual(std_res.json()["standard"], "ASTM D6433")

            raw_detections = [
                {
                    "id": 1,
                    "class_id": 3,
                    "class_name": "Pothole",
                    "confidence": 0.82,
                    "bbox": {"x1": 50.0, "y1": 50.0, "x2": 220.0, "y2": 220.0, "width": 170.0, "height": 170.0},
                    "bbox_normalized": {"x1": 0.1, "y1": 0.1, "x2": 0.4, "y2": 0.4},
                }
            ]
            assess_res = await client.post(
                "/v1/assess",
                json={
                    "image_width": self.img_w,
                    "image_height": self.img_h,
                    "detections": raw_detections,
                    "image_b64": self.image_b64,
                },
            )
            self.assertEqual(assess_res.status_code, 200)
            data = assess_res.json()
            self.assertEqual(data["service"], "severity-service")
            self.assertEqual(len(data["detections"]), 1)
            self.assertEqual(data["detections"][0]["severity"]["level"], "High")
            self.assertLess(data["summary"]["health_score"], 100.0)

    async def test_3_visualization_and_reporting_microservices(self):
        """Verify Visualization (/v1/render) and Reporting (/v1/reports/generate) microservices."""
        assessed_detections = [
            {
                "id": 1,
                "class_id": 3,
                "class_name": "Pothole",
                "confidence": 0.85,
                "bbox": {"x1": 50.0, "y1": 50.0, "x2": 200.0, "y2": 200.0, "width": 150.0, "height": 150.0},
                "bbox_normalized": {"x1": 0.1, "y1": 0.1, "x2": 0.35, "y2": 0.35},
                "severity": {
                    "level": "High",
                    "score": 0.78,
                    "color_hex": "#ef4444",
                    "area_pixels": 22500,
                    "area_pct": 6.92,
                    "aspect_ratio": 1.0,
                    "extent_norm": 0.26,
                    "edge_density": 0.22,
                    "contrast_delta": 18.5,
                    "rationale": "Severe deep pothole.",
                    "recommended_action": "EMERGENCY patch required.",
                },
            }
        ]
        summary = {
            "health_score": 72.0,
            "status": "Fair",
            "total_defects": 1,
            "critical_defects_count": 1,
            "severity_counts": {"High": 1, "Medium": 0, "Low": 0},
            "class_counts": {"Pothole": 1},
            "urgency": "Preventative Maintenance",
            "action_items": ["[Pothole - High]: EMERGENCY patch required."],
        }

        # Test Visualization Service
        vis_transport = httpx.ASGITransport(app=visualization_app)
        async with httpx.AsyncClient(transport=vis_transport, base_url="http://vis") as client:
            vis_res = await client.post(
                "/v1/render",
                json={
                    "image_b64": self.image_b64,
                    "image_width": self.img_w,
                    "image_height": self.img_h,
                    "inference_time_ms": 34.5,
                    "backend_used": "ONNX (CPU-optimized)",
                    "source_info": "test.jpg",
                    "detections": assessed_detections,
                    "summary": summary,
                    "show_hud": True,
                    "show_badges": True,
                    "show_conf": True,
                },
            )
            self.assertEqual(vis_res.status_code, 200)
            vis_data = vis_res.json()
            self.assertTrue(vis_data["annotated_image_uri"].startswith("data:image/jpeg;base64,"))
            self.assertIn("1", vis_data["thumbnails_uri_map"])

        # Test Reporting Service
        rep_transport = httpx.ASGITransport(app=reporting_app)
        async with httpx.AsyncClient(transport=rep_transport, base_url="http://rep") as client:
            rep_res = await client.post(
                "/v1/reports/generate",
                json={
                    "source_info": "test.jpg",
                    "image_width": self.img_w,
                    "image_height": self.img_h,
                    "inference_time_ms": 34.5,
                    "backend_used": "ONNX (CPU-optimized)",
                    "summary": summary,
                    "detections": assessed_detections,
                },
            )
            self.assertEqual(rep_res.status_code, 200)
            rep_data = rep_res.json()
            self.assertTrue(rep_data["report_id"].startswith("RPT-"))
            self.assertIn("defect_id,class_name", rep_data["csv_content"])
            self.assertIn("Road Pavement Distress", rep_data["markdown_summary"])

            hist_res = await client.get("/v1/reports/history")
            self.assertEqual(hist_res.status_code, 200)
            self.assertGreaterEqual(hist_res.json()["total_records"], 1)

    async def test_4_api_gateway_orchestration_and_tracing(self):
        """Verify API Gateway orchestrates all 4 microservices and returns trace telemetry."""
        gw_transport = httpx.ASGITransport(app=gateway_app)
        async with httpx.AsyncClient(transport=gw_transport, base_url="http://gateway") as client:
            # 1. Aggregated Health
            h_res = await client.get("/api/health")
            self.assertEqual(h_res.status_code, 200)
            h_data = h_res.json()
            self.assertEqual(h_data["status"], "healthy")
            self.assertEqual(h_data["architecture"], "microservices")
            self.assertIn("detection-service", h_data["microservices"])
            self.assertIn("severity-service", h_data["microservices"])
            self.assertIn("visualization-service", h_data["microservices"])
            self.assertIn("reporting-service", h_data["microservices"])

            # 2. Topology Status
            topo_res = await client.get("/api/services/status")
            self.assertEqual(topo_res.status_code, 200)
            self.assertEqual(topo_res.json()["total_services"], 5)

            # 3. End-to-End Orchestrated Detection
            det_res = await client.post(
                "/api/detect",
                data={
                    "sample_id": "pothole_sample",
                    "conf_threshold": "0.25",
                    "iou_threshold": "0.45",
                    "show_hud": "true",
                    "show_badges": "true",
                    "show_conf": "true",
                },
                headers={"X-Correlation-ID": "e2e-trace-999"},
            )
            self.assertEqual(det_res.status_code, 200)
            body = det_res.json()
            self.assertTrue(body["success"])
            self.assertTrue(body["report_id"].startswith("RPT-"))
            self.assertEqual(body["microservices_trace"]["correlation_id"], "e2e-trace-999")
            self.assertEqual(len(body["microservices_trace"]["steps"]), 4)
            step_services = [s["service"] for s in body["microservices_trace"]["steps"]]
            self.assertEqual(
                step_services,
                [
                    "detection-service",
                    "severity-service",
                    "visualization-service",
                    "reporting-service",
                ],
            )


if __name__ == "__main__":
    unittest.main()
