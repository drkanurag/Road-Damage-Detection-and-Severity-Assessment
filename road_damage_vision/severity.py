"""
Severity Assessment Engine for Road Damage.
Grounds visual defect features (bounding box geometry, area ratio, aspect ratio,
edge density, and contrast) in standard pavement engineering distress criteria
(ASTM D6433 and FHWA Road Distress Identification manuals).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np

from road_damage_vision.config import (
    DEDUCT_POINTS,
    MAINTENANCE_ACTIONS,
    ROAD_STATUS_CRITICAL,
    ROAD_STATUS_FAIR,
    ROAD_STATUS_GOOD,
    ROAD_STATUS_POOR,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
)


@dataclass
class SeverityAssessment:
    """Detailed severity assessment for an individual road defect."""
    level: str  # "Low", "Medium", "High"
    score: float  # Quantitative score between 0.0 and 1.0
    area_pixels: int
    area_pct: float  # Area as % of total image
    aspect_ratio: float
    extent_norm: float  # Longest dimension normalized to image max dimension
    edge_density: float  # Density of high-frequency edges in defect ROI
    contrast_delta: float  # Depression / dark contrast differential
    rationale: str  # Human-readable engineering rationale
    recommended_action: str  # Practical maintenance recommendation


@dataclass
class RoadHealthSummary:
    """Roadway-level condition index and health summary."""
    health_score: float  # 0 to 100 (100 = flawless, 0 = impassable)
    status: str  # "Good", "Fair", "Poor", "Critical"
    total_defects: int
    severity_counts: Dict[str, int]
    class_counts: Dict[str, int]
    critical_defects_count: int
    estimated_maintenance_urgency: str
    action_items: List[str] = field(default_factory=list)


class SeverityEstimator:
    """
    Evaluates road damage severity using multi-modal geometric and photometric features.
    
    Adheres to ASTM D6433 guidelines:
      - Low: Minor hairline cracks (<6mm equivalent), shallow/small potholes (<15cm / <0.4% area).
      - Medium: Moderate width (6-20mm), medium pothole (15-30cm / 0.4%-1.5% area), interconnected cracks.
      - High: Wide cracks (>20mm), deep/large potholes (>30cm / >1.5% area), severely spalled alligator blocks.
    """

    def __init__(
        self,
        pothole_area_thresholds: Tuple[float, float] = (0.45, 1.40),
        alligator_area_thresholds: Tuple[float, float] = (0.75, 2.20),
        crack_extent_thresholds: Tuple[float, float] = (0.14, 0.32),
    ):
        """
        Args:
            pothole_area_thresholds: (low_max_pct, med_max_pct) area percentages
            alligator_area_thresholds: (low_max_pct, med_max_pct) area percentages
            crack_extent_thresholds: (low_max_pct, med_max_pct) normalized dimension
        """
        self.pothole_area_thresh = pothole_area_thresholds
        self.alligator_area_thresh = alligator_area_thresholds
        self.crack_extent_thresh = crack_extent_thresholds

    def estimate(
        self,
        class_name: str,
        bbox: Tuple[float, float, float, float],
        img_shape: Tuple[int, int],
        confidence: float = 1.0,
        image_bgr: Optional[np.ndarray] = None,
    ) -> SeverityAssessment:
        """
        Estimates severity for a single detected defect.

        Args:
            class_name: Canonical defect class name
            bbox: (x1, y1, x2, y2) in pixel coordinates
            img_shape: (height, width) of source image
            confidence: Model confidence [0.0, 1.0]
            image_bgr: Optional full BGR image for local ROI feature extraction

        Returns:
            SeverityAssessment with level, score, metrics, and rationale.
        """
        h_img, w_img = img_shape
        x1, y1, x2, y2 = bbox
        
        # Clip to image boundaries
        x1 = max(0.0, min(float(x1), float(w_img)))
        y1 = max(0.0, min(float(y1), float(h_img)))
        x2 = max(0.0, min(float(x2), float(w_img)))
        y2 = max(0.0, min(float(y2), float(h_img)))

        box_w = max(1.0, x2 - x1)
        box_h = max(1.0, y2 - y1)
        area_px = int(box_w * box_h)
        total_img_area = float(h_img * w_img)
        area_pct = (area_px / total_img_area) * 100.0

        aspect_ratio = max(box_w, box_h) / max(1.0, min(box_w, box_h))
        max_dim = max(box_w, box_h)
        extent_norm = max_dim / float(max(h_img, w_img))

        # Photometric / Texture analysis on the ROI
        edge_density = 0.15
        contrast_delta = 0.0

        if image_bgr is not None and area_px > 16:
            ix1, iy1, ix2, iy2 = int(x1), int(y1), int(x2), int(y2)
            crop = image_bgr[iy1:iy2, ix1:ix2]
            if crop.size > 0:
                gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                # Compute Canny edge density inside bounding box
                canny_edges = cv2.Canny(gray_crop, 40, 120)
                edge_density = float(np.count_nonzero(canny_edges)) / float(gray_crop.size)

                # Surrounding context brightness vs inside depression brightness
                mean_inner = float(np.mean(gray_crop))
                # Sample a small band around the defect if within bounds
                pad = 12
                sy1 = max(0, iy1 - pad)
                sy2 = min(h_img, iy2 + pad)
                sx1 = max(0, ix1 - pad)
                sx2 = min(w_img, ix2 + pad)
                surrounding = cv2.cvtColor(image_bgr[sy1:sy2, sx1:sx2], cv2.COLOR_BGR2GRAY)
                mean_surrounding = float(np.mean(surrounding))
                contrast_delta = max(0.0, mean_surrounding - mean_inner)

        # Normalize defect category name
        c_lower = class_name.lower().replace("_", " ")

        if "pothole" in c_lower:
            level, score, rationale = self._assess_pothole(
                area_pct, extent_norm, edge_density, contrast_delta
            )
            canonical_class = "Pothole"
        elif "alligator" in c_lower:
            level, score, rationale = self._assess_alligator(
                area_pct, extent_norm, edge_density
            )
            canonical_class = "Alligator crack"
        elif "longitudinal" in c_lower:
            level, score, rationale = self._assess_longitudinal(
                box_w, box_h, extent_norm, edge_density
            )
            canonical_class = "Longitudinal crack"
        elif "transverse" in c_lower:
            level, score, rationale = self._assess_transverse(
                box_w, box_h, extent_norm, edge_density
            )
            canonical_class = "Transverse crack"
        else:
            # Generic defect fallback
            score = min(1.0, max(0.1, (area_pct / 2.0) * 0.5 + extent_norm * 0.5))
            if score < 0.35:
                level = SEVERITY_LOW
            elif score < 0.65:
                level = SEVERITY_MEDIUM
            else:
                level = SEVERITY_HIGH
            rationale = f"General surface distress with {area_pct:.2f}% relative area."
            canonical_class = "Pothole"

        rec_action = MAINTENANCE_ACTIONS.get(canonical_class, {}).get(
            level, "Inspect during routine survey."
        )

        return SeverityAssessment(
            level=level,
            score=round(score, 3),
            area_pixels=area_px,
            area_pct=round(area_pct, 3),
            aspect_ratio=round(aspect_ratio, 2),
            extent_norm=round(extent_norm, 3),
            edge_density=round(edge_density, 3),
            contrast_delta=round(contrast_delta, 1),
            rationale=rationale,
            recommended_action=rec_action,
        )

    def _assess_pothole(
        self, area_pct: float, extent_norm: float, edge_density: float, contrast: float
    ) -> Tuple[str, float, str]:
        """ASTM D6433 Pothole severity based on diameter, area, and bowl depth."""
        t_low, t_med = self.pothole_area_thresh

        # Area score component (0 to 1)
        area_score = min(1.0, area_pct / (t_med * 1.5))
        extent_score = min(1.0, extent_norm / 0.30)
        contrast_score = min(1.0, contrast / 35.0)

        # Weighted combination: Area (50%) + Extent (25%) + Depth contrast (25%)
        raw_score = 0.50 * area_score + 0.25 * extent_score + 0.25 * contrast_score
        score = min(1.0, max(0.05, raw_score))

        if area_pct < t_low and score < 0.38:
            level = SEVERITY_LOW
            rationale = (
                f"Small shallow pothole ({area_pct:.2f}% area, extent={extent_norm:.2f}). "
                "Low risk to vehicles; minor ride quality disturbance."
            )
        elif area_pct >= t_med or score >= 0.65 or contrast > 40.0:
            level = SEVERITY_HIGH
            rationale = (
                f"Severe deep pothole ({area_pct:.2f}% area, extent={extent_norm:.2f}, "
                f"contrast={contrast:.1f}). Acute hazard to vehicle rims and suspension."
            )
        else:
            level = SEVERITY_MEDIUM
            rationale = (
                f"Moderate pothole ({area_pct:.2f}% area, extent={extent_norm:.2f}). "
                "Noticeable jolt; requires scheduled patch before pothole perimeter expands."
            )

        return level, score, rationale

    def _assess_alligator(
        self, area_pct: float, extent_norm: float, edge_density: float
    ) -> Tuple[str, float, str]:
        """ASTM D6433 Alligator crack severity based on network density & fatigue extent."""
        t_low, t_med = self.alligator_area_thresh

        area_score = min(1.0, area_pct / (t_med * 1.4))
        # Edge density > 0.25 signifies highly fractured, disintegrating blocks
        edge_score = min(1.0, max(0.0, (edge_density - 0.08) / 0.24))

        raw_score = 0.60 * area_score + 0.40 * edge_score
        score = min(1.0, max(0.05, raw_score))

        if (area_pct < t_low and edge_density < 0.20) or score < 0.36:
            level = SEVERITY_LOW
            rationale = (
                f"Early-stage alligator cracking ({area_pct:.2f}% area, edge density={edge_density:.2f}). "
                "Fine parallel hairline patterns with minimal block detachment."
            )
        elif area_pct >= t_med or edge_density >= 0.28 or score >= 0.65:
            level = SEVERITY_HIGH
            rationale = (
                f"Severe alligator fatigue ({area_pct:.2f}% area, edge density={edge_density:.2f}). "
                "Heavily spalled, loose polygonal block network with base pavement degradation."
            )
        else:
            level = SEVERITY_MEDIUM
            rationale = (
                f"Developing alligator pattern ({area_pct:.2f}% area, edge density={edge_density:.2f}). "
                "Well-defined interconnected chicken-wire pattern with minor edge spalling."
            )

        return level, score, rationale

    def _assess_longitudinal(
        self, box_w: float, box_h: float, extent_norm: float, edge_density: float
    ) -> Tuple[str, float, str]:
        """ASTM D6433 Longitudinal crack severity based on length and crack width."""
        t_low, t_med = self.crack_extent_thresh

        # Extent score based on normalized length along pavement
        extent_score = min(1.0, extent_norm / (t_med * 1.5))
        density_score = min(1.0, edge_density / 0.25)
        raw_score = 0.70 * extent_score + 0.30 * density_score
        score = min(1.0, max(0.05, raw_score))

        if extent_norm < t_low and score < 0.36:
            level = SEVERITY_LOW
            rationale = (
                f"Narrow hairline longitudinal crack (span={extent_norm:.2f}). "
                "Low severity; crack width < 6mm equivalent with intact joint."
            )
        elif extent_norm >= t_med or score >= 0.65:
            level = SEVERITY_HIGH
            rationale = (
                f"Extensive longitudinal crack (span={extent_norm:.2f}). "
                "High severity; wide crack with continuous joint opening and aggregate loss."
            )
        else:
            level = SEVERITY_MEDIUM
            rationale = (
                f"Moderate longitudinal crack (span={extent_norm:.2f}). "
                "Crack width 6-20mm with slight edge spalling along wheel path."
            )

        return level, score, rationale

    def _assess_transverse(
        self, box_w: float, box_h: float, extent_norm: float, edge_density: float
    ) -> Tuple[str, float, str]:
        """ASTM D6433 Transverse crack severity based on lane span and roughness."""
        t_low, t_med = self.crack_extent_thresh

        extent_score = min(1.0, extent_norm / (t_med * 1.5))
        density_score = min(1.0, edge_density / 0.25)
        raw_score = 0.70 * extent_score + 0.30 * density_score
        score = min(1.0, max(0.05, raw_score))

        if extent_norm < t_low and score < 0.36:
            level = SEVERITY_LOW
            rationale = (
                f"Minor transverse crack (lane span={extent_norm:.2f}). "
                "Narrow width (<6mm) spanning partial lane with smooth wheel transition."
            )
        elif extent_norm >= t_med or score >= 0.65:
            level = SEVERITY_HIGH
            rationale = (
                f"Major transverse fracture (lane span={extent_norm:.2f}). "
                "Full lane span with severe edge spalling and perceptible bump to traffic."
            )
        else:
            level = SEVERITY_MEDIUM
            rationale = (
                f"Moderate transverse crack (lane span={extent_norm:.2f}). "
                "Width 6-20mm across mid-lane with minor chipping along crack lips."
            )

        return level, score, rationale

    def compute_road_health(
        self, detections: List[Tuple[str, str]]
    ) -> RoadHealthSummary:
        """
        Calculates composite Pavement Condition Index (PCI) and overall health summary.

        Args:
            detections: List of (class_name, severity_level) tuples

        Returns:
            RoadHealthSummary with score (0-100), condition category, and action list.
        """
        score = 100.0
        sev_counts = {SEVERITY_LOW: 0, SEVERITY_MEDIUM: 0, SEVERITY_HIGH: 0}
        cls_counts: Dict[str, int] = {}
        critical_count = 0
        action_items: List[str] = []

        for cname, slevel in detections:
            sev_counts[slevel] = sev_counts.get(slevel, 0) + 1
            cls_counts[cname] = cls_counts.get(cname, 0) + 1

            if slevel == SEVERITY_HIGH:
                critical_count += 1

            # Deduct points
            class_deducts = DEDUCT_POINTS.get(cname, {})
            deduct = class_deducts.get(slevel, 8.0)
            score -= deduct

        score = max(0.0, min(100.0, round(score, 1)))

        # Determine condition status
        if score >= 85.0:
            status = ROAD_STATUS_GOOD
            urgency = "Routine Maintenance (annual inspection)"
        elif score >= 65.0:
            status = ROAD_STATUS_FAIR
            urgency = "Preventative Maintenance (within 60-90 days)"
        elif score >= 40.0:
            status = ROAD_STATUS_POOR
            urgency = "Corrective Repair Needed (within 30 days)"
        else:
            status = ROAD_STATUS_CRITICAL
            urgency = "URGENT INTERVENTION: High hazard risk to traffic"

        # Unique action items
        for cname in cls_counts:
            # prioritize highest severity found for this class
            highest_sev = SEVERITY_LOW
            if any(s == SEVERITY_HIGH for c, s in detections if c == cname):
                highest_sev = SEVERITY_HIGH
            elif any(s == SEVERITY_MEDIUM for c, s in detections if c == cname):
                highest_sev = SEVERITY_MEDIUM

            act = MAINTENANCE_ACTIONS.get(cname, {}).get(highest_sev)
            if act:
                action_items.append(f"[{cname} - {highest_sev}]: {act}")

        return RoadHealthSummary(
            health_score=score,
            status=status,
            total_defects=len(detections),
            severity_counts=sev_counts,
            class_counts=cls_counts,
            critical_defects_count=critical_count,
            estimated_maintenance_urgency=urgency,
            action_items=action_items,
        )
