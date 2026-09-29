"""
Command-Line Interface (CLI) for Road Damage Detection and Severity Assessment.

Usage Examples:
  python cli.py --image samples/pothole_sample.jpg --output results/
  python cli.py --dir samples/ --conf 0.30 --backend onnx --save-crops
"""

import argparse
import glob
import os
import sys
import time
import cv2

from road_damage_vision import (
    RoadDamageDetector,
    RoadDamageVisualizer,
    generate_markdown_summary,
    save_csv_report,
    save_json_report,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Lightweight Road Damage Detection & Severity Assessment CLI"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", "-i", type=str, help="Path to a single road image")
    group.add_argument("--dir", "-d", type=str, help="Directory containing road images for batch analysis")

    parser.add_argument(
        "--conf", "-c", type=float, default=0.25, help="Confidence threshold (default: 0.25)"
    )
    parser.add_argument(
        "--iou", type=float, default=0.45, help="NMS IoU threshold (default: 0.45)"
    )
    parser.add_argument(
        "--backend", "-b", type=str, choices=["onnx", "pytorch"], default="onnx",
        help="Inference engine backend (default: onnx)"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="output", help="Directory to save output annotations and reports"
    )
    parser.add_argument(
        "--save-crops", action="store_true", help="Extract and save cropped defect thumbnails"
    )
    parser.add_argument(
        "--no-hud", action="store_true", help="Disable the executive summary HUD banner on output images"
    )
    return parser.parse_args()


def process_single_image(image_path: str, detector: RoadDamageDetector, visualizer: RoadDamageVisualizer, args):
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    out_dir = args.output
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n[+] Analyzing: {image_path}")
    t0 = time.time()
    report = detector.predict(image_path, conf_threshold=args.conf, iou_threshold=args.iou)
    elapsed = (time.time() - t0) * 1000

    print(f"    - Resolution: {report.image_shape[1]}x{report.image_shape[0]}")
    print(f"    - Latency: {report.inference_time_ms:.1f}ms (Engine: {report.backend_used})")
    print(f"    - Health Index: {report.summary.health_score:.0f}/100 [{report.summary.status}]")
    print(f"    - Total Defects: {report.summary.total_defects} "
          f"(High: {report.summary.severity_counts.get('High', 0)}, "
          f"Med: {report.summary.severity_counts.get('Medium', 0)}, "
          f"Low: {report.summary.severity_counts.get('Low', 0)})")

    # Render annotated visualization
    annotated = visualizer.draw(image_path, report)
    annotated_path = os.path.join(out_dir, f"{base_name}_annotated.jpg")
    cv2.imwrite(annotated_path, annotated)
    print(f"    - Annotated image saved: {annotated_path}")

    # Export reports
    json_path = os.path.join(out_dir, f"{base_name}_report.json")
    save_json_report(report, json_path)

    csv_path = os.path.join(out_dir, f"{base_name}_defects.csv")
    save_csv_report(report, csv_path)

    md_path = os.path.join(out_dir, f"{base_name}_summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(generate_markdown_summary(report))

    # Optional Thumbnails
    if args.save_crops and report.detections:
        crops_dir = os.path.join(out_dir, f"{base_name}_crops")
        os.makedirs(crops_dir, exist_ok=True)
        thumbs = visualizer.create_thumbnail_grid(image_path, report)
        for det, crop_img in thumbs:
            cpath = os.path.join(crops_dir, f"defect_{det.id}_{det.class_name.replace(' ', '_')}_{det.severity.level}.jpg")
            cv2.imwrite(cpath, crop_img)
        print(f"    - Extracted {len(thumbs)} defect crops to: {crops_dir}")

    # Print summary table
    if report.detections:
        print("\n    Detections Breakdown:")
        for d in report.detections:
            print(f"      #{d.id:02d} | {d.class_name:<18} | Sev: {d.severity.level:<6} (Score: {d.severity.score:.2f}) | "
                  f"Conf: {d.confidence*100:>3.0f}% | Area: {d.severity.area_pct:>5.2f}%")
    else:
        print("    [i] No road distress detected meeting the confidence threshold.")

    return report


def main():
    args = parse_args()
    print("=" * 70)
    print("  Road Damage Detection and Severity Assessment Pipeline")
    print("=" * 70)

    # Initialize model and visualizer
    print(f"[*] Initializing {args.backend.upper()} detector...")
    detector = RoadDamageDetector(backend=args.backend, conf_threshold=args.conf, iou_threshold=args.iou)
    visualizer = RoadDamageVisualizer(show_hud=not args.no_hud)

    images_to_process = []
    if args.image:
        if not os.path.exists(args.image):
            print(f"[-] Error: Image file '{args.image}' not found.")
            sys.exit(1)
        images_to_process.append(args.image)
    elif args.dir:
        if not os.path.isdir(args.dir):
            print(f"[-] Error: Directory '{args.dir}' not found.")
            sys.exit(1)
        exts = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]
        for ext in exts:
            images_to_process.extend(glob.glob(os.path.join(args.dir, ext)))
        images_to_process = sorted(list(set(images_to_process)))
        if not images_to_process:
            print(f"[-] No images found in '{args.dir}'.")
            sys.exit(1)
        print(f"[*] Found {len(images_to_process)} images to analyze.")

    total_defects = 0
    start_total = time.time()
    for img_path in images_to_process:
        rep = process_single_image(img_path, detector, visualizer, args)
        total_defects += rep.summary.total_defects

    total_time = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"[*] Batch Complete: Processed {len(images_to_process)} images in {total_time:.2f}s "
          f"({total_time/len(images_to_process)*1000:.1f}ms/img avg)")
    print(f"[*] Total Defects Identified: {total_defects}")
    print(f"[*] Results saved to: {os.path.abspath(args.output)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
