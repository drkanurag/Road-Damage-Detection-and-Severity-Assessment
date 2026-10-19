"""
Custom Training and Fine-Tuning Pipeline for Road Damage Detection.
Supports YOLO txt, Pascal VOC XML, and COCO JSON annotation formats.
Trains YOLOv8-nano on custom road photos and exports optimized ONNX models.
"""

import glob
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import yaml

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
POTHOLE_DATASET_ROOT = "dataset_pothole_only"


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


def build_pothole_only_dataset(
    source_root: str = DATASET_ROOT,
    output_root: str = POTHOLE_DATASET_ROOT,
    max_new_images: int = 400,
) -> str:
    """Create an isolated one-class dataset combining base RDD and new dashcam imagery.

    Potholes (Class 3 in RDD, Class 0 in new_dashcam) become class 0.
    Spatial road verification ensures only potholes lying on the road surface
    are kept. Images with other pavement features (cracks, manholes) or road
    scenes with buildings, cars, sidewalks, and car hoods are kept with empty
    label files as valuable hard negatives that teach the model NOT to flag
    buildings, cars, sidewalks, or normal asphalt as potholes.
    """
    source = Path(source_root)
    output = Path(output_root)
    image_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    image_count = pothole_count = negative_count = 0

    for split in ("train", "val"):
        source_images = source / "images" / split
        source_labels = source / "labels" / split
        target_images = output / "images" / split
        target_labels = output / "labels" / split
        target_images.mkdir(parents=True, exist_ok=True)
        target_labels.mkdir(parents=True, exist_ok=True)

        if source_images.exists():
            for image_path in source_images.rglob("*"):
                if not image_path.is_file() or image_path.suffix.lower() not in image_exts:
                    continue
                relative = image_path.relative_to(source_images)
                target_image = target_images / relative
                target_image.parent.mkdir(parents=True, exist_ok=True)
                if not target_image.exists():
                    try:
                        os.link(image_path, target_image)
                    except OSError:
                        shutil.copy2(image_path, target_image)

                source_label = (source_labels / relative).with_suffix(".txt")
                target_label = (target_labels / relative).with_suffix(".txt")
                target_label.parent.mkdir(parents=True, exist_ok=True)
                pothole_lines: List[str] = []
                if source_label.exists():
                    for line in source_label.read_text(encoding="utf-8").splitlines():
                        fields = line.split()
                        if len(fields) == 5 and fields[0] == "3":
                            pothole_lines.append("0 " + " ".join(fields[1:]))
                target_label.write_text("\n".join(pothole_lines), encoding="utf-8")
                image_count += 1
                pothole_count += len(pothole_lines)
                negative_count += int(not pothole_lines)

    # Ingest new dashcam dataset (from dataset/new_dashcam or archive/data)
    new_dashcam_candidates = [
        source / "new_dashcam",
        Path("dataset/new_dashcam"),
        Path(r"c:\Users\anura\Downloads\archive\data"),
    ]
    dashcam_root = next((p for p in new_dashcam_candidates if p.exists() and (p / "images").exists()), None)
    if dashcam_root:
        dashcam_imgs = list((dashcam_root / "images").glob("*.jpg"))
        dashcam_labels_dir = dashcam_root / "labels-YOLO"
        print(f"[*] Found {len(dashcam_imgs)} new dashcam images in: {dashcam_root}")

        import random
        random.seed(42)
        # Separate positive pothole images and negative background images
        pos_dashcam = []
        neg_dashcam = []
        for imp in dashcam_imgs:
            lbl_file = dashcam_labels_dir / (imp.stem + ".txt")
            has_pothole = False
            if lbl_file.exists():
                for line in lbl_file.read_text(encoding="utf-8").splitlines():
                    parts = line.strip().split()
                    if len(parts) >= 5 and parts[0] == "0":
                        has_pothole = True
                        break
            if has_pothole:
                pos_dashcam.append(imp)
            else:
                neg_dashcam.append(imp)

        # Sample a balanced subset for training
        n_pos = min(len(pos_dashcam), int(max_new_images * 0.70))
        n_neg = min(len(neg_dashcam), int(max_new_images * 0.30))
        selected_pos = random.sample(pos_dashcam, n_pos)
        selected_neg = random.sample(neg_dashcam, n_neg)
        selected_dashcam = [(p, True) for p in selected_pos] + [(p, False) for p in selected_neg]
        random.shuffle(selected_dashcam)

        new_ingested = 0
        for imp, is_pos in selected_dashcam:
            split = "val" if random.random() < 0.18 else "train"
            target_image = output / "images" / split / imp.name
            target_label = output / "labels" / split / (imp.stem + ".txt")
            if not target_image.exists():
                try:
                    os.link(imp, target_image)
                except OSError:
                    shutil.copy2(imp, target_image)

            pothole_lines = []
            lbl_file = dashcam_labels_dir / (imp.stem + ".txt")
            if is_pos and lbl_file.exists():
                for line in lbl_file.read_text(encoding="utf-8").splitlines():
                    parts = line.strip().split()
                    if len(parts) >= 5 and parts[0] == "0":
                        yc = float(parts[2])
                        # Road plane spatial rule: potholes must be below horizon and above car hood
                        if 0.32 <= yc <= 0.88:
                            pothole_lines.append("0 " + " ".join(parts[1:]))

            target_label.write_text("\n".join(pothole_lines), encoding="utf-8")
            image_count += 1
            pothole_count += len(pothole_lines)
            negative_count += int(not pothole_lines)
            new_ingested += 1

        print(f"[*] Ingested {new_ingested} new dashcam images ({n_pos} pothole frames, {n_neg} hard-negative scenes).")

    data_yaml = {
        "path": str(output.resolve()).replace("\\", "/"),
        "train": "images/train",
        "val": "images/val",
        "names": {0: "Pothole"},
    }
    yaml_path = output / "data.yaml"
    yaml_path.write_text(yaml.dump(data_yaml, sort_keys=False), encoding="utf-8")
    print(
        f"[*] Unified Pothole-only dataset ready: {image_count} total images, "
        f"{pothole_count} pothole labels, {negative_count} hard-negative images."
    )
    return str(yaml_path)


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
    epochs: int = 3,
    imgsz: int = 640,
    batch_size: int = 8,
    fraction: float = 0.05,
    output_name: str = "custom_rdd_model",
):
    """
    Trains / fine-tunes YOLOv8-nano on custom annotated dataset and exports to ONNX.
    """
    from ultralytics import YOLO

    print(f"\n[*] Starting training with base weights: {pretrained_weights}")
    print(f"[*] Epochs: {epochs} | Batch size: {batch_size} | Image size: {imgsz} | Fraction: {fraction}")

    model = YOLO(pretrained_weights)

    # Train with augmentation tuned for road textures
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        fraction=fraction,
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

    # Ultralytics may prefix the configured project directory through its global
    # settings, so use the trainer's resolved directory rather than rebuilding
    # a path from assumptions.
    run_dir = Path(getattr(model.trainer, "save_dir", Path("runs") / "detect" / output_name))
    best_pt = run_dir / "weights" / "best.pt"
    if not best_pt.exists():
        best_pt = run_dir / "weights" / "last.pt"

    print(f"\n[+] Training complete! Best weights saved to: {best_pt}")

    # Copy to models directory
    dest_pt = f"models/{output_name}.pt"
    shutil.copy(str(best_pt), dest_pt)
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


