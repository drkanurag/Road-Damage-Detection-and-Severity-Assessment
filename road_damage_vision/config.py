"""
Configuration parameters, defect category definitions, ASTM D6433 standards,
and severity styling constants for Road Damage Detection.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

# Standard Road Damage Dataset (RDD2020 / RDD2022 / GRDDC) defect classes
# D00: Longitudinal crack
# D10: Transverse crack
# D20: Alligator crack
# D40: Pothole
DEFECT_CLASSES: Dict[int, str] = {
    0: "Longitudinal crack",
    1: "Transverse crack",
    2: "Alligator crack",
    3: "Pothole"
}

# Alias mapping for flexible input
CLASS_ALIASES: Dict[str, str] = {
    "longitudinal_crack": "Longitudinal crack",
    "transverse_crack": "Transverse crack",
    "alligator_crack": "Alligator crack",
    "pothole": "Pothole",
    "d00": "Longitudinal crack",
    "d10": "Transverse crack",
    "d20": "Alligator crack",
    "d40": "Pothole",
}

# Severity Levels
SEVERITY_LOW = "Low"
SEVERITY_MEDIUM = "Medium"
SEVERITY_HIGH = "High"

SEVERITY_LEVELS = [SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH]

# Color palettes (BGR format for OpenCV, Hex for Web/Streamlit)
SEVERITY_COLORS_BGR: Dict[str, Tuple[int, int, int]] = {
    SEVERITY_LOW: (94, 197, 34),       # Modern Soft Green (#22c55e)
    SEVERITY_MEDIUM: (11, 158, 245),    # Vibrant Amber/Orange (#f59e0b)
    SEVERITY_HIGH: (68, 68, 239)        # Urgent Crimson/Red (#ef4444)
}

SEVERITY_COLORS_HEX: Dict[str, str] = {
    SEVERITY_LOW: "#22c55e",
    SEVERITY_MEDIUM: "#f59e0b",
    SEVERITY_HIGH: "#ef4444"
}

# Road Health Status Thresholds (based on Pavement Condition Index 0 - 100)
ROAD_STATUS_GOOD = "Good"
ROAD_STATUS_FAIR = "Fair"
ROAD_STATUS_POOR = "Poor"
ROAD_STATUS_CRITICAL = "Critical"

# Deduct points per defect for Road Health Score (0 - 100)
DEDUCT_POINTS: Dict[str, Dict[str, float]] = {
    "Pothole": {
        SEVERITY_LOW: 7.0,
        SEVERITY_MEDIUM: 16.0,
        SEVERITY_HIGH: 28.0
    },
    "Alligator crack": {
        SEVERITY_LOW: 6.0,
        SEVERITY_MEDIUM: 14.0,
        SEVERITY_HIGH: 24.0
    },
    "Longitudinal crack": {
        SEVERITY_LOW: 3.0,
        SEVERITY_MEDIUM: 7.0,
        SEVERITY_HIGH: 14.0
    },
    "Transverse crack": {
        SEVERITY_LOW: 4.0,
        SEVERITY_MEDIUM: 8.0,
        SEVERITY_HIGH: 16.0
    }
}

# Recommended Maintenance Action Guidance
MAINTENANCE_ACTIONS: Dict[str, Dict[str, str]] = {
    "Pothole": {
        SEVERITY_LOW: "Surface patch / cold mix during regular maintenance cycle.",
        SEVERITY_MEDIUM: "Hot asphalt fill and compaction within 14 days to prevent rim expansion.",
        SEVERITY_HIGH: "EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
    },
    "Alligator crack": {
        SEVERITY_LOW: "Seal surface with fog seal / slurry seal to inhibit water penetration.",
        SEVERITY_MEDIUM: "Apply crack sealing mastic and microsurfacing within 30 days.",
        SEVERITY_HIGH: "CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
    },
    "Longitudinal crack": {
        SEVERITY_LOW: "Monitor during next routine survey; verify joint integrity.",
        SEVERITY_MEDIUM: "Clean and route crack, fill with rubberized asphalt crack sealant.",
        SEVERITY_HIGH: "Deep rout, structural seal, and investigate potential pavement base settlement."
    },
    "Transverse crack": {
        SEVERITY_LOW: "Monitor for thermal contraction widening during temperature shifts.",
        SEVERITY_MEDIUM: "Rout and seal with hot-pour elastomeric sealant.",
        SEVERITY_HIGH: "Severe thermal cracking with spalling; mill edge boundaries and apply asphalt patch."
    }
}

DEFAULT_ONNX_MODEL_PATH = "models/rdd2022_yolov8n.onnx"
DEFAULT_PT_MODEL_PATH = "models/rdd2022_yolov8n.pt"
SPECIALIST_ONNX_MODEL_PATH = "models/rdd2022_india_trained.onnx"
SPECIALIST_PT_MODEL_PATH = "models/rdd2022_india_trained.pt"
DEFAULT_IMG_SIZE = 640
# Balanced sensitivity: captures genuine road distress while RoadSurfaceFilter eliminates out-of-road noise
DEFAULT_CONF_THRESHOLD = 0.18
DEFAULT_IOU_THRESHOLD = 0.45
DEFAULT_ORT_THREADS = 6

