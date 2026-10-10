// Auto-generated YOLOv8 WBF Ensemble & ASTM D6433 Telemetry for Serverless / Instant Browser Mode
window.PRECOMPUTED_TELEMETRY = {
  "india_pothole_cracks": {
    "sample_meta": {
      "id": "india_pothole_cracks",
      "title": "Roadway Pothole & Alligator Distress (Your Photo)",
      "category": "Pothole & Alligator",
      "description": "Complex Indian road distress with localized potholes and base fatigue.",
      "filename": "india_pothole_cracks.jpg"
    },
    "metadata": {
      "image_width": 720,
      "image_height": 720,
      "inference_time_ms": 69.52,
      "backend": "ONNX (Dual-Model WBF Ensemble, CPU-optimized)",
      "source": "india_pothole_cracks.jpg"
    },
    "summary": {
      "health_score": 48.0,
      "status": "Poor",
      "total_defects": 2,
      "critical_defects_count": 2,
      "severity_counts": {
        "Low": 0,
        "Medium": 0,
        "High": 2
      },
      "class_counts": {
        "Pothole": 1,
        "Alligator crack": 1
      },
      "estimated_maintenance_urgency": "Corrective Repair Needed (within 30 days)",
      "action_items": [
        "[Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage.",
        "[Alligator crack - High]: CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
      ]
    },
    "defects": [
      {
        "id": 1,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.454,
        "bbox": {
          "x1": 514.5,
          "y1": 526.3,
          "x2": 669.9,
          "y2": 667.5,
          "width": 155.4,
          "height": 141.2
        },
        "bbox_normalized": {
          "x1": 0.7146,
          "y1": 0.731,
          "x2": 0.9304,
          "y2": 0.9271
        },
        "severity": {
          "level": "High",
          "score": 0.729,
          "color_hex": "#ef4444",
          "area_pixels": 21932,
          "area_pct": 4.231,
          "aspect_ratio": 1.1,
          "extent_norm": 0.216,
          "edge_density": 0.001,
          "contrast_delta": 7.0,
          "rationale": "Severe deep pothole (4.23% area, extent=0.22, contrast=7.0). Acute hazard to vehicle rims and suspension.",
          "recommended_action": "EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
        }
      },
      {
        "id": 2,
        "class_id": 2,
        "class_name": "Alligator crack",
        "confidence": 0.409,
        "bbox": {
          "x1": 148.4,
          "y1": 498.4,
          "x2": 435.2,
          "y2": 685.4,
          "width": 286.8,
          "height": 187.0
        },
        "bbox_normalized": {
          "x1": 0.2061,
          "y1": 0.6922,
          "x2": 0.6045,
          "y2": 0.9519
        },
        "severity": {
          "level": "High",
          "score": 0.6,
          "color_hex": "#ef4444",
          "area_pixels": 53627,
          "area_pct": 10.345,
          "aspect_ratio": 1.53,
          "extent_norm": 0.398,
          "edge_density": 0.002,
          "contrast_delta": 12.0,
          "rationale": "Severe alligator fatigue (10.34% area, edge density=0.00). Heavily spalled, loose polygonal block network with base pavement degradation.",
          "recommended_action": "CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
        }
      }
    ],
    "markdown_summary": "# Road Pavement Distress & Severity Assessment Report\n\n- **Inspection Source**: `samples\\india_pothole_cracks.jpg`\n- **Pavement Condition Index (PCI)**: **48.0 / 100** (Poor)\n- **Total Defects Detected**: 2\n- **Critical Severity Defects**: 2\n- **Inference Speed**: 69.5 ms via ONNX (Dual-Model WBF Ensemble, CPU-optimized)\n- **Maintenance Urgency**: Corrective Repair Needed (within 30 days)\n\n### Severity Breakdown\n- [HIGH] High Severity: 2\n- [MED]  Medium Severity: 0\n- [LOW]  Low Severity: 0\n\n### Detected Defects Log\n| ID | Class | Severity | Conf | Area % | Action Required |\n|---|---|---|---|---|---|\n| #1 | **Pothole** | `High` (0.73) | 45% | 4.23% | EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage. |\n| #2 | **Alligator crack** | `High` (0.60) | 41% | 10.35% | CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay. |\n\n### Recommended Action Items\n- [Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage.\n- [Alligator crack - High]: CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
  },
  "india_barricade_potholes": {
    "sample_meta": {
      "id": "india_barricade_potholes",
      "title": "Barricade Road Cavities (Your Photo)",
      "category": "Potholes (D40)",
      "description": "Fine-tuned detection of subtle pothole depressions along corridor.",
      "filename": "india_barricade_potholes.jpg"
    },
    "metadata": {
      "image_width": 720,
      "image_height": 720,
      "inference_time_ms": 64.07,
      "backend": "ONNX (Dual-Model WBF Ensemble, CPU-optimized)",
      "source": "india_barricade_potholes.jpg"
    },
    "summary": {
      "health_score": 21.0,
      "status": "Critical",
      "total_defects": 4,
      "critical_defects_count": 2,
      "severity_counts": {
        "Low": 1,
        "Medium": 1,
        "High": 2
      },
      "class_counts": {
        "Pothole": 4
      },
      "estimated_maintenance_urgency": "URGENT INTERVENTION: High hazard risk to traffic",
      "action_items": [
        "[Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
      ]
    },
    "defects": [
      {
        "id": 1,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.347,
        "bbox": {
          "x1": 524.3,
          "y1": 479.3,
          "x2": 720.0,
          "y2": 605.7,
          "width": 195.7,
          "height": 126.4
        },
        "bbox_normalized": {
          "x1": 0.7282,
          "y1": 0.6656,
          "x2": 1.0,
          "y2": 0.8413
        },
        "severity": {
          "level": "High",
          "score": 0.727,
          "color_hex": "#ef4444",
          "area_pixels": 24753,
          "area_pct": 4.775,
          "aspect_ratio": 1.55,
          "extent_norm": 0.272,
          "edge_density": 0.052,
          "contrast_delta": 0.0,
          "rationale": "Severe deep pothole (4.77% area, extent=0.27, contrast=0.0). Acute hazard to vehicle rims and suspension.",
          "recommended_action": "EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
        }
      },
      {
        "id": 2,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.329,
        "bbox": {
          "x1": 413.9,
          "y1": 485.5,
          "x2": 545.6,
          "y2": 585.7,
          "width": 131.7,
          "height": 100.2
        },
        "bbox_normalized": {
          "x1": 0.5748,
          "y1": 0.6744,
          "x2": 0.7577,
          "y2": 0.8135
        },
        "severity": {
          "level": "High",
          "score": 0.652,
          "color_hex": "#ef4444",
          "area_pixels": 13188,
          "area_pct": 2.544,
          "aspect_ratio": 1.31,
          "extent_norm": 0.183,
          "edge_density": 0.031,
          "contrast_delta": 0.0,
          "rationale": "Severe deep pothole (2.54% area, extent=0.18, contrast=0.0). Acute hazard to vehicle rims and suspension.",
          "recommended_action": "EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
        }
      },
      {
        "id": 3,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.272,
        "bbox": {
          "x1": 332.8,
          "y1": 541.3,
          "x2": 389.3,
          "y2": 601.8,
          "width": 56.5,
          "height": 60.5
        },
        "bbox_normalized": {
          "x1": 0.4622,
          "y1": 0.7518,
          "x2": 0.5407,
          "y2": 0.8359
        },
        "severity": {
          "level": "Medium",
          "score": 0.227,
          "color_hex": "#f59e0b",
          "area_pixels": 3425,
          "area_pct": 0.661,
          "aspect_ratio": 1.07,
          "extent_norm": 0.084,
          "edge_density": 0.053,
          "contrast_delta": 0.0,
          "rationale": "Moderate pothole (0.66% area, extent=0.08). Noticeable jolt; requires scheduled patch before pothole perimeter expands.",
          "recommended_action": "Hot asphalt fill and compaction within 14 days to prevent rim expansion."
        }
      },
      {
        "id": 4,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.321,
        "bbox": {
          "x1": 201.6,
          "y1": 407.7,
          "x2": 248.1,
          "y2": 433.6,
          "width": 46.5,
          "height": 25.9
        },
        "bbox_normalized": {
          "x1": 0.28,
          "y1": 0.5663,
          "x2": 0.3446,
          "y2": 0.6022
        },
        "severity": {
          "level": "Low",
          "score": 0.113,
          "color_hex": "#22c55e",
          "area_pixels": 1202,
          "area_pct": 0.232,
          "aspect_ratio": 1.8,
          "extent_norm": 0.065,
          "edge_density": 0.024,
          "contrast_delta": 0.0,
          "rationale": "Small shallow pothole (0.24% area, extent=0.07). Low risk to vehicles; minor ride quality disturbance.",
          "recommended_action": "Surface patch / cold mix during regular maintenance cycle."
        }
      }
    ],
    "markdown_summary": "# Road Pavement Distress & Severity Assessment Report\n\n- **Inspection Source**: `samples\\india_barricade_potholes.jpg`\n- **Pavement Condition Index (PCI)**: **21.0 / 100** (Critical)\n- **Total Defects Detected**: 4\n- **Critical Severity Defects**: 2\n- **Inference Speed**: 64.1 ms via ONNX (Dual-Model WBF Ensemble, CPU-optimized)\n- **Maintenance Urgency**: URGENT INTERVENTION: High hazard risk to traffic\n\n### Severity Breakdown\n- [HIGH] High Severity: 2\n- [MED]  Medium Severity: 1\n- [LOW]  Low Severity: 1\n\n### Detected Defects Log\n| ID | Class | Severity | Conf | Area % | Action Required |\n|---|---|---|---|---|---|\n| #1 | **Pothole** | `High` (0.73) | 35% | 4.78% | EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage. |\n| #2 | **Pothole** | `High` (0.65) | 33% | 2.54% | EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage. |\n| #3 | **Pothole** | `Medium` (0.23) | 27% | 0.66% | Hot asphalt fill and compaction within 14 days to prevent rim expansion. |\n| #4 | **Pothole** | `Low` (0.11) | 32% | 0.23% | Surface patch / cold mix during regular maintenance cycle. |\n\n### Recommended Action Items\n- [Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
  },
  "india_highway_distress": {
    "sample_meta": {
      "id": "india_highway_distress",
      "title": "Highway Mid-Lane Pothole Cluster (Your Photo)",
      "category": "Potholes & Fatigue",
      "description": "Accurately localized multiple pothole cavities across traffic lane.",
      "filename": "india_highway_distress.jpg"
    },
    "metadata": {
      "image_width": 720,
      "image_height": 720,
      "inference_time_ms": 66.44,
      "backend": "ONNX (Dual-Model WBF Ensemble, CPU-optimized)",
      "source": "india_highway_distress.jpg"
    },
    "summary": {
      "health_score": 31.0,
      "status": "Critical",
      "total_defects": 5,
      "critical_defects_count": 0,
      "severity_counts": {
        "Low": 1,
        "Medium": 4,
        "High": 0
      },
      "class_counts": {
        "Pothole": 4,
        "Alligator crack": 1
      },
      "estimated_maintenance_urgency": "URGENT INTERVENTION: High hazard risk to traffic",
      "action_items": [
        "[Pothole - Medium]: Hot asphalt fill and compaction within 14 days to prevent rim expansion.",
        "[Alligator crack - Medium]: Apply crack sealing mastic and microsurfacing within 30 days."
      ]
    },
    "defects": [
      {
        "id": 1,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.529,
        "bbox": {
          "x1": 622.3,
          "y1": 432.1,
          "x2": 671.6,
          "y2": 481.5,
          "width": 49.3,
          "height": 49.4
        },
        "bbox_normalized": {
          "x1": 0.8643,
          "y1": 0.6002,
          "x2": 0.9328,
          "y2": 0.6688
        },
        "severity": {
          "level": "Medium",
          "score": 0.191,
          "color_hex": "#f59e0b",
          "area_pixels": 2432,
          "area_pct": 0.469,
          "aspect_ratio": 1.0,
          "extent_norm": 0.069,
          "edge_density": 0.022,
          "contrast_delta": 2.5,
          "rationale": "Moderate pothole (0.48% area, extent=0.07). Noticeable jolt; requires scheduled patch before pothole perimeter expands.",
          "recommended_action": "Hot asphalt fill and compaction within 14 days to prevent rim expansion."
        }
      },
      {
        "id": 2,
        "class_id": 2,
        "class_name": "Alligator crack",
        "confidence": 0.436,
        "bbox": {
          "x1": 427.3,
          "y1": 492.1,
          "x2": 531.1,
          "y2": 596.2,
          "width": 103.8,
          "height": 104.1
        },
        "bbox_normalized": {
          "x1": 0.5935,
          "y1": 0.6835,
          "x2": 0.7377,
          "y2": 0.828
        },
        "severity": {
          "level": "Medium",
          "score": 0.488,
          "color_hex": "#f59e0b",
          "area_pixels": 10799,
          "area_pct": 2.083,
          "aspect_ratio": 1.0,
          "extent_norm": 0.145,
          "edge_density": 0.129,
          "contrast_delta": 3.4,
          "rationale": "Developing alligator pattern (2.08% area, edge density=0.13). Well-defined interconnected chicken-wire pattern with minor edge spalling.",
          "recommended_action": "Apply crack sealing mastic and microsurfacing within 30 days."
        }
      },
      {
        "id": 3,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.313,
        "bbox": {
          "x1": 509.7,
          "y1": 478.6,
          "x2": 582.2,
          "y2": 512.2,
          "width": 72.5,
          "height": 33.6
        },
        "bbox_normalized": {
          "x1": 0.708,
          "y1": 0.6647,
          "x2": 0.8086,
          "y2": 0.7113
        },
        "severity": {
          "level": "Medium",
          "score": 0.224,
          "color_hex": "#f59e0b",
          "area_pixels": 2430,
          "area_pct": 0.469,
          "aspect_ratio": 2.16,
          "extent_norm": 0.101,
          "edge_density": 0.088,
          "contrast_delta": 3.7,
          "rationale": "Moderate pothole (0.47% area, extent=0.10). Noticeable jolt; requires scheduled patch before pothole perimeter expands.",
          "recommended_action": "Hot asphalt fill and compaction within 14 days to prevent rim expansion."
        }
      },
      {
        "id": 4,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.285,
        "bbox": {
          "x1": 278.5,
          "y1": 413.8,
          "x2": 386.0,
          "y2": 453.3,
          "width": 107.5,
          "height": 39.5
        },
        "bbox_normalized": {
          "x1": 0.3869,
          "y1": 0.5748,
          "x2": 0.5361,
          "y2": 0.6296
        },
        "severity": {
          "level": "Medium",
          "score": 0.41,
          "color_hex": "#f59e0b",
          "area_pixels": 4241,
          "area_pct": 0.818,
          "aspect_ratio": 2.72,
          "extent_norm": 0.149,
          "edge_density": 0.001,
          "contrast_delta": 11.1,
          "rationale": "Moderate pothole (0.85% area, extent=0.15). Noticeable jolt; requires scheduled patch before pothole perimeter expands.",
          "recommended_action": "Hot asphalt fill and compaction within 14 days to prevent rim expansion."
        }
      },
      {
        "id": 5,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.296,
        "bbox": {
          "x1": 305.2,
          "y1": 479.7,
          "x2": 350.7,
          "y2": 507.8,
          "width": 45.5,
          "height": 28.1
        },
        "bbox_normalized": {
          "x1": 0.424,
          "y1": 0.6662,
          "x2": 0.487,
          "y2": 0.7053
        },
        "severity": {
          "level": "Low",
          "score": 0.136,
          "color_hex": "#22c55e",
          "area_pixels": 1277,
          "area_pct": 0.246,
          "aspect_ratio": 1.61,
          "extent_norm": 0.063,
          "edge_density": 0.027,
          "contrast_delta": 3.3,
          "rationale": "Small shallow pothole (0.25% area, extent=0.06). Low risk to vehicles; minor ride quality disturbance.",
          "recommended_action": "Surface patch / cold mix during regular maintenance cycle."
        }
      }
    ],
    "markdown_summary": "# Road Pavement Distress & Severity Assessment Report\n\n- **Inspection Source**: `samples\\india_highway_distress.jpg`\n- **Pavement Condition Index (PCI)**: **31.0 / 100** (Critical)\n- **Total Defects Detected**: 5\n- **Critical Severity Defects**: 0\n- **Inference Speed**: 66.4 ms via ONNX (Dual-Model WBF Ensemble, CPU-optimized)\n- **Maintenance Urgency**: URGENT INTERVENTION: High hazard risk to traffic\n\n### Severity Breakdown\n- [HIGH] High Severity: 0\n- [MED]  Medium Severity: 4\n- [LOW]  Low Severity: 1\n\n### Detected Defects Log\n| ID | Class | Severity | Conf | Area % | Action Required |\n|---|---|---|---|---|---|\n| #1 | **Pothole** | `Medium` (0.19) | 53% | 0.47% | Hot asphalt fill and compaction within 14 days to prevent rim expansion. |\n| #2 | **Alligator crack** | `Medium` (0.49) | 44% | 2.08% | Apply crack sealing mastic and microsurfacing within 30 days. |\n| #3 | **Pothole** | `Medium` (0.22) | 31% | 0.47% | Hot asphalt fill and compaction within 14 days to prevent rim expansion. |\n| #4 | **Pothole** | `Medium` (0.41) | 28% | 0.82% | Hot asphalt fill and compaction within 14 days to prevent rim expansion. |\n| #5 | **Pothole** | `Low` (0.14) | 30% | 0.25% | Surface patch / cold mix during regular maintenance cycle. |\n\n### Recommended Action Items\n- [Pothole - Medium]: Hot asphalt fill and compaction within 14 days to prevent rim expansion.\n- [Alligator crack - Medium]: Apply crack sealing mastic and microsurfacing within 30 days."
  },
  "india_corridor_worn_road": {
    "sample_meta": {
      "id": "india_corridor_worn_road",
      "title": "Suburban Corridor Pothole Field (Your Photo)",
      "category": "Multiple Potholes",
      "description": "Severe road deterioration with foreground and midground pothole depressions.",
      "filename": "india_corridor_worn_road.jpg"
    },
    "metadata": {
      "image_width": 720,
      "image_height": 720,
      "inference_time_ms": 55.63,
      "backend": "ONNX (Dual-Model WBF Ensemble, CPU-optimized)",
      "source": "india_corridor_worn_road.jpg"
    },
    "summary": {
      "health_score": 33.0,
      "status": "Critical",
      "total_defects": 4,
      "critical_defects_count": 1,
      "severity_counts": {
        "Low": 1,
        "Medium": 2,
        "High": 1
      },
      "class_counts": {
        "Pothole": 4
      },
      "estimated_maintenance_urgency": "URGENT INTERVENTION: High hazard risk to traffic",
      "action_items": [
        "[Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
      ]
    },
    "defects": [
      {
        "id": 1,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.315,
        "bbox": {
          "x1": 433.9,
          "y1": 254.6,
          "x2": 630.5,
          "y2": 392.3,
          "width": 196.6,
          "height": 137.7
        },
        "bbox_normalized": {
          "x1": 0.6026,
          "y1": 0.3536,
          "x2": 0.8756,
          "y2": 0.5449
        },
        "severity": {
          "level": "High",
          "score": 0.743,
          "color_hex": "#ef4444",
          "area_pixels": 27075,
          "area_pct": 5.223,
          "aspect_ratio": 1.43,
          "extent_norm": 0.273,
          "edge_density": 0.062,
          "contrast_delta": 0.0,
          "rationale": "Severe deep pothole (5.69% area, extent=0.29, contrast=0.0). Acute hazard to vehicle rims and suspension.",
          "recommended_action": "EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
        }
      },
      {
        "id": 2,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.38,
        "bbox": {
          "x1": 360.0,
          "y1": 252.1,
          "x2": 428.6,
          "y2": 296.8,
          "width": 68.6,
          "height": 44.7
        },
        "bbox_normalized": {
          "x1": 0.5,
          "y1": 0.3502,
          "x2": 0.5952,
          "y2": 0.4122
        },
        "severity": {
          "level": "Medium",
          "score": 0.251,
          "color_hex": "#f59e0b",
          "area_pixels": 3063,
          "area_pct": 0.591,
          "aspect_ratio": 1.54,
          "extent_norm": 0.095,
          "edge_density": 0.057,
          "contrast_delta": 1.2,
          "rationale": "Moderate pothole (0.66% area, extent=0.10). Noticeable jolt; requires scheduled patch before pothole perimeter expands.",
          "recommended_action": "Hot asphalt fill and compaction within 14 days to prevent rim expansion."
        }
      },
      {
        "id": 3,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.295,
        "bbox": {
          "x1": 252.7,
          "y1": 235.7,
          "x2": 345.4,
          "y2": 270.1,
          "width": 92.7,
          "height": 34.4
        },
        "bbox_normalized": {
          "x1": 0.351,
          "y1": 0.3274,
          "x2": 0.4797,
          "y2": 0.3752
        },
        "severity": {
          "level": "Medium",
          "score": 0.297,
          "color_hex": "#f59e0b",
          "area_pixels": 3189,
          "area_pct": 0.615,
          "aspect_ratio": 2.69,
          "extent_norm": 0.129,
          "edge_density": 0.01,
          "contrast_delta": 2.1,
          "rationale": "Moderate pothole (0.69% area, extent=0.14). Noticeable jolt; requires scheduled patch before pothole perimeter expands.",
          "recommended_action": "Hot asphalt fill and compaction within 14 days to prevent rim expansion."
        }
      },
      {
        "id": 4,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.266,
        "bbox": {
          "x1": 398.2,
          "y1": 224.8,
          "x2": 441.6,
          "y2": 249.2,
          "width": 43.4,
          "height": 24.4
        },
        "bbox_normalized": {
          "x1": 0.553,
          "y1": 0.3122,
          "x2": 0.6133,
          "y2": 0.3461
        },
        "severity": {
          "level": "Low",
          "score": 0.14,
          "color_hex": "#22c55e",
          "area_pixels": 1059,
          "area_pct": 0.204,
          "aspect_ratio": 1.78,
          "extent_norm": 0.06,
          "edge_density": 0.014,
          "contrast_delta": 4.2,
          "rationale": "Small shallow pothole (0.23% area, extent=0.07). Low risk to vehicles; minor ride quality disturbance.",
          "recommended_action": "Surface patch / cold mix during regular maintenance cycle."
        }
      }
    ],
    "markdown_summary": "# Road Pavement Distress & Severity Assessment Report\n\n- **Inspection Source**: `samples\\india_corridor_worn_road.jpg`\n- **Pavement Condition Index (PCI)**: **33.0 / 100** (Critical)\n- **Total Defects Detected**: 4\n- **Critical Severity Defects**: 1\n- **Inference Speed**: 55.6 ms via ONNX (Dual-Model WBF Ensemble, CPU-optimized)\n- **Maintenance Urgency**: URGENT INTERVENTION: High hazard risk to traffic\n\n### Severity Breakdown\n- [HIGH] High Severity: 1\n- [MED]  Medium Severity: 2\n- [LOW]  Low Severity: 1\n\n### Detected Defects Log\n| ID | Class | Severity | Conf | Area % | Action Required |\n|---|---|---|---|---|---|\n| #1 | **Pothole** | `High` (0.74) | 32% | 5.22% | EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage. |\n| #2 | **Pothole** | `Medium` (0.25) | 38% | 0.59% | Hot asphalt fill and compaction within 14 days to prevent rim expansion. |\n| #3 | **Pothole** | `Medium` (0.30) | 30% | 0.61% | Hot asphalt fill and compaction within 14 days to prevent rim expansion. |\n| #4 | **Pothole** | `Low` (0.14) | 27% | 0.20% | Surface patch / cold mix during regular maintenance cycle. |\n\n### Recommended Action Items\n- [Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
  },
  "pothole_sample": {
    "sample_meta": {
      "id": "pothole_sample",
      "title": "Severe Potholes & Transverse Fracture",
      "category": "Pothole & Transverse",
      "description": "Depression cavities with sharp edges and thermal cracking.",
      "filename": "pothole_sample.jpg"
    },
    "metadata": {
      "image_width": 570,
      "image_height": 570,
      "inference_time_ms": 56.61,
      "backend": "ONNX (Dual-Model WBF Ensemble, CPU-optimized)",
      "source": "pothole_sample.jpg"
    },
    "summary": {
      "health_score": 21.0,
      "status": "Critical",
      "total_defects": 4,
      "critical_defects_count": 3,
      "severity_counts": {
        "Low": 1,
        "Medium": 0,
        "High": 3
      },
      "class_counts": {
        "Pothole": 3,
        "Transverse crack": 1
      },
      "estimated_maintenance_urgency": "URGENT INTERVENTION: High hazard risk to traffic",
      "action_items": [
        "[Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage.",
        "[Transverse crack - High]: Severe thermal cracking with spalling; mill edge boundaries and apply asphalt patch."
      ]
    },
    "defects": [
      {
        "id": 1,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.602,
        "bbox": {
          "x1": 0.1,
          "y1": 306.9,
          "x2": 52.6,
          "y2": 395.1,
          "width": 52.5,
          "height": 88.2
        },
        "bbox_normalized": {
          "x1": 0.0002,
          "y1": 0.5385,
          "x2": 0.0923,
          "y2": 0.6932
        },
        "severity": {
          "level": "High",
          "score": 0.733,
          "color_hex": "#ef4444",
          "area_pixels": 4631,
          "area_pct": 1.425,
          "aspect_ratio": 1.68,
          "extent_norm": 0.155,
          "edge_density": 0.234,
          "contrast_delta": 44.8,
          "rationale": "Severe deep pothole (1.47% area, extent=0.16, contrast=44.8). Acute hazard to vehicle rims and suspension.",
          "recommended_action": "EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
        }
      },
      {
        "id": 2,
        "class_id": 1,
        "class_name": "Transverse crack",
        "confidence": 0.573,
        "bbox": {
          "x1": 347.6,
          "y1": 337.7,
          "x2": 570.0,
          "y2": 372.1,
          "width": 222.4,
          "height": 34.4
        },
        "bbox_normalized": {
          "x1": 0.6099,
          "y1": 0.5925,
          "x2": 1.0,
          "y2": 0.6527
        },
        "severity": {
          "level": "High",
          "score": 0.844,
          "color_hex": "#ef4444",
          "area_pixels": 7638,
          "area_pct": 2.351,
          "aspect_ratio": 6.47,
          "extent_norm": 0.39,
          "edge_density": 0.218,
          "contrast_delta": 16.1,
          "rationale": "Major transverse fracture (lane span=0.40). Full lane span with severe edge spalling and perceptible bump to traffic.",
          "recommended_action": "Severe thermal cracking with spalling; mill edge boundaries and apply asphalt patch."
        }
      },
      {
        "id": 3,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.339,
        "bbox": {
          "x1": 194.0,
          "y1": 333.1,
          "x2": 279.9,
          "y2": 386.5,
          "width": 85.9,
          "height": 53.4
        },
        "bbox_normalized": {
          "x1": 0.3404,
          "y1": 0.5844,
          "x2": 0.491,
          "y2": 0.6781
        },
        "severity": {
          "level": "High",
          "score": 0.724,
          "color_hex": "#ef4444",
          "area_pixels": 4588,
          "area_pct": 1.412,
          "aspect_ratio": 1.61,
          "extent_norm": 0.151,
          "edge_density": 0.189,
          "contrast_delta": 38.8,
          "rationale": "Severe deep pothole (1.45% area, extent=0.15, contrast=38.8). Acute hazard to vehicle rims and suspension.",
          "recommended_action": "EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
        }
      },
      {
        "id": 4,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.692,
        "bbox": {
          "x1": 466.5,
          "y1": 538.6,
          "x2": 515.3,
          "y2": 553.8,
          "width": 48.8,
          "height": 15.2
        },
        "bbox_normalized": {
          "x1": 0.8183,
          "y1": 0.9449,
          "x2": 0.904,
          "y2": 0.9716
        },
        "severity": {
          "level": "Low",
          "score": 0.126,
          "color_hex": "#22c55e",
          "area_pixels": 743,
          "area_pct": 0.229,
          "aspect_ratio": 3.21,
          "extent_norm": 0.086,
          "edge_density": 0.185,
          "contrast_delta": 0.0,
          "rationale": "Small shallow pothole (0.23% area, extent=0.09). Low risk to vehicles; minor ride quality disturbance.",
          "recommended_action": "Surface patch / cold mix during regular maintenance cycle."
        }
      }
    ],
    "markdown_summary": "# Road Pavement Distress & Severity Assessment Report\n\n- **Inspection Source**: `samples\\pothole_sample.jpg`\n- **Pavement Condition Index (PCI)**: **21.0 / 100** (Critical)\n- **Total Defects Detected**: 4\n- **Critical Severity Defects**: 3\n- **Inference Speed**: 56.6 ms via ONNX (Dual-Model WBF Ensemble, CPU-optimized)\n- **Maintenance Urgency**: URGENT INTERVENTION: High hazard risk to traffic\n\n### Severity Breakdown\n- [HIGH] High Severity: 3\n- [MED]  Medium Severity: 0\n- [LOW]  Low Severity: 1\n\n### Detected Defects Log\n| ID | Class | Severity | Conf | Area % | Action Required |\n|---|---|---|---|---|---|\n| #1 | **Pothole** | `High` (0.73) | 60% | 1.43% | EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage. |\n| #2 | **Transverse crack** | `High` (0.84) | 57% | 2.35% | Severe thermal cracking with spalling; mill edge boundaries and apply asphalt patch. |\n| #3 | **Pothole** | `High` (0.72) | 34% | 1.41% | EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage. |\n| #4 | **Pothole** | `Low` (0.13) | 69% | 0.23% | Surface patch / cold mix during regular maintenance cycle. |\n\n### Recommended Action Items\n- [Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage.\n- [Transverse crack - High]: Severe thermal cracking with spalling; mill edge boundaries and apply asphalt patch."
  },
  "alligator_crack_sample": {
    "sample_meta": {
      "id": "alligator_crack_sample",
      "title": "Alligator Fatigue Cracking",
      "category": "Alligator crack",
      "description": "Interconnected polygonal pattern signaling sub-base failure.",
      "filename": "alligator_crack_sample.jpg"
    },
    "metadata": {
      "image_width": 570,
      "image_height": 570,
      "inference_time_ms": 57.42,
      "backend": "ONNX (Dual-Model WBF Ensemble, CPU-optimized)",
      "source": "alligator_crack_sample.jpg"
    },
    "summary": {
      "health_score": 17.0,
      "status": "Critical",
      "total_defects": 4,
      "critical_defects_count": 3,
      "severity_counts": {
        "Low": 0,
        "Medium": 1,
        "High": 3
      },
      "class_counts": {
        "Alligator crack": 2,
        "Longitudinal crack": 1,
        "Pothole": 1
      },
      "estimated_maintenance_urgency": "URGENT INTERVENTION: High hazard risk to traffic",
      "action_items": [
        "[Alligator crack - High]: CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay.",
        "[Longitudinal crack - Medium]: Clean and route crack, fill with rubberized asphalt crack sealant.",
        "[Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
      ]
    },
    "defects": [
      {
        "id": 1,
        "class_id": 2,
        "class_name": "Alligator crack",
        "confidence": 0.693,
        "bbox": {
          "x1": 421.7,
          "y1": 396.5,
          "x2": 561.8,
          "y2": 562.2,
          "width": 140.1,
          "height": 165.7
        },
        "bbox_normalized": {
          "x1": 0.7399,
          "y1": 0.6956,
          "x2": 0.9856,
          "y2": 0.9862
        },
        "severity": {
          "level": "High",
          "score": 0.717,
          "color_hex": "#ef4444",
          "area_pixels": 23202,
          "area_pct": 7.141,
          "aspect_ratio": 1.18,
          "extent_norm": 0.291,
          "edge_density": 0.15,
          "contrast_delta": 20.5,
          "rationale": "Severe alligator fatigue (7.14% area, edge density=0.15). Heavily spalled, loose polygonal block network with base pavement degradation.",
          "recommended_action": "CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
        }
      },
      {
        "id": 2,
        "class_id": 2,
        "class_name": "Alligator crack",
        "confidence": 0.603,
        "bbox": {
          "x1": 0.0,
          "y1": 429.8,
          "x2": 137.4,
          "y2": 562.9,
          "width": 137.4,
          "height": 133.1
        },
        "bbox_normalized": {
          "x1": 0.0,
          "y1": 0.7541,
          "x2": 0.2411,
          "y2": 0.9875
        },
        "severity": {
          "level": "High",
          "score": 0.978,
          "color_hex": "#ef4444",
          "area_pixels": 18281,
          "area_pct": 5.627,
          "aspect_ratio": 1.03,
          "extent_norm": 0.241,
          "edge_density": 0.307,
          "contrast_delta": 18.9,
          "rationale": "Severe alligator fatigue (5.63% area, edge density=0.31). Heavily spalled, loose polygonal block network with base pavement degradation.",
          "recommended_action": "CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
        }
      },
      {
        "id": 3,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.33,
        "bbox": {
          "x1": 145.9,
          "y1": 322.7,
          "x2": 290.7,
          "y2": 462.3,
          "width": 144.8,
          "height": 139.6
        },
        "bbox_normalized": {
          "x1": 0.256,
          "y1": 0.5661,
          "x2": 0.51,
          "y2": 0.811
        },
        "severity": {
          "level": "High",
          "score": 0.913,
          "color_hex": "#ef4444",
          "area_pixels": 20206,
          "area_pct": 6.219,
          "aspect_ratio": 1.04,
          "extent_norm": 0.254,
          "edge_density": 0.07,
          "contrast_delta": 28.0,
          "rationale": "Severe deep pothole (6.28% area, extent=0.26, contrast=28.0). Acute hazard to vehicle rims and suspension.",
          "recommended_action": "EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
        }
      },
      {
        "id": 4,
        "class_id": 0,
        "class_name": "Longitudinal crack",
        "confidence": 0.608,
        "bbox": {
          "x1": 249.6,
          "y1": 15.0,
          "x2": 327.9,
          "y2": 72.8,
          "width": 78.3,
          "height": 57.8
        },
        "bbox_normalized": {
          "x1": 0.4379,
          "y1": 0.0263,
          "x2": 0.5754,
          "y2": 0.1277
        },
        "severity": {
          "level": "Medium",
          "score": 0.533,
          "color_hex": "#f59e0b",
          "area_pixels": 4526,
          "area_pct": 1.393,
          "aspect_ratio": 1.36,
          "extent_norm": 0.137,
          "edge_density": 0.481,
          "contrast_delta": 17.2,
          "rationale": "Moderate longitudinal crack (span=0.16). Crack width 6-20mm with slight edge spalling along wheel path.",
          "recommended_action": "Clean and route crack, fill with rubberized asphalt crack sealant."
        }
      }
    ],
    "markdown_summary": "# Road Pavement Distress & Severity Assessment Report\n\n- **Inspection Source**: `samples\\alligator_crack_sample.jpg`\n- **Pavement Condition Index (PCI)**: **17.0 / 100** (Critical)\n- **Total Defects Detected**: 4\n- **Critical Severity Defects**: 3\n- **Inference Speed**: 57.4 ms via ONNX (Dual-Model WBF Ensemble, CPU-optimized)\n- **Maintenance Urgency**: URGENT INTERVENTION: High hazard risk to traffic\n\n### Severity Breakdown\n- [HIGH] High Severity: 3\n- [MED]  Medium Severity: 1\n- [LOW]  Low Severity: 0\n\n### Detected Defects Log\n| ID | Class | Severity | Conf | Area % | Action Required |\n|---|---|---|---|---|---|\n| #1 | **Alligator crack** | `High` (0.72) | 69% | 7.14% | CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay. |\n| #2 | **Alligator crack** | `High` (0.98) | 60% | 5.63% | CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay. |\n| #3 | **Pothole** | `High` (0.91) | 33% | 6.22% | EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage. |\n| #4 | **Longitudinal crack** | `Medium` (0.53) | 61% | 1.39% | Clean and route crack, fill with rubberized asphalt crack sealant. |\n\n### Recommended Action Items\n- [Alligator crack - High]: CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay.\n- [Longitudinal crack - Medium]: Clean and route crack, fill with rubberized asphalt crack sealant.\n- [Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
  },
  "longitudinal_crack_sample": {
    "sample_meta": {
      "id": "longitudinal_crack_sample",
      "title": "Longitudinal Wheel-Path Crack",
      "category": "Longitudinal crack",
      "description": "Linear crack running parallel to traffic direction.",
      "filename": "longitudinal_crack_sample.jpg"
    },
    "metadata": {
      "image_width": 570,
      "image_height": 570,
      "inference_time_ms": 64.1,
      "backend": "ONNX (Dual-Model WBF Ensemble, CPU-optimized)",
      "source": "longitudinal_crack_sample.jpg"
    },
    "summary": {
      "health_score": 55.0,
      "status": "Poor",
      "total_defects": 3,
      "critical_defects_count": 2,
      "severity_counts": {
        "Low": 0,
        "Medium": 1,
        "High": 2
      },
      "class_counts": {
        "Longitudinal crack": 2,
        "Alligator crack": 1
      },
      "estimated_maintenance_urgency": "Corrective Repair Needed (within 30 days)",
      "action_items": [
        "[Longitudinal crack - High]: Deep rout, structural seal, and investigate potential pavement base settlement.",
        "[Alligator crack - High]: CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
      ]
    },
    "defects": [
      {
        "id": 1,
        "class_id": 2,
        "class_name": "Alligator crack",
        "confidence": 0.34,
        "bbox": {
          "x1": 419.6,
          "y1": 308.0,
          "x2": 562.9,
          "y2": 424.4,
          "width": 143.3,
          "height": 116.4
        },
        "bbox_normalized": {
          "x1": 0.7362,
          "y1": 0.5403,
          "x2": 0.9875,
          "y2": 0.7445
        },
        "severity": {
          "level": "High",
          "score": 0.821,
          "color_hex": "#ef4444",
          "area_pixels": 16675,
          "area_pct": 5.132,
          "aspect_ratio": 1.23,
          "extent_norm": 0.251,
          "edge_density": 0.213,
          "contrast_delta": 13.4,
          "rationale": "Severe alligator fatigue (5.26% area, edge density=0.21). Heavily spalled, loose polygonal block network with base pavement degradation.",
          "recommended_action": "CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
        }
      },
      {
        "id": 2,
        "class_id": 0,
        "class_name": "Longitudinal crack",
        "confidence": 0.265,
        "bbox": {
          "x1": 302.4,
          "y1": 262.5,
          "x2": 389.4,
          "y2": 424.9,
          "width": 87.0,
          "height": 162.4
        },
        "bbox_normalized": {
          "x1": 0.5305,
          "y1": 0.4606,
          "x2": 0.6831,
          "y2": 0.7455
        },
        "severity": {
          "level": "High",
          "score": 0.665,
          "color_hex": "#ef4444",
          "area_pixels": 14129,
          "area_pct": 4.349,
          "aspect_ratio": 1.87,
          "extent_norm": 0.285,
          "edge_density": 0.198,
          "contrast_delta": 11.7,
          "rationale": "Extensive longitudinal crack (span=0.29). High severity; wide crack with continuous joint opening and aggregate loss.",
          "recommended_action": "Deep rout, structural seal, and investigate potential pavement base settlement."
        }
      },
      {
        "id": 3,
        "class_id": 0,
        "class_name": "Longitudinal crack",
        "confidence": 0.778,
        "bbox": {
          "x1": 47.8,
          "y1": 339.9,
          "x2": 137.2,
          "y2": 411.9,
          "width": 89.4,
          "height": 72.0
        },
        "bbox_normalized": {
          "x1": 0.0838,
          "y1": 0.5964,
          "x2": 0.2406,
          "y2": 0.7226
        },
        "severity": {
          "level": "Medium",
          "score": 0.411,
          "color_hex": "#f59e0b",
          "area_pixels": 6434,
          "area_pct": 1.98,
          "aspect_ratio": 1.24,
          "extent_norm": 0.157,
          "edge_density": 0.149,
          "contrast_delta": 54.9,
          "rationale": "Moderate longitudinal crack (span=0.16). Crack width 6-20mm with slight edge spalling along wheel path.",
          "recommended_action": "Clean and route crack, fill with rubberized asphalt crack sealant."
        }
      }
    ],
    "markdown_summary": "# Road Pavement Distress & Severity Assessment Report\n\n- **Inspection Source**: `samples\\longitudinal_crack_sample.jpg`\n- **Pavement Condition Index (PCI)**: **55.0 / 100** (Poor)\n- **Total Defects Detected**: 3\n- **Critical Severity Defects**: 2\n- **Inference Speed**: 64.1 ms via ONNX (Dual-Model WBF Ensemble, CPU-optimized)\n- **Maintenance Urgency**: Corrective Repair Needed (within 30 days)\n\n### Severity Breakdown\n- [HIGH] High Severity: 2\n- [MED]  Medium Severity: 1\n- [LOW]  Low Severity: 0\n\n### Detected Defects Log\n| ID | Class | Severity | Conf | Area % | Action Required |\n|---|---|---|---|---|---|\n| #1 | **Alligator crack** | `High` (0.82) | 34% | 5.13% | CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay. |\n| #2 | **Longitudinal crack** | `High` (0.67) | 26% | 4.35% | Deep rout, structural seal, and investigate potential pavement base settlement. |\n| #3 | **Longitudinal crack** | `Medium` (0.41) | 78% | 1.98% | Clean and route crack, fill with rubberized asphalt crack sealant. |\n\n### Recommended Action Items\n- [Longitudinal crack - High]: Deep rout, structural seal, and investigate potential pavement base settlement.\n- [Alligator crack - High]: CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
  },
  "multi_defect_pavement": {
    "sample_meta": {
      "id": "multi_defect_pavement",
      "title": "Multi-Defect Distressed Roadway",
      "category": "Multi-Defect",
      "description": "Combined potholes, longitudinal cracks, and fatigue cracking.",
      "filename": "multi_defect_pavement.jpg"
    },
    "metadata": {
      "image_width": 570,
      "image_height": 570,
      "inference_time_ms": 66.51,
      "backend": "ONNX (Dual-Model WBF Ensemble, CPU-optimized)",
      "source": "multi_defect_pavement.jpg"
    },
    "summary": {
      "health_score": 2.0,
      "status": "Critical",
      "total_defects": 5,
      "critical_defects_count": 4,
      "severity_counts": {
        "Low": 0,
        "Medium": 1,
        "High": 4
      },
      "class_counts": {
        "Pothole": 1,
        "Alligator crack": 2,
        "Longitudinal crack": 1,
        "Transverse crack": 1
      },
      "estimated_maintenance_urgency": "URGENT INTERVENTION: High hazard risk to traffic",
      "action_items": [
        "[Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage.",
        "[Alligator crack - High]: CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay.",
        "[Longitudinal crack - High]: Deep rout, structural seal, and investigate potential pavement base settlement.",
        "[Transverse crack - Medium]: Rout and seal with hot-pour elastomeric sealant."
      ]
    },
    "defects": [
      {
        "id": 1,
        "class_id": 3,
        "class_name": "Pothole",
        "confidence": 0.875,
        "bbox": {
          "x1": 269.9,
          "y1": 417.1,
          "x2": 363.1,
          "y2": 560.9,
          "width": 93.2,
          "height": 143.8
        },
        "bbox_normalized": {
          "x1": 0.4734,
          "y1": 0.7318,
          "x2": 0.6371,
          "y2": 0.9841
        },
        "severity": {
          "level": "High",
          "score": 0.809,
          "color_hex": "#ef4444",
          "area_pixels": 13412,
          "area_pct": 4.128,
          "aspect_ratio": 1.54,
          "extent_norm": 0.252,
          "edge_density": 0.323,
          "contrast_delta": 13.9,
          "rationale": "Severe deep pothole (4.13% area, extent=0.25, contrast=13.9). Acute hazard to vehicle rims and suspension.",
          "recommended_action": "EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage."
        }
      },
      {
        "id": 2,
        "class_id": 2,
        "class_name": "Alligator crack",
        "confidence": 0.641,
        "bbox": {
          "x1": 69.3,
          "y1": 474.1,
          "x2": 217.2,
          "y2": 563.0,
          "width": 147.9,
          "height": 88.9
        },
        "bbox_normalized": {
          "x1": 0.1216,
          "y1": 0.8317,
          "x2": 0.381,
          "y2": 0.9877
        },
        "severity": {
          "level": "High",
          "score": 1.0,
          "color_hex": "#ef4444",
          "area_pixels": 13148,
          "area_pct": 4.047,
          "aspect_ratio": 1.66,
          "extent_norm": 0.259,
          "edge_density": 0.375,
          "contrast_delta": 33.5,
          "rationale": "Severe alligator fatigue (4.05% area, edge density=0.38). Heavily spalled, loose polygonal block network with base pavement degradation.",
          "recommended_action": "CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
        }
      },
      {
        "id": 3,
        "class_id": 2,
        "class_name": "Alligator crack",
        "confidence": 0.433,
        "bbox": {
          "x1": 65.2,
          "y1": 0.1,
          "x2": 151.1,
          "y2": 101.8,
          "width": 85.9,
          "height": 101.7
        },
        "bbox_normalized": {
          "x1": 0.1143,
          "y1": 0.0002,
          "x2": 0.265,
          "y2": 0.1785
        },
        "severity": {
          "level": "High",
          "score": 1.0,
          "color_hex": "#ef4444",
          "area_pixels": 8734,
          "area_pct": 2.688,
          "aspect_ratio": 1.18,
          "extent_norm": 0.178,
          "edge_density": 0.517,
          "contrast_delta": 1.9,
          "rationale": "Severe alligator fatigue (3.25% area, edge density=0.52). Heavily spalled, loose polygonal block network with base pavement degradation.",
          "recommended_action": "CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay."
        }
      },
      {
        "id": 4,
        "class_id": 0,
        "class_name": "Longitudinal crack",
        "confidence": 0.429,
        "bbox": {
          "x1": 539.6,
          "y1": 0.0,
          "x2": 569.9,
          "y2": 138.0,
          "width": 30.3,
          "height": 138.0
        },
        "bbox_normalized": {
          "x1": 0.9467,
          "y1": 0.0,
          "x2": 0.9998,
          "y2": 0.2421
        },
        "severity": {
          "level": "High",
          "score": 0.706,
          "color_hex": "#ef4444",
          "area_pixels": 4179,
          "area_pct": 1.286,
          "aspect_ratio": 4.56,
          "extent_norm": 0.242,
          "edge_density": 0.316,
          "contrast_delta": 17.1,
          "rationale": "Extensive longitudinal crack (span=0.28). High severity; wide crack with continuous joint opening and aggregate loss.",
          "recommended_action": "Deep rout, structural seal, and investigate potential pavement base settlement."
        }
      },
      {
        "id": 5,
        "class_id": 1,
        "class_name": "Transverse crack",
        "confidence": 0.3,
        "bbox": {
          "x1": 178.2,
          "y1": 18.4,
          "x2": 254.8,
          "y2": 37.4,
          "width": 76.6,
          "height": 19.0
        },
        "bbox_normalized": {
          "x1": 0.3126,
          "y1": 0.0323,
          "x2": 0.447,
          "y2": 0.0657
        },
        "severity": {
          "level": "Medium",
          "score": 0.529,
          "color_hex": "#f59e0b",
          "area_pixels": 1457,
          "area_pct": 0.448,
          "aspect_ratio": 4.03,
          "extent_norm": 0.134,
          "edge_density": 0.287,
          "contrast_delta": 6.5,
          "rationale": "Moderate transverse crack (lane span=0.16). Width 6-20mm across mid-lane with minor chipping along crack lips.",
          "recommended_action": "Rout and seal with hot-pour elastomeric sealant."
        }
      }
    ],
    "markdown_summary": "# Road Pavement Distress & Severity Assessment Report\n\n- **Inspection Source**: `samples\\multi_defect_pavement.jpg`\n- **Pavement Condition Index (PCI)**: **2.0 / 100** (Critical)\n- **Total Defects Detected**: 5\n- **Critical Severity Defects**: 4\n- **Inference Speed**: 66.5 ms via ONNX (Dual-Model WBF Ensemble, CPU-optimized)\n- **Maintenance Urgency**: URGENT INTERVENTION: High hazard risk to traffic\n\n### Severity Breakdown\n- [HIGH] High Severity: 4\n- [MED]  Medium Severity: 1\n- [LOW]  Low Severity: 0\n\n### Detected Defects Log\n| ID | Class | Severity | Conf | Area % | Action Required |\n|---|---|---|---|---|---|\n| #1 | **Pothole** | `High` (0.81) | 88% | 4.13% | EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage. |\n| #2 | **Alligator crack** | `High` (1.00) | 64% | 4.05% | CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay. |\n| #3 | **Alligator crack** | `High` (1.00) | 43% | 2.69% | CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay. |\n| #4 | **Longitudinal crack** | `High` (0.71) | 43% | 1.29% | Deep rout, structural seal, and investigate potential pavement base settlement. |\n| #5 | **Transverse crack** | `Medium` (0.53) | 30% | 0.45% | Rout and seal with hot-pour elastomeric sealant. |\n\n### Recommended Action Items\n- [Pothole - High]: EMERGENCY: Immediate mill and deep structural patch required to prevent wheel/axle damage.\n- [Alligator crack - High]: CRITICAL: Base layer fatigue failure; requires full-depth reclamation / asphalt overlay.\n- [Longitudinal crack - High]: Deep rout, structural seal, and investigate potential pavement base settlement.\n- [Transverse crack - Medium]: Rout and seal with hot-pour elastomeric sealant."
  },
  "transverse_longitudinal_crack": {
    "sample_meta": {
      "id": "transverse_longitudinal_crack",
      "title": "Transverse & Longitudinal Joints",
      "category": "Transverse & Longitudinal",
      "description": "Intersecting thermal and wheel-path cracks across asphalt lane.",
      "filename": "transverse_longitudinal_crack.jpg"
    },
    "metadata": {
      "image_width": 570,
      "image_height": 570,
      "inference_time_ms": 61.16,
      "backend": "ONNX (Dual-Model WBF Ensemble, CPU-optimized)",
      "source": "transverse_longitudinal_crack.jpg"
    },
    "summary": {
      "health_score": 75.0,
      "status": "Fair",
      "total_defects": 4,
      "critical_defects_count": 1,
      "severity_counts": {
        "Low": 3,
        "Medium": 0,
        "High": 1
      },
      "class_counts": {
        "Transverse crack": 1,
        "Longitudinal crack": 3
      },
      "estimated_maintenance_urgency": "Preventative Maintenance (within 60-90 days)",
      "action_items": [
        "[Transverse crack - High]: Severe thermal cracking with spalling; mill edge boundaries and apply asphalt patch.",
        "[Longitudinal crack - Low]: Monitor during next routine survey; verify joint integrity."
      ]
    },
    "defects": [
      {
        "id": 1,
        "class_id": 1,
        "class_name": "Transverse crack",
        "confidence": 0.635,
        "bbox": {
          "x1": 144.9,
          "y1": 483.2,
          "x2": 554.7,
          "y2": 531.3,
          "width": 409.8,
          "height": 48.1
        },
        "bbox_normalized": {
          "x1": 0.2542,
          "y1": 0.8477,
          "x2": 0.9731,
          "y2": 0.932
        },
        "severity": {
          "level": "High",
          "score": 1.0,
          "color_hex": "#ef4444",
          "area_pixels": 19697,
          "area_pct": 6.062,
          "aspect_ratio": 8.52,
          "extent_norm": 0.719,
          "edge_density": 0.467,
          "contrast_delta": 12.1,
          "rationale": "Major transverse fracture (lane span=0.72). Full lane span with severe edge spalling and perceptible bump to traffic.",
          "recommended_action": "Severe thermal cracking with spalling; mill edge boundaries and apply asphalt patch."
        }
      },
      {
        "id": 2,
        "class_id": 0,
        "class_name": "Longitudinal crack",
        "confidence": 0.478,
        "bbox": {
          "x1": 55.6,
          "y1": 32.2,
          "x2": 74.0,
          "y2": 61.7,
          "width": 18.4,
          "height": 29.5
        },
        "bbox_normalized": {
          "x1": 0.0976,
          "y1": 0.0564,
          "x2": 0.1299,
          "y2": 0.1083
        },
        "severity": {
          "level": "Low",
          "score": 0.286,
          "color_hex": "#22c55e",
          "area_pixels": 543,
          "area_pct": 0.167,
          "aspect_ratio": 1.61,
          "extent_norm": 0.052,
          "edge_density": 0.165,
          "contrast_delta": 20.7,
          "rationale": "Narrow hairline longitudinal crack (span=0.06). Low severity; crack width < 6mm equivalent with intact joint.",
          "recommended_action": "Monitor during next routine survey; verify joint integrity."
        }
      },
      {
        "id": 3,
        "class_id": 0,
        "class_name": "Longitudinal crack",
        "confidence": 0.427,
        "bbox": {
          "x1": 310.0,
          "y1": 238.4,
          "x2": 333.6,
          "y2": 280.6,
          "width": 23.6,
          "height": 42.2
        },
        "bbox_normalized": {
          "x1": 0.5439,
          "y1": 0.4182,
          "x2": 0.5852,
          "y2": 0.4923
        },
        "severity": {
          "level": "Low",
          "score": 0.141,
          "color_hex": "#22c55e",
          "area_pixels": 995,
          "area_pct": 0.306,
          "aspect_ratio": 1.79,
          "extent_norm": 0.074,
          "edge_density": 0.022,
          "contrast_delta": 36.3,
          "rationale": "Narrow hairline longitudinal crack (span=0.08). Low severity; crack width < 6mm equivalent with intact joint.",
          "recommended_action": "Monitor during next routine survey; verify joint integrity."
        }
      },
      {
        "id": 4,
        "class_id": 0,
        "class_name": "Longitudinal crack",
        "confidence": 0.366,
        "bbox": {
          "x1": 296.1,
          "y1": 134.6,
          "x2": 311.3,
          "y2": 160.4,
          "width": 15.2,
          "height": 25.8
        },
        "bbox_normalized": {
          "x1": 0.5196,
          "y1": 0.2361,
          "x2": 0.5462,
          "y2": 0.2814
        },
        "severity": {
          "level": "Low",
          "score": 0.186,
          "color_hex": "#22c55e",
          "area_pixels": 391,
          "area_pct": 0.12,
          "aspect_ratio": 1.7,
          "extent_norm": 0.045,
          "edge_density": 0.093,
          "contrast_delta": 11.4,
          "rationale": "Narrow hairline longitudinal crack (span=0.05). Low severity; crack width < 6mm equivalent with intact joint.",
          "recommended_action": "Monitor during next routine survey; verify joint integrity."
        }
      }
    ],
    "markdown_summary": "# Road Pavement Distress & Severity Assessment Report\n\n- **Inspection Source**: `samples\\transverse_longitudinal_crack.jpg`\n- **Pavement Condition Index (PCI)**: **75.0 / 100** (Fair)\n- **Total Defects Detected**: 4\n- **Critical Severity Defects**: 1\n- **Inference Speed**: 61.2 ms via ONNX (Dual-Model WBF Ensemble, CPU-optimized)\n- **Maintenance Urgency**: Preventative Maintenance (within 60-90 days)\n\n### Severity Breakdown\n- [HIGH] High Severity: 1\n- [MED]  Medium Severity: 0\n- [LOW]  Low Severity: 3\n\n### Detected Defects Log\n| ID | Class | Severity | Conf | Area % | Action Required |\n|---|---|---|---|---|---|\n| #1 | **Transverse crack** | `High` (1.00) | 64% | 6.06% | Severe thermal cracking with spalling; mill edge boundaries and apply asphalt patch. |\n| #2 | **Longitudinal crack** | `Low` (0.29) | 48% | 0.17% | Monitor during next routine survey; verify joint integrity. |\n| #3 | **Longitudinal crack** | `Low` (0.14) | 43% | 0.31% | Monitor during next routine survey; verify joint integrity. |\n| #4 | **Longitudinal crack** | `Low` (0.19) | 37% | 0.12% | Monitor during next routine survey; verify joint integrity. |\n\n### Recommended Action Items\n- [Transverse crack - High]: Severe thermal cracking with spalling; mill edge boundaries and apply asphalt patch.\n- [Longitudinal crack - Low]: Monitor during next routine survey; verify joint integrity."
  }
};