def train_pothole_model(
    epochs: int = 3,
    imgsz: int = 640,
    batch_size: int = 8,
    fraction: float = 0.05,
    pretrained_weights: str = "models/rdd2022_india_trained.pt",
    output_name: str = "pothole_only_yolov8n",
    sync_to_live: bool = True,
):
    """Fine-tune a single-class pothole detector using the unified road dataset."""
    data_yaml = build_pothole_only_dataset()
    dest_pt, dest_onnx = train_model(
        data_yaml=data_yaml,
        pretrained_weights=pretrained_weights,
        epochs=epochs,
        imgsz=imgsz,
        batch_size=batch_size,
        fraction=fraction,
        output_name=output_name,
    )

    if sync_to_live:
        # Sync to specialist model path so live inference immediately benefits
        spec_pt = "models/rdd2022_india_trained.pt"
        spec_onnx = "models/rdd2022_india_trained.onnx"
        if os.path.exists(dest_pt):
            shutil.copy2(dest_pt, spec_pt)
            print(f"[+] Synced fine-tuned weights to live PyTorch engine: {spec_pt}")
        if os.path.exists(dest_onnx):
            shutil.copy2(dest_onnx, spec_onnx)
            print(f"[+] Synced fine-tuned ONNX model to live inference engine: {spec_onnx}")

    return dest_pt, dest_onnx


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RoadVision model training")
    parser.add_argument("--pothole-only", action="store_true", help="train the one-class pothole detector")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--fraction", type=float, default=0.05, help="dataset fraction to use (for CPU speed)")
    args = parser.parse_args()

    if args.pothole_only:
        train_pothole_model(epochs=args.epochs, batch_size=args.batch, fraction=args.fraction)
    else:
        setup_dataset_structure()

