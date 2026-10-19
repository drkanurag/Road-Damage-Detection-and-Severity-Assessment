"""
Unified Road Damage Detector supporting ONNX Runtime (CPU-optimized lightweight inference)
and PyTorch Ultralytics backends.
"""

from dataclasses import dataclass, field
import os
import time
from typing import List, Optional, Tuple, Union
import cv2
import numpy as np
from PIL import Image

from road_damage_vision.config import (
    CLASS_ALIASES,
    DEFAULT_CONF_THRESHOLD,
    DEFAULT_IMG_SIZE,
    DEFAULT_IOU_THRESHOLD,
    DEFAULT_ONNX_MODEL_PATH,
    DEFAULT_ORT_THREADS,
    DEFAULT_PT_MODEL_PATH,
    DEFECT_CLASSES,
    SPECIALIST_ONNX_MODEL_PATH,
    SPECIALIST_PT_MODEL_PATH,
)
from road_damage_vision.road_filter import RoadSurfaceFilter
from road_damage_vision.severity import RoadHealthSummary, SeverityAssessment, SeverityEstimator


@dataclass
class Detection:
    """Represents a localized, classified, and severity-scored road defect."""
    id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2) in pixels
    bbox_normalized: Tuple[float, float, float, float]  # (x1/W, y1/H, x2/W, y2/H)
    severity: SeverityAssessment


@dataclass
class RoadDamageReport:
    """Complete diagnostic report for a road surface image."""
    image_shape: Tuple[int, int]  # (height, width)
    detections: List[Detection]
    summary: RoadHealthSummary
    inference_time_ms: float
    backend_used: str
    source_info: str = ""


