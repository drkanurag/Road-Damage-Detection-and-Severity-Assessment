"""
Road Surface & Drivable Pavement Geometric and Semantic Filter.

Guarantees that detected potholes and road distresses lie strictly ON the
drivable road pavement surface, eliminating false positives on:
  1. Sky & upper horizon (trees, clouds, utility poles, upper building floors).
  2. Multi-story buildings, balconies, roof eaves, and architectural facades.
  3. Vehicle dashboard, windshield base, wipers, and front car hood.
  4. Sidewalks, pedestrian curbs, storefronts, and peripheral off-road zones.
  5. Non-asphalt materials (painted vehicle bodywork, saturated brick, signs).
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import cv2
import numpy as np


@dataclass
class RoadFilterResult:
    """Diagnostic outcome for a candidate bounding box against road surface rules."""
    is_on_road: bool
    rejection_reason: str = ""
    road_confidence: float = 1.0


class RoadSurfaceFilter:
    """
    High-precision spatial and photometric road plane verification engine.
    
    Supports both close-up surface inspection imagery and forward-facing vehicle
    dashcam footage (GoPro, smartphone windshield mount, dashcam).
    """

    def __init__(
        self,
        horizon_ratio: float = 0.32,
        hood_ratio: float = 0.88,
        lane_vanishing_x: float = 0.50,
        min_lane_half_width: float = 0.20,
        max_lane_half_width: float = 0.46,
        max_asphalt_saturation: float = 115.0,
    ):
        """
        Args:
            horizon_ratio: Maximum normalized Y above which scene is considered sky/façade.
            hood_ratio: Minimum normalized Y below which scene is vehicle hood/dashboard.
            lane_vanishing_x: Normalized X position of vanishing point / road center.
            min_lane_half_width: Road half-width at the horizon line.
            max_lane_half_width: Road half-width at the bottom of the drivable frame.
            max_asphalt_saturation: HSV saturation limit (0-255) for asphalt pavement.
        """
        self.horizon_ratio = horizon_ratio
        self.hood_ratio = hood_ratio
        self.lane_vanishing_x = lane_vanishing_x
        self.min_lane_half_width = min_lane_half_width
        self.max_lane_half_width = max_lane_half_width
        self.max_asphalt_saturation = max_asphalt_saturation

    def is_dashcam_scene(self, img_bgr: np.ndarray) -> bool:
        """
        Detects whether an image is forward-facing vehicular dashcam footage
        (with horizon, sky/buildings, and perspective road lane) versus
        top-down perpendicular pavement inspection close-ups.
        """
        h, w = img_bgr.shape[:2]
        if h < 64 or w < 64:
            return False

        # Top strip (sky / background) vs bottom strip (road pavement)
        top_strip = img_bgr[: max(10, int(h * 0.22)), :]
        bot_strip = img_bgr[int(h * 0.55) : int(h * 0.85), :]

        top_hsv = cv2.cvtColor(top_strip, cv2.COLOR_BGR2HSV)
        bot_hsv = cv2.cvtColor(bot_strip, cv2.COLOR_BGR2HSV)

        # Sky or bright buildings typically have higher brightness and distinct contrast vs road
        top_val_mean = float(np.mean(top_hsv[:, :, 2]))
        bot_val_mean = float(np.mean(bot_hsv[:, :, 2]))
        top_sat_mean = float(np.mean(top_hsv[:, :, 1]))

        # Aspect ratio: dashcam footage is typically wide (>= 1.33)
        aspect = w / float(h)

        # If top strip is significantly brighter (sky) or has high saturation (buildings/sky)
        is_wide = aspect >= 1.25
        has_sky_gradient = (top_val_mean - bot_val_mean > 18.0) or (top_sat_mean > 45.0 and top_val_mean > 120.0)

        return is_wide and (has_sky_gradient or aspect >= 1.45)

    def verify_candidate(
        self,
        bbox: Tuple[float, float, float, float],
        img_bgr: np.ndarray,
        is_dashcam: Optional[bool] = None,
    ) -> RoadFilterResult:
        """
        Verifies whether a candidate defect bounding box (x1, y1, x2, y2)
        lies strictly on the road surface.
        """
        h, w = img_bgr.shape[:2]
        x1, y1, x2, y2 = bbox
        if x2 <= x1 or y2 <= y1 or w <= 0 or h <= 0:
            return RoadFilterResult(False, "Invalid zero-area bounding box")

        xc = (x1 + x2) / (2.0 * w)
        yc = (y1 + y2) / (2.0 * h)
        x1_norm, x2_norm = max(0.0, x1 / w), min(1.0, x2 / w)
        y1_norm, y2_norm = max(0.0, y1 / h), min(1.0, y2 / h)

        if is_dashcam is None:
            is_dashcam = self.is_dashcam_scene(img_bgr)

        # -------------------------------------------------------------
        # 1. Horizon & Sky / Façade Constraint (Always Active for Dashcams)
        # -------------------------------------------------------------
        if is_dashcam:
            if yc < self.horizon_ratio or y2_norm < (self.horizon_ratio + 0.04):
                return RoadFilterResult(
                    False,
                    f"Above road horizon (yc={yc:.2f} < {self.horizon_ratio:.2f}); located in sky or upper building façade",
                    0.0,
                )

        # -------------------------------------------------------------
        # 2. Vehicle Hood / Dashboard Suppression (Bottom of Dashcam Frame)
        # -------------------------------------------------------------
        if is_dashcam:
            # Absolute hood cutoff
            if yc > self.hood_ratio or y2_norm > 0.95:
                return RoadFilterResult(
                    False,
                    f"On vehicle dashboard/hood (yc={yc:.2f} > {self.hood_ratio:.2f})",
                    0.0,
                )

            # Curved hood corners: bottom-left & bottom-right
            if yc > 0.76 and (xc < 0.28 or xc > 0.72):
                ix1, iy1 = max(0, int(x1)), max(0, int(y1))
                ix2, iy2 = min(w, int(x2)), min(h, int(y2))
                crop = img_bgr[iy1:iy2, ix1:ix2]
                if crop.size > 0:
                    crop_hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
                    sat_mean = float(np.mean(crop_hsv[:, :, 1]))
                    # Painted vehicle bodywork typically has strong chromatic saturation
                    if sat_mean > 95.0:
                        return RoadFilterResult(
                            False,
                            f"Vehicle painted hood/bodywork (saturation={sat_mean:.1f})",
                            0.0,
                        )

        # -------------------------------------------------------------
        # 3. Trapezoidal Drivable Road Corridor (Perspective Boundary)
        # -------------------------------------------------------------
        if is_dashcam:
            # Progress down from horizon (0.0) to bottom hood line (1.0)
            t = (yc - self.horizon_ratio) / max(0.01, (self.hood_ratio - self.horizon_ratio))
            t = max(0.0, min(1.0, t))
            half_w = self.min_lane_half_width + (self.max_lane_half_width - self.min_lane_half_width) * (t ** 0.85)
            x_min_road = max(0.0, self.lane_vanishing_x - half_w)
            x_max_road = min(1.0, self.lane_vanishing_x + half_w)

            if xc < x_min_road or xc > x_max_road:
                return RoadFilterResult(
                    False,
                    f"Outside drivable road corridor (xc={xc:.2f} outside [{x_min_road:.2f}, {x_max_road:.2f}])",
                    0.0,
                )

        # -------------------------------------------------------------
        # 4. Asphalt Chrominance & Texture Material Verification
        # -------------------------------------------------------------
        ix1, iy1 = max(0, int(x1)), max(0, int(y1))
        ix2, iy2 = min(w, int(x2)), min(h, int(y2))
        crop = img_bgr[iy1:iy2, ix1:ix2]
        if crop.size == 0:
            return RoadFilterResult(False, "Empty crop", 0.0)

        crop_hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        sat_mean = float(np.mean(crop_hsv[:, :, 1]))

        # Pavement is neutral gray/dark; high saturation indicates brick buildings,
        # sky billboards, or colorful vehicle paint
        if sat_mean > self.max_asphalt_saturation:
            return RoadFilterResult(
                False,
                f"Non-asphalt material: chromatic saturation ({sat_mean:.1f} > {self.max_asphalt_saturation:.1f})",
                0.0,
            )

        # -------------------------------------------------------------
        # 5. Passed all road surface filters
        # -------------------------------------------------------------
        road_score = 1.0 - min(0.35, max(0.0, sat_mean / 255.0))
        return RoadFilterResult(True, "Valid drivable road pavement surface", road_score)

    def filter_detections(
        self,
        detections: List[Tuple[int, float, Tuple[float, float, float, float]]],
        img_bgr: np.ndarray,
    ) -> List[Tuple[int, float, Tuple[float, float, float, float]]]:
        """
        Filters a list of (class_id, confidence, (x1, y1, x2, y2)) detections,
        retaining ONLY detections verified to lie on the road surface.
        """
        is_dashcam = self.is_dashcam_scene(img_bgr)
        valid: List[Tuple[int, float, Tuple[float, float, float, float]]] = []

        for cid, conf, bbox in detections:
            res = self.verify_candidate(bbox, img_bgr, is_dashcam=is_dashcam)
            if res.is_on_road:
                # Slightly adjust confidence by road surface fidelity
                adjusted_conf = min(0.99, conf * (0.90 + 0.10 * res.road_confidence))
                valid.append((cid, adjusted_conf, bbox))

        return valid

