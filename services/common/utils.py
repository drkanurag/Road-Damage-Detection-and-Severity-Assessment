"""
Image encoding/decoding utilities shared across microservices for stateless payload transport.
"""

import base64
import cv2
import numpy as np


def encode_bgr_to_base64(img_bgr: np.ndarray, quality: int = 90, include_prefix: bool = False) -> str:
    """Encodes a BGR numpy image into a JPEG base64 string."""
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, buffer = cv2.imencode(".jpg", img_bgr, encode_params)
    if not success:
        raise ValueError("Failed to encode BGR image to JPEG.")
    b64 = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}" if include_prefix else b64


def decode_base64_to_bgr(b64_str: str) -> np.ndarray:
    """Decodes a base64 string (with or without data URI prefix) into a BGR numpy image."""
    if "," in b64_str and b64_str.startswith("data:"):
        b64_str = b64_str.split(",", 1)[1]
    raw_bytes = base64.b64decode(b64_str)
    nparr = np.frombuffer(raw_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise ValueError("Failed to decode base64 string into a valid BGR image.")
    return img_bgr
