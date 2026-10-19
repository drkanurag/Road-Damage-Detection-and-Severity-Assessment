"""
Automated Unit Test Suite for Road Damage Detection and Severity Assessment.
"""

import os
import unittest
import numpy as np
import cv2

from road_damage_vision import (
    DEFECT_CLASSES,
    RoadDamageDetector,
    RoadDamageVisualizer,
    SeverityEstimator,
    generate_markdown_summary,
    report_to_dict,
    save_csv_report,
    save_json_report,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
)


class TestRoadDamageSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_image = "samples/pothole_sample.jpg"
        cls.detector_onnx = RoadDamageDetector(backend="onnx")
        cls.visualizer = RoadDamageVisualizer()
        cls.severity_estimator = SeverityEstimator()

    def test_required_classes_present(self):
        """Verify the 4 required defect categories are defined."""
        class_names = set(DEFECT_CLASSES.values())
        self.assertIn("Pothole", class_names)
        self.assertIn("Longitudinal crack", class_names)
        self.assertIn("Transverse crack", class_names)
        self.assertIn("Alligator crack", class_names)

    def test_onnx_inference_and_localization(self):
        """Verify ONNX model produces valid bounding boxes and detections."""
        report = self.detector_onnx.predict(self.sample_image, conf_threshold=0.20)
        self.assertGreater(len(report.detections), 0)
        self.assertGreater(report.image_shape[0], 0)
        self.assertGreater(report.image_shape[1], 0)
        self.assertLess(report.inference_time_ms, 300.0)  # Lightweight CPU speed target

        for det in report.detections:
            x1, y1, x2, y2 = det.bbox
            self.assertGreaterEqual(x1, 0.0)
            self.assertGreaterEqual(y1, 0.0)
            self.assertGreater(x2, x1)
            self.assertGreater(y2, y1)
            self.assertIn(det.severity.level, [SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH])
            self.assertGreaterEqual(det.severity.score, 0.0)
            self.assertLessEqual(det.severity.score, 1.0)

    def test_pytorch_inference(self):
        """Verify PyTorch backend executes properly."""
        detector_pt = RoadDamageDetector(backend="pytorch")
        report = detector_pt.predict(self.sample_image, conf_threshold=0.25)
        self.assertIsNotNone(report)
        self.assertGreaterEqual(len(report.detections), 1)

    def test_severity_pothole_scaling(self):
        """Verify small vs large pothole severity thresholds."""
        img_shape = (1000, 1000)
        
        # Small shallow pothole (<0.4% area)
        small_box = (100, 100, 150, 150) # 2500 px = 0.25%
        res_low = self.severity_estimator.estimate("Pothole", small_box, img_shape)
        self.assertEqual(res_low.level, SEVERITY_LOW)

        # Huge deep pothole (>1.5% area)
        large_box = (100, 100, 300, 300) # 40000 px = 4.0%
        res_high = self.severity_estimator.estimate("Pothole", large_box, img_shape)
        self.assertEqual(res_high.level, SEVERITY_HIGH)

    def test_severity_cracks_scaling(self):
        """Verify hairline vs major crack severity."""
        img_shape = (1000, 1000)

        # Hairline longitudinal crack (<14% span)
        short_crack = (200, 200, 220, 300) # height 100 = 10% span
        res_crack_low = self.severity_estimator.estimate("Longitudinal crack", short_crack, img_shape)
        self.assertEqual(res_crack_low.level, SEVERITY_LOW)

        # Major longitudinal fracture (>32% span)
        long_crack = (200, 100, 240, 600) # height 500 = 50% span
        res_crack_high = self.severity_estimator.estimate("Longitudinal crack", long_crack, img_shape)
        self.assertEqual(res_crack_high.level, SEVERITY_HIGH)

    def test_road_health_calculation(self):
        """Verify Pavement Condition Index logic."""
        # Clean road
        clean_health = self.severity_estimator.compute_road_health([])
        self.assertEqual(clean_health.health_score, 100.0)
        self.assertEqual(clean_health.status, "Good")

        # Severely damaged road
        severe_distress = [
            ("Pothole", SEVERITY_HIGH),
            ("Pothole", SEVERITY_HIGH),
            ("Alligator crack", SEVERITY_HIGH),
        ]
        severe_health = self.severity_estimator.compute_road_health(severe_distress)
        self.assertLess(severe_health.health_score, 40.0)
        self.assertEqual(severe_health.status, "Critical")

    def test_visualizer_output(self):
        """Verify visualization renders correct image dimensions and HUD."""
        report = self.detector_onnx.predict(self.sample_image, conf_threshold=0.25)
        annotated = self.visualizer.draw(self.sample_image, report)
        self.assertEqual(len(annotated.shape), 3)
        self.assertEqual(annotated.shape[2], 3)

        # Thumbnail extraction
        thumbs = self.visualizer.create_thumbnail_grid(self.sample_image, report)
        self.assertEqual(len(thumbs), len(report.detections))

    def test_reporting_exports(self):
        """Verify JSON, CSV, and Markdown exports."""
        report = self.detector_onnx.predict(self.sample_image, conf_threshold=0.25)
        
        # JSON dict
        d = report_to_dict(report)
        self.assertIn("road_condition_summary", d)
        self.assertIn("defects", d)

        # Files export
        test_json = "samples/_temp_test_report.json"
        test_csv = "samples/_temp_test_defects.csv"
        try:
            save_json_report(report, test_json)
            save_csv_report(report, test_csv)
            self.assertTrue(os.path.exists(test_json))
            self.assertTrue(os.path.exists(test_csv))
        finally:
            if os.path.exists(test_json):
                os.remove(test_json)
            if os.path.exists(test_csv):
                os.remove(test_csv)

        # Markdown
        md = generate_markdown_summary(report)
        self.assertIn("Road Pavement Distress", md)
        self.assertIn("PCI", md)

    def test_pothole_only_precision_policy(self):
        """Only confirmed potholes may reach the public detection report."""
        # A multi-defect frame may contain a pothole, but cracks must not be reported.
        rep_multi = self.detector_onnx.predict("samples/multi_defect_pavement.jpg", conf_threshold=0.20)
        self.assertGreaterEqual(len(rep_multi.detections), 1)
        self.assertTrue(all(d.class_name == "Pothole" for d in rep_multi.detections))

        # A road containing only linear cracks must not be converted into potholes.
        rep_cracks = self.detector_onnx.predict("samples/transverse_longitudinal_crack.jpg", conf_threshold=0.20)
        self.assertEqual(rep_cracks.detections, [])

        # Regional road imagery retains at least one confirmed pothole.
        rep_india = self.detector_onnx.predict("samples/india_barricade_potholes.jpg", conf_threshold=0.20)
        self.assertGreaterEqual(len(rep_india.detections), 1)
        self.assertTrue(all(d.class_name == "Pothole" for d in rep_india.detections))

    def test_road_surface_filter_rejects_out_of_road_objects(self):
        """Verify RoadSurfaceFilter rejects sky, buildings, car hoods, and sidewalks."""
        from road_damage_vision.road_filter import RoadSurfaceFilter

        rf = RoadSurfaceFilter()
        # Synthetic dashcam test image (600x1000): top 30% sky/buildings, middle 55% road, bottom 15% orange car hood
        test_img = np.zeros((600, 1000, 3), dtype=np.uint8)
        # Upper sky/building
        test_img[:180, :] = [220, 180, 140]
        # Asphalt road surface (neutral gray)
        test_img[180:520, :] = [65, 65, 65]
        # Painted car hood (bright orange)
        test_img[520:, :] = [20, 80, 220]

        # 1. Box in sky / upper building
        sky_box = (400, 50, 600, 120)
        res_sky = rf.verify_candidate(sky_box, test_img, is_dashcam=True)
        self.assertFalse(res_sky.is_on_road)
        self.assertIn("horizon", res_sky.rejection_reason.lower())

        # 2. Box on vehicle hood
        hood_box = (100, 530, 350, 580)
        res_hood = rf.verify_candidate(hood_box, test_img, is_dashcam=True)
        self.assertFalse(res_hood.is_on_road)
        self.assertTrue("hood" in res_hood.rejection_reason.lower() or "saturation" in res_hood.rejection_reason.lower())

        # 3. Box outside road corridor on upper-left/right periphery
        periphery_box = (50, 220, 150, 280)
        res_periph = rf.verify_candidate(periphery_box, test_img, is_dashcam=True)
        self.assertFalse(res_periph.is_on_road)
        self.assertIn("corridor", res_periph.rejection_reason.lower())

        # 4. Valid pothole on the asphalt road surface
        road_pothole_box = (450, 360, 550, 420)
        res_road = rf.verify_candidate(road_pothole_box, test_img, is_dashcam=True)
        self.assertTrue(res_road.is_on_road)


if __name__ == "__main__":
    unittest.main()