class RoadDamageDetector:
    """
    High-performance, lightweight road defect detector and severity classifier.
    
    Uses a Dual-Model Specialist Ensemble (Global RDD2022 Multi-Class + India Pothole
    Specialist) with Weighted Box Fusion (WBF) and Containment NMS by default,
    running on ONNX Runtime for ultra-fast execution on standard CPUs.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        backend: str = "onnx",
        img_size: int = DEFAULT_IMG_SIZE,
        conf_threshold: float = DEFAULT_CONF_THRESHOLD,
        iou_threshold: float = DEFAULT_IOU_THRESHOLD,
        ensemble: bool = True,
        pothole_only: bool = True,
        filter_road_surface: bool = True,
    ):
        """
        Args:
            model_path: Path to .onnx or .pt model file. If None, uses default.
            backend: 'onnx' (recommended for CPU) or 'pytorch'.
            img_size: Input resolution (default 640).
            conf_threshold: Minimum detection confidence (0.0 to 1.0).
            iou_threshold: IoU overlap threshold for Non-Maximum Suppression.
            ensemble: Whether to fuse predictions with the secondary regional specialist model.
            pothole_only: Return only confirmed potholes. Enabled by default so
                unrelated objects are never reported as road damage.
            filter_road_surface: Enforce strict road surface & drivable pavement spatial
                and photometric validation to reject buildings, car hoods, sky, and sidewalks.
        """
        self.backend = backend.lower()
        self.img_size = img_size
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.pothole_only = pothole_only
        self.filter_road_surface = filter_road_surface
        self.road_filter = RoadSurfaceFilter()
        self.severity_estimator = SeverityEstimator()

        if model_path is None:
            if self.backend == "onnx":
                model_path = DEFAULT_ONNX_MODEL_PATH
            else:
                model_path = DEFAULT_PT_MODEL_PATH

        self.model_path = model_path
        self.specialist_path: Optional[str] = None
        if ensemble and self.model_path in (DEFAULT_ONNX_MODEL_PATH, DEFAULT_PT_MODEL_PATH):
            cand_spec = (
                SPECIALIST_ONNX_MODEL_PATH
                if self.backend == "onnx"
                else SPECIALIST_PT_MODEL_PATH
            )
            if os.path.exists(cand_spec) and os.path.abspath(cand_spec) != os.path.abspath(self.model_path):
                self.specialist_path = cand_spec

        self.use_ensemble = self.specialist_path is not None
        self._init_backend()

    def _init_backend(self) -> None:
        """Loads model(s) into memory using the selected engine."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model file not found at: {self.model_path}. "
                "Ensure models/rdd2022_yolov8n.onnx or .pt exists."
            )

        if self.backend == "onnx":
            import onnxruntime as ort

            # Optimal thread count avoids OpenMP spin-wait overhead on multi-core CPUs
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.intra_op_num_threads = min(
                DEFAULT_ORT_THREADS, max(1, os.cpu_count() or 4)
            )

            self.session = ort.InferenceSession(
                self.model_path,
                sess_options=sess_options,
                providers=["CPUExecutionProvider"],
            )
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            # Pre-allocate ONNX Runtime memory arena so first inference is sub-50ms
            dummy = np.zeros((1, 3, self.img_size, self.img_size), dtype=np.float32)
            self.session.run([self.output_name], {self.input_name: dummy})

            self.specialist_session = None
            if self.use_ensemble and self.specialist_path:
                self.specialist_session = ort.InferenceSession(
                    self.specialist_path,
                    sess_options=sess_options,
                    providers=["CPUExecutionProvider"],
                )
                self.spec_input_name = self.specialist_session.get_inputs()[0].name
                self.spec_output_name = self.specialist_session.get_outputs()[0].name
                self.specialist_session.run(
                    [self.spec_output_name], {self.spec_input_name: dummy}
                )

            self.model = None
            self.specialist_model = None

        elif self.backend == "pytorch":
            from ultralytics import YOLO

            self.model = YOLO(self.model_path)
            self.specialist_model = (
                YOLO(self.specialist_path)
                if (self.use_ensemble and self.specialist_path)
                else None
            )
            self.session = None
            self.specialist_session = None

        else:
            raise ValueError(f"Unsupported backend '{self.backend}'. Use 'onnx' or 'pytorch'.")

    def _letterbox(
        self, img: np.ndarray, new_shape: int = 640, color: Tuple[int, int, int] = (114, 114, 114)
    ) -> Tuple[np.ndarray, float, Tuple[int, int]]:
        """
        Resizes and pads image to square while maintaining aspect ratio.
        
        Returns:
            padded_img, scale_ratio, (pad_x, pad_y)
        """
        h, w = img.shape[:2]
        r = min(new_shape / h, new_shape / w)
        new_w, new_h = int(round(w * r)), int(round(h * r))

        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        pad_x = (new_shape - new_w) // 2
        pad_y = (new_shape - new_h) // 2

        padded = np.full((new_shape, new_shape, 3), color, dtype=np.uint8)
        padded[pad_y : pad_y + new_h, pad_x : pad_x + new_w] = resized

        return padded, r, (pad_x, pad_y)

    def _preprocess_onnx(self, img_bgr: np.ndarray) -> Tuple[np.ndarray, float, Tuple[int, int]]:
        """Prepares raw BGR image for ONNX model tensor input."""
        padded, r, (pad_x, pad_y) = self._letterbox(img_bgr, self.img_size)
        # BGR -> RGB -> HWC to CHW -> Float32 / 255.0
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        tensor = rgb.transpose(2, 0, 1).astype(np.float32) / 255.0
        tensor = np.expand_dims(tensor, axis=0)  # [1, 3, H, W]
        return tensor, r, (pad_x, pad_y)

    def _postprocess_onnx(
        self,
        output_tensor: np.ndarray,
        orig_shape: Tuple[int, int],
        ratio: float,
        pad: Tuple[int, int],
        conf_thresh: float,
        iou_thresh: float,
    ) -> List[Tuple[int, float, Tuple[float, float, float, float]]]:
        """
        Parses raw YOLO ONNX outputs [1, 8, 8400] -> NMS -> Original Image Coordinates.
        
        Returns:
            List of (class_id, confidence, (x1, y1, x2, y2))
        """
        orig_h, orig_w = orig_shape
        pad_x, pad_y = pad

        # Transpose [1, 8, 8400] to [8400, 8]
        preds = output_tensor[0].T

        boxes = preds[:, :4]  # [cx, cy, w, h]
        class_scores = preds[:, 4:]  # 4 classes

        max_scores = class_scores.max(axis=1)
        class_ids = class_scores.argmax(axis=1)
        # A dedicated pothole model has one output class (index 0). Keep the
        # public id at 3 so existing severity and visualisation code remains
        # compatible with the RDD class map.
        if class_scores.shape[1] == 1:
            class_ids = np.full_like(class_ids, 3)

        # Filter by confidence threshold
        mask = max_scores >= conf_thresh
        if not np.any(mask):
            return []

        cand_boxes = boxes[mask]
        cand_scores = max_scores[mask]
        cand_classes = class_ids[mask]

        # Convert [cx, cy, w, h] to [x1, y1, w, h] for cv2.dnn.NMSBoxes
        nms_boxes = []
        for cx, cy, bw, bh in cand_boxes:
            x1 = cx - bw / 2.0
            y1 = cy - bh / 2.0
            nms_boxes.append([float(x1), float(y1), float(bw), float(bh)])

        indices = cv2.dnn.NMSBoxes(nms_boxes, cand_scores.tolist(), conf_thresh, iou_thresh)
        if len(indices) == 0:
            return []

        results = []
        for idx in indices:
            i = int(idx)
            x1, y1, bw, bh = nms_boxes[i]
            cid = int(cand_classes[i])
            score = float(cand_scores[i])

            # Invert padding and aspect scaling
            orig_x1 = max(0.0, (x1 - pad_x) / ratio)
            orig_y1 = max(0.0, (y1 - pad_y) / ratio)
            orig_x2 = min(float(orig_w), (x1 + bw - pad_x) / ratio)
            orig_y2 = min(float(orig_h), (y1 + bh - pad_y) / ratio)

            # Ensure valid box dimensions
            if orig_x2 > orig_x1 and orig_y2 > orig_y1:
                results.append((cid, score, (orig_x1, orig_y1, orig_x2, orig_y2)))

        return results

    @staticmethod
    def _box_iou_and_containment(
        b1: Tuple[float, float, float, float],
        b2: Tuple[float, float, float, float],
    ) -> Tuple[float, float]:
        """Computes standard Intersection-over-Union (IoU) and Intersection-over-Minimum-Area (IoMin)."""
        ix1 = max(b1[0], b2[0])
        iy1 = max(b1[1], b2[1])
        ix2 = min(b1[2], b2[2])
        iy2 = min(b1[3], b2[3])
        inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
        a1 = max(1e-6, (b1[2] - b1[0]) * (b1[3] - b1[1]))
        a2 = max(1e-6, (b2[2] - b2[0]) * (b2[3] - b2[1]))
        union = a1 + a2 - inter
        iou = inter / union if union > 0 else 0.0
        containment = inter / min(a1, a2)
        return iou, containment

    def _fuse_ensemble_detections(
        self,
        det_global: List[Tuple[int, float, Tuple[float, float, float, float]]],
        det_specialist: List[Tuple[int, float, Tuple[float, float, float, float]]],
        conf_thresh: float,
    ) -> List[Tuple[int, float, Tuple[float, float, float, float]]]:
        """
        Fuses predictions from the Global Multi-Class RDD2022 model and the Regional
        Pothole Specialist model using Domain-Aware Gated Weighted Box Fusion (WBF),
        class-conflict resolution, and Containment-Aware Non-Maximum Suppression.
        """
        fused: List[Tuple[int, float, Tuple[float, float, float, float]]] = []
        used_spec = set()

        # Assess whether the Global Multi-Class model already has strong confidence
        # or multiple crack detections on this frame
        max_global_conf = max((c[1] for c in det_global), default=0.0)
        global_crack_count = sum(1 for c in det_global if c[0] in (0, 1, 2))
        global_crack_dominant = (max_global_conf >= 0.50) or (global_crack_count >= 2)

        for g_cid, g_conf, g_box in det_global:
            matches = []
            for j, (s_cid, s_conf, s_box) in enumerate(det_specialist):
                iou, cont = self._box_iou_and_containment(g_box, s_box)
                if iou >= 0.15 or cont >= 0.40:
                    matches.append((j, s_cid, s_conf, s_box, iou))

            if matches:
                for m in matches:
                    used_spec.add(m[0])
                best_m = max(matches, key=lambda x: x[2])
                _, s_cid, s_conf, s_box, best_iou = best_m

                if g_cid == s_cid and best_iou >= 0.30:
                    # Both models agree on class & location: Weighted Box Fusion + confidence boost
                    w1, w2 = g_conf, s_conf
                    fx1 = (g_box[0] * w1 + s_box[0] * w2) / (w1 + w2)
                    fy1 = (g_box[1] * w1 + s_box[1] * w2) / (w1 + w2)
                    fx2 = (g_box[2] * w1 + s_box[2] * w2) / (w1 + w2)
                    fy2 = (g_box[3] * w1 + s_box[3] * w2) / (w1 + w2)
                    f_conf = min(0.98, max(g_conf, s_conf) + 0.12 * min(g_conf, s_conf))
                    fused.append((g_cid, f_conf, (fx1, fy1, fx2, fy2)))
                else:
                    # Class conflict resolution:
                    # Global model has superior multi-class crack discrimination (classes 0, 1, 2)
                    if g_cid in (0, 1, 2) and s_cid == 3:
                        fused.append((g_cid, min(0.95, g_conf + 0.05), g_box))
                    elif g_conf >= s_conf:
                        fused.append((g_cid, g_conf, g_box))
                    else:
                        fused.append((s_cid, s_conf, s_box))
            else:
                fused.append((g_cid, g_conf, g_box))

        # Incorporate non-overlapping specialist pothole detections on weathered/Indian roads
        for j, (s_cid, s_conf, s_box) in enumerate(det_specialist):
            if j in used_spec:
                continue
            overlaps_existing = any(
                self._box_iou_and_containment(s_box, f_box)[0] >= 0.15
                or self._box_iou_and_containment(s_box, f_box)[1] >= 0.40
                for _, _, f_box in fused
            )
            if overlaps_existing:
                continue

            if global_crack_dominant:
                # Frame already has strong Global multi-class detections; only allow high-confidence
                # independent specialist detections to avoid crack-fragment false positives
                if s_conf >= max(0.45, conf_thresh + 0.20):
                    fused.append((s_cid, s_conf, s_box))
            else:
                # Weathered / Indian asphalt domain where Global model has low recall
                if s_cid == 3:
                    calib_conf = min(0.92, s_conf * 1.18)
                    if calib_conf >= conf_thresh:
                        fused.append((s_cid, calib_conf, s_box))
                elif s_conf >= conf_thresh + 0.08:
                    fused.append((s_cid, s_conf, s_box))

        # Final Containment-Aware NMS to eliminate nested redundant bounding boxes
        fused.sort(key=lambda x: x[1], reverse=True)
        final_boxes: List[Tuple[int, float, Tuple[float, float, float, float]]] = []
        for cid, conf, box in fused:
            if conf < conf_thresh:
                continue
            keep = True
            for k_cid, _, k_box in final_boxes:
                iou, cont = self._box_iou_and_containment(box, k_box)
                if iou >= 0.45 or (cid == k_cid and cont >= 0.72):
                    keep = False
                    break
            if keep:
                final_boxes.append((cid, conf, box))

        return final_boxes

    def detect_raw(
        self,
        img_bgr: np.ndarray,
        conf_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None,
    ) -> List[Tuple[int, float, Tuple[float, float, float, float]]]:
        """
        Runs object detection (including Dual-Model Specialist WBF Ensemble if enabled)
        and returns raw (class_id, confidence, (x1, y1, x2, y2)) detections.
        """
        conf_t = conf_threshold if conf_threshold is not None else self.conf_threshold
        iou_t = iou_threshold if iou_threshold is not None else self.iou_threshold
        orig_h, orig_w = img_bgr.shape[:2]

        if self.backend == "onnx":
            inp_tensor, ratio, pad = self._preprocess_onnx(img_bgr)
            out_global = self.session.run([self.output_name], {self.input_name: inp_tensor})[0]
            det_global = self._postprocess_onnx(
                out_global, (orig_h, orig_w), ratio, pad, conf_t, iou_t
            )
            if self.use_ensemble and self.specialist_session is not None:
                spec_conf = max(0.20, conf_t * 0.85)
                out_spec = self.specialist_session.run(
                    [self.spec_output_name], {self.spec_input_name: inp_tensor}
                )[0]
                det_spec = self._postprocess_onnx(
                    out_spec, (orig_h, orig_w), ratio, pad, spec_conf, iou_t
                )
                detections = self._fuse_ensemble_detections(det_global, det_spec, conf_t)
            else:
                detections = det_global

            if self.filter_road_surface:
                detections = self.road_filter.filter_detections(detections, img_bgr)
            return self._keep_potholes(detections, conf_t)

        elif self.backend == "pytorch":
            results = self.model.predict(
                img_bgr, conf=conf_t, iou=iou_t, imgsz=self.img_size, verbose=False
            )[0]
            det_global = []
            global_is_single_class = len(results.names) == 1
            for box in results.boxes:
                cid = 3 if global_is_single_class else int(box.cls[0])
                score = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                det_global.append((cid, score, (x1, y1, x2, y2)))

            if self.use_ensemble and self.specialist_model is not None:
                spec_conf = max(0.20, conf_t * 0.85)
                res_spec = self.specialist_model.predict(
                    img_bgr, conf=spec_conf, iou=iou_t, imgsz=self.img_size, verbose=False
                )[0]
                det_spec = []
                specialist_is_single_class = len(res_spec.names) == 1
                for box in res_spec.boxes:
                    cid = 3 if specialist_is_single_class else int(box.cls[0])
                    score = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    det_spec.append((cid, score, (x1, y1, x2, y2)))
                detections = self._fuse_ensemble_detections(det_global, det_spec, conf_t)
            else:
                detections = det_global

            if self.filter_road_surface:
                detections = self.road_filter.filter_detections(detections, img_bgr)
            return self._keep_potholes(detections, conf_t)

        return []

    def _keep_potholes(
        self,
        detections: List[Tuple[int, float, Tuple[float, float, float, float]]],
        requested_threshold: float,
    ) -> List[Tuple[int, float, Tuple[float, float, float, float]]]:
        """Apply the precision-first pothole-only product policy."""
        if not self.pothole_only:
            return detections

        # Respect the caller's requested threshold (or instance default)
        confirmation_threshold = requested_threshold
        return [
            detection
            for detection in detections
            if detection[0] == 3 and detection[1] >= confirmation_threshold
        ]

    def predict(
        self,
        image_input: Union[str, np.ndarray, Image.Image],
        conf_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None,
    ) -> RoadDamageReport:
        """
        Executes end-to-end detection, localization, classification, and severity estimation.

        Args:
            image_input: File path, numpy BGR array, or PIL Image.
            conf_threshold: Override confidence threshold.
            iou_threshold: Override NMS IoU threshold.

        Returns:
            RoadDamageReport with complete detections, severity rankings, and health summary.
        """
        conf_t = conf_threshold if conf_threshold is not None else self.conf_threshold
        iou_t = iou_threshold if iou_threshold is not None else self.iou_threshold

        source_info = ""
        if isinstance(image_input, str):
            source_info = image_input
            img_bgr = cv2.imread(image_input)
            if img_bgr is None:
                raise ValueError(f"Failed to read image from path: {image_input}")
        elif isinstance(image_input, Image.Image):
            source_info = "PIL Image"
            img_rgb = np.array(image_input)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            source_info = "NumPy Array"
            img_bgr = image_input.copy()
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

        orig_h, orig_w = img_bgr.shape[:2]
        t_start = time.perf_counter()

        raw_detections = self.detect_raw(img_bgr, conf_threshold=conf_t, iou_threshold=iou_t)

        t_end = time.perf_counter()
        inference_ms = (t_end - t_start) * 1000.0

        # Construct structured detections with ASTM severity assessment
        detections: List[Detection] = []
        summary_tuples: List[Tuple[str, str]] = []

        for det_idx, (cid, score, (x1, y1, x2, y2)) in enumerate(raw_detections, start=1):
            class_name = DEFECT_CLASSES.get(cid, "Pothole")

            # Assess severity using bounding box geometry and local pixel texture
            severity = self.severity_estimator.estimate(
                class_name=class_name,
                bbox=(x1, y1, x2, y2),
                img_shape=(orig_h, orig_w),
                confidence=score,
                image_bgr=img_bgr,
            )

            norm_box = (
                round(x1 / orig_w, 4),
                round(y1 / orig_h, 4),
                round(x2 / orig_w, 4),
                round(y2 / orig_h, 4),
            )

            det = Detection(
                id=det_idx,
                class_id=cid,
                class_name=class_name,
                confidence=round(score, 3),
                bbox=(round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)),
                bbox_normalized=norm_box,
                severity=severity,
            )
            detections.append(det)
            summary_tuples.append((class_name, severity.level))

        # Sort detections: Highest severity first (High -> Medium -> Low), then confidence
        sev_rank = {"High": 0, "Medium": 1, "Low": 2}
        detections.sort(key=lambda d: (sev_rank.get(d.severity.level, 3), -d.confidence))
        # Re-index
        for idx, d in enumerate(detections, start=1):
            d.id = idx

        # Overall Pavement Health Index
        summary = self.severity_estimator.compute_road_health(summary_tuples)

        ensemble_tag = "Dual-Model WBF Ensemble, CPU-optimized" if self.use_ensemble else "CPU-optimized"
        return RoadDamageReport(
            image_shape=(orig_h, orig_w),
            detections=detections,
            summary=summary,
            inference_time_ms=round(inference_ms, 2),
            backend_used=f"{self.backend.upper()} ({ensemble_tag})",
            source_info=source_info,
        )
