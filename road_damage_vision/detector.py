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
    DEFAULT_PT_MODEL_PATH,
    DEFECT_CLASSES,
)
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
    
    Defaults to ONNX Runtime for ultra-fast, dependency-free execution on edge devices
    and standard CPUs without requiring large GPU frameworks.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        backend: str = "onnx",
        img_size: int = DEFAULT_IMG_SIZE,
        conf_threshold: float = DEFAULT_CONF_THRESHOLD,
        iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    ):
        """
        Args:
            model_path: Path to .onnx or .pt model file. If None, uses default.
            backend: 'onnx' (recommended for CPU) or 'pytorch'.
            img_size: Input resolution (default 640).
            conf_threshold: Minimum detection confidence (0.0 to 1.0).
            iou_threshold: IoU overlap threshold for Non-Maximum Suppression.
        """
        self.backend = backend.lower()
        self.img_size = img_size
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.severity_estimator = SeverityEstimator()

        if model_path is None:
            if self.backend == "onnx":
                model_path = DEFAULT_ONNX_MODEL_PATH
            else:
                model_path = DEFAULT_PT_MODEL_PATH

        self.model_path = model_path
        self._init_backend()

    def _init_backend(self) -> None:
        """Loads model into memory using the selected engine."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model file not found at: {self.model_path}. "
                "Ensure models/rdd2022_yolov8n.onnx or .pt exists."
            )

        if self.backend == "onnx":
            import onnxruntime as ort

            # Prefer CPUExecutionProvider for lightweight edge/desktop deployment
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.intra_op_num_threads = max(1, os.cpu_count() or 4)

            self.session = ort.InferenceSession(
                self.model_path,
                sess_options=sess_options,
                providers=["CPUExecutionProvider"],
            )
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            self.model = None

        elif self.backend == "pytorch":
            from ultralytics import YOLO

            self.model = YOLO(self.model_path)
            self.session = None

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

        raw_detections: List[Tuple[int, float, Tuple[float, float, float, float]]] = []

        if self.backend == "onnx":
            inp_tensor, ratio, pad = self._preprocess_onnx(img_bgr)
            out_tensor = self.session.run([self.output_name], {self.input_name: inp_tensor})[0]
            raw_detections = self._postprocess_onnx(
                out_tensor, (orig_h, orig_w), ratio, pad, conf_t, iou_t
            )

        elif self.backend == "pytorch":
            results = self.model.predict(
                img_bgr, conf=conf_t, iou=iou_t, imgsz=self.img_size, verbose=False
            )[0]
            for box in results.boxes:
                cid = int(box.cls[0])
                score = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                raw_detections.append((cid, score, (x1, y1, x2, y2)))

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

        return RoadDamageReport(
            image_shape=(orig_h, orig_w),
            detections=detections,
            summary=summary,
            inference_time_ms=round(inference_ms, 2),
            backend_used=f"{self.backend.upper()} (CPU-optimized)",
            source_info=source_info,
        )
