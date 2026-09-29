"""
Custom Training and Fine-Tuning Pipeline for Road Damage Detection.
Supports YOLO txt, Pascal VOC XML, and COCO JSON annotation formats.
Trains YOLOv8-nano on custom road photos and exports optimized ONNX models.
"""

import glob
import os
import shutil
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Union
import yaml

from road_damage_vision.config import DEFECT_CLASSES

# Canonical class mapping
CLASS_MAP = {
    # 0: Longitudinal crack
    "longitudinal crack": 0,
    "longitudinal_crack": 0,
    "d00": 0,
    "d00_longitudinal": 0,
    # 1: Transverse crack
    "transverse crack": 1,
    "transverse_crack": 1,
    "d10": 1,
    "d10_transverse": 1,
    # 2: Alligator crack
    "alligator crack": 2,
    "alligator_crack": 2,
    "d20": 2,
    "d20_alligator": 2,
    # 3: Pothole
    "pothole": 3,
    "d40": 3,
    "d40_pothole": 3,
}

DATASET_ROOT = "dataset"
IMAGES_DIR = os.path.join(DATASET_ROOT, "images")
LABELS_DIR = os.path.join(DATASET_ROOT, "labels")


def setup_dataset_structure():
    """Initializes dataset folders and data.yaml configuration."""
    for split in ["train", "val"]:
        os.makedirs(os.path.join(IMAGES_DIR, split), exist_ok=True)
        os.makedirs(os.path.join(LABELS_DIR, split), exist_ok=True)

    data_yaml_content = {
        "path": os.path.abspath(DATASET_ROOT).replace("\\", "/"),
        "train": "images/train",
        "val": "images/val",
        "names": {
            0: "Longitudinal crack",
            1: "Transverse crack",
            2: "Alligator crack",
            3: "Pothole",
        },
    }

    yaml_path = os.path.join(DATASET_ROOT, "data.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data_yaml_content, f, sort_keys=False)

    print(f"[*] Dataset structure initialized at: {DATASET_ROOT}")
    print(f"[*] Configuration saved to: {yaml_path}")
    return yaml_path


def convert_voc_xml_to_yolo(xml_file: str, img_w: int, img_h: int) -> str:
    """Converts a Pascal VOC XML annotation file to YOLO format lines."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    yolo_lines = []

    # Get image size from XML if not provided
    size_el = root.find("size")
    if size_el is not None:
        w_el = size_el.find("width")
        h_el = size_el.find("height")
        if w_el is not None and int(w_el.text) > 0:
            img_w = int(w_el.text)
        if h_el is not None and int(h_el.text) > 0:
            img_h = int(h_el.text)

    for obj in root.findall("object"):
        name = obj.find("name").text.strip().lower()
        if name not in CLASS_MAP:
            continue
        cls_id = CLASS_MAP[name]

        bndbox = obj.find("bndbox")
        xmin = float(bndbox.find("xmin").text)
        ymin = float(bndbox.find("ymin").text)
        xmax = float(bndbox.find("xmax").text)
        ymax = float(bndbox.find("ymax").text)

        # Convert to normalized xywh
        x_center = ((xmin + xmax) / 2.0) / img_w
        y_center = ((ymin + ymax) / 2.0) / img_h
        width = (xmax - xmin) / img_w
        height = (ymax - ymin) / img_h

        yolo_lines.append(f"{cls_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

    return "\n".join(yolo_lines)


def train_model(
    data_yaml: str = "dataset/data.yaml",
    pretrained_weights: str = "models/rdd2022_yolov8n.pt",
    epochs: int = 30,
    imgsz: int = 640,
    batch_size: int = 8,
    output_name: str = "custom_rdd_model",
):
    """
    Trains / fine-tunes YOLOv8-nano on custom annotated dataset and exports to ONNX.
    """
    from ultralytics import YOLO

    print(f"\n[*] Starting training with base weights: {pretrained_weights}")
    print(f"[*] Epochs: {epochs} | Batch size: {batch_size} | Image size: {imgsz}")

    model = YOLO(pretrained_weights)

    # Train with augmentation tuned for road textures
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        device="cpu",
        project="runs/detect",
        name=output_name,
        exist_ok=True,
        save=True,
        verbose=True,
        # Road augmentation hyperparameters
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.4,
        degrees=5.0,
        translate=0.1,
        scale=0.3,
        fliplr=0.5,
        mosaic=0.5,
    )

    best_pt = os.path.join("runs", "detect", output_name, "weights", "best.pt")
    if not os.path.exists(best_pt):
        best_pt = os.path.join("runs", "detect", output_name, "weights", "last.pt")

    print(f"\n[+] Training complete! Best weights saved to: {best_pt}")

    # Copy to models directory
    dest_pt = f"models/{output_name}.pt"
    shutil.copy(best_pt, dest_pt)
    print(f"[+] Saved model to: {dest_pt}")

    # Export to ONNX for fast CPU inference
    print("[*] Exporting fine-tuned model to ONNX...")
    trained_model = YOLO(dest_pt)
    onnx_path = trained_model.export(format="onnx", imgsz=imgsz, dynamic=False)
    dest_onnx = f"models/{output_name}.onnx"
    if os.path.exists(onnx_path):
        if os.path.abspath(onnx_path) != os.path.abspath(dest_onnx):
            shutil.copy(onnx_path, dest_onnx)
        print(f"[+] Exported ONNX to: {dest_onnx}")

    return dest_pt, dest_onnx


if __name__ == "__main__":
    setup_dataset_structure()
