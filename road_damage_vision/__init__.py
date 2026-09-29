"""
Road Damage Detection and Severity Assessment Package.
Lightweight computer vision pipeline for detecting potholes, longitudinal cracks,
transverse cracks, and alligator cracks with ASTM D6433 compliant severity estimation.
"""

from road_damage_vision.config import (
    DEFECT_CLASSES,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
)
from road_damage_vision.detector import Detection, RoadDamageDetector, RoadDamageReport
from road_damage_vision.report import (
    generate_markdown_summary,
    report_to_dict,
    save_csv_report,
    save_json_report,
)
from road_damage_vision.severity import RoadHealthSummary, SeverityAssessment, SeverityEstimator
from road_damage_vision.visualizer import RoadDamageVisualizer

__version__ = "1.0.0"
__all__ = [
    "RoadDamageDetector",
    "RoadDamageVisualizer",
    "SeverityEstimator",
    "Detection",
    "RoadDamageReport",
    "SeverityAssessment",
    "RoadHealthSummary",
    "DEFECT_CLASSES",
    "SEVERITY_LOW",
    "SEVERITY_MEDIUM",
    "SEVERITY_HIGH",
    "report_to_dict",
    "save_json_report",
    "save_csv_report",
    "generate_markdown_summary",
]
