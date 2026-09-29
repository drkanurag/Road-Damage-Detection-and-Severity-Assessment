"""
Reporting module for exporting road damage inspection findings to JSON, CSV,
and executive Markdown formats for maintenance dispatch systems.
"""

import csv
import json
import os
from typing import Any, Dict
from road_damage_vision.detector import RoadDamageReport


def report_to_dict(report: RoadDamageReport) -> Dict[str, Any]:
    """Converts RoadDamageReport to a clean JSON-serializable dictionary."""
    return {
        "metadata": {
            "source": report.source_info,
            "image_dimensions": {"height": report.image_shape[0], "width": report.image_shape[1]},
            "inference_time_ms": report.inference_time_ms,
            "engine": report.backend_used,
        },
        "road_condition_summary": {
            "pavement_health_score": report.summary.health_score,
            "status": report.summary.status,
            "total_defects_count": report.summary.total_defects,
            "critical_defects_count": report.summary.critical_defects_count,
            "severity_breakdown": report.summary.severity_counts,
            "defect_class_breakdown": report.summary.class_counts,
            "maintenance_urgency": report.summary.estimated_maintenance_urgency,
            "recommended_actions": report.summary.action_items,
        },
        "defects": [
            {
                "id": d.id,
                "class_id": d.class_id,
                "class_name": d.class_name,
                "confidence": d.confidence,
                "bounding_box_pixels": {
                    "x1": d.bbox[0],
                    "y1": d.bbox[1],
                    "x2": d.bbox[2],
                    "y2": d.bbox[3],
                },
                "bounding_box_normalized": {
                    "x1": d.bbox_normalized[0],
                    "y1": d.bbox_normalized[1],
                    "x2": d.bbox_normalized[2],
                    "y2": d.bbox_normalized[3],
                },
                "severity": {
                    "level": d.severity.level,
                    "score": d.severity.score,
                    "area_pixels": d.severity.area_pixels,
                    "area_percentage": d.severity.area_pct,
                    "aspect_ratio": d.severity.aspect_ratio,
                    "extent_normalized": d.severity.extent_norm,
                    "edge_density": d.severity.edge_density,
                    "contrast_delta": d.severity.contrast_delta,
                    "rationale": d.severity.rationale,
                    "recommended_action": d.severity.recommended_action,
                },
            }
            for d in report.detections
        ],
    }


def save_json_report(report: RoadDamageReport, output_path: str) -> None:
    """Exports report to JSON format."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    data = report_to_dict(report)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_csv_report(report: RoadDamageReport, output_path: str) -> None:
    """Exports detections to CSV format for GIS / Asset Management integration."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
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
        ])
        for d in report.detections:
            writer.writerow([
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
            ])


def generate_markdown_summary(report: RoadDamageReport) -> str:
    """Creates a high-level executive inspection markdown summary."""
    s = report.summary
    md = [
        "# Road Pavement Distress & Severity Assessment Report",
        "",
        f"- **Inspection Source**: `{report.source_info or 'Image Stream'}`",
        f"- **Pavement Condition Index (PCI)**: **{s.health_score:.1f} / 100** ({s.status})",
        f"- **Total Defects Detected**: {s.total_defects}",
        f"- **Critical Severity Defects**: {s.critical_defects_count}",
        f"- **Inference Speed**: {report.inference_time_ms:.1f} ms via {report.backend_used}",
        f"- **Maintenance Urgency**: {s.estimated_maintenance_urgency}",
        "",
        "### Severity Breakdown",
        f"- [HIGH] High Severity: {s.severity_counts.get('High', 0)}",
        f"- [MED]  Medium Severity: {s.severity_counts.get('Medium', 0)}",
        f"- [LOW]  Low Severity: {s.severity_counts.get('Low', 0)}",
        "",
        "### Detected Defects Log",
        "| ID | Class | Severity | Conf | Area % | Action Required |",
        "|---|---|---|---|---|---|",
    ]
    for d in report.detections:
        md.append(
            f"| #{d.id} | **{d.class_name}** | `{d.severity.level}` ({d.severity.score:.2f}) | "
            f"{d.confidence*100:.0f}% | {d.severity.area_pct:.2f}% | {d.severity.recommended_action} |"
        )

    if s.action_items:
        md.extend(["", "### Recommended Action Items"])
        for act in s.action_items:
            md.append(f"- {act}")

    return "\n".join(md)
