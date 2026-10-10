# 🛣️ Road Damage Detection & Severity Assessment System

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/drkanurag/Road-Damage-Detection-and-Severity-Assessment?quickstart=1)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=drkanurag/Road-Damage-Detection-and-Severity-Assessment&branch=main&mainModule=app.py)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/drkanurag/Road-Damage-Detection-and-Severity-Assessment)

A production-ready, lightweight computer vision system for real-time pavement inspection, automated defect localization, classification into 4 standardized damage types, and multi-factor ASTM D6433 severity estimation (**Low**, **Medium**, **High**).

Designed for edge deployment, CPU-only servers, and vehicle inspection dashcams with **sub-50ms inference latency** on standard Intel/AMD CPUs.

---

## 🌐 Direct Access Links (Use the Program Instantly)

Anyone can launch and use the application directly via the links below:

| Access Method | Clickable Link | Description |
|---|---|---|
| **🚀 Run in Browser (Zero Install)** | [**Launch in GitHub Codespaces**](https://codespaces.new/drkanurag/Road-Damage-Detection-and-Severity-Assessment?quickstart=1) | Automatically provisions the environment, starts the microservices server, and opens the Web UI in your browser. |
| **☁️ Streamlit Cloud App** | [**Open / Deploy on Streamlit Cloud**](https://share.streamlit.io/deploy?repository=drkanurag/Road-Damage-Detection-and-Severity-Assessment&branch=main&mainModule=app.py) | 1-click cloud access to the interactive Streamlit Road Damage Analytics Dashboard. |
| **☁️ Render Cloud Web App** | [**Deploy Full Microservices App on Render**](https://render.com/deploy?repo=https://github.com/drkanurag/Road-Damage-Detection-and-Severity-Assessment) | 1-click public cloud hosting for the Cyber-Glassmorphic Web UI & FastAPI Gateway. |
| **💻 Local Web Application** | [**http://localhost:8000**](http://localhost:8000) / [**http://127.0.0.1:8000**](http://127.0.0.1:8000) | Direct link to the main RoadVision AI Web Application when running locally. |
| **📖 Interactive API Swagger UI** | [**http://localhost:8000/docs**](http://localhost:8000/docs) | Live OpenAPI documentation to test `/api/detect` and all microservice endpoints directly in the browser. |
| **📊 Local Streamlit Dashboard** | [**http://localhost:8501**](http://localhost:8501) | Direct link when running `streamlit run app.py`. |
| **📦 Download Program (ZIP)** | [**Download Latest Release ZIP**](https://github.com/drkanurag/Road-Damage-Detection-and-Severity-Assessment/archive/refs/heads/main.zip) | Direct 1-click download of the complete source code and pre-trained ONNX/PyTorch models. |

---

## 🎯 Objectives & Capabilities

| Objective | Capability | Implementation Detail |
|---|---|---|
| **1. Defect Detection** | Detects surface anomalies in pavement imagery | YOLOv8-nano fine-tuned on RDD2022 (Road Damage Dataset) benchmark |
| **2. Defect Localization** | Precise pixel and normalized bounding boxes | `[x1, y1, x2, y2]` coordinates with aspect-ratio preserving letterbox scaling |
| **3. Defect Classification** | Categorizes into 4 standardized distress types | • **Pothole**<br>• **Longitudinal crack**<br>• **Transverse crack**<br>• **Alligator crack** |
| **4. Severity Assessment** | Estimates engineering distress level | **Low**, **Medium**, **High** using ASTM D6433 multi-attribute scoring |
| **5. Road Condition Index** | Computes overall roadway health | Pavement Condition Index (PCI 0–100) and condition category (**Good**, **Fair**, **Poor**, **Critical**) |

---

## 🏗️ Microservices System Architecture

The system follows **Domain-Driven Microservices Architecture** and **12-Factor App** principles, decomposing road inspection into 5 decoupled services with strict Pydantic DTO contracts, Correlation-ID distributed tracing (`X-Correlation-ID`), and resilient circuit-breaker fallback:

| Microservice | Default Port | Bounded Context & Responsibility | Key Endpoints |
|---|---|---|---|
| **API Gateway** (`services.api_gateway`) | `:8000` | Edge routing, pipeline orchestration, circuit breaker, static UI | `POST /api/detect`, `GET /api/health`, `GET /api/services/status` |
| **Detection Service** (`services.detection_service`) | `:8001` | YOLOv8 ONNX / PyTorch inference, letterbox scaling & NMS | `POST /v1/detect`, `GET /health` |
| **Severity Service** (`services.severity_service`) | `:8002` | Stateless ASTM D6433 severity grading & PCI (0–100) scoring | `POST /v1/assess`, `GET /v1/standards`, `GET /health` |
| **Visualization Service** (`services.visualization_service`) | `:8003` | Bounding box overlays, Executive HUD & defect crop extraction | `POST /v1/render`, `GET /health` |
| **Reporting Service** (`services.reporting_service`) | `:8004` | Multi-format exports (JSON, CSV, Markdown) & inspection audit store | `POST /v1/reports/generate`, `GET /v1/reports/history`, `GET /health` |

```mermaid
flowchart TD
    Client["Web UI / REST Client / Dashcam"] --> GW["API Gateway & Orchestrator (:8000)<br>X-Correlation-ID & Circuit Breaker"]
    
    GW -->|"1. POST /v1/detect"| S1["Detection Microservice (:8001)<br>YOLOv8 ONNX / PyTorch Engine"]
    GW -->|"2. POST /v1/assess"| S2["Severity Microservice (:8002)<br>ASTM D6433 & PCI Health Engine"]
    GW -->|"3. POST /v1/render"| S3["Visualization Microservice (:8003)<br>OpenCV HUD & Forensic Thumbnails"]
    GW -->|"4. POST /v1/reports/generate"| S4["Reporting Microservice (:8004)<br>JSON / CSV / Markdown & Audit Log"]
```

---

## 📊 Defect Classification & Severity Standards (ASTM D6433)

Our severity engine directly implements the international **ASTM D6433 (Standard Practice for Roads and Parking Lots Pavement Condition Index Surveys)**:

### 1. 🕳️ Pothole
- **Definition**: Bowl-shaped depressions in the asphalt surface caused by structural moisture erosion and cyclic wheel load failure.
- **Severity Criteria**:
  - **Low**: Shallow depression, relative area $< 0.4\%$, depth $< 25\text{ mm}$. Minor ride disturbance.
  - **Medium**: Moderate area ($0.4\% - 1.5\%$), depth $25 - 50\text{ mm}$. Noticeable vehicle jolt; requires scheduled patch.
  - **High**: Deep depression, area $> 1.5\%$, depth $> 50\text{ mm}$, sharp vertical rim edges. Immediate vehicle tire/suspension hazard.

### 2. 📏 Longitudinal Crack
- **Definition**: Cracks running parallel to the pavement centerline or vehicle travel direction.
- **Severity Criteria**:
  - **Low**: Hairline crack, width $< 6\text{ mm}$, length span $< 14\%$, intact joint.
  - **Medium**: Crack width $6 - 20\text{ mm}$, span $14\% - 32\%$, minor edge spalling along wheel path.
  - **High**: Wide continuous crack $> 20\text{ mm}$, span $> 32\%$, aggregate loss and base settlement risk.

### 3. 🛣️ Transverse Crack
- **Definition**: Cracks running perpendicular to the pavement centerline (thermal contraction and joint reflection).
- **Severity Criteria**:
  - **Low**: Narrow hairline $< 6\text{ mm}$, spanning partial lane with smooth wheel transition.
  - **Medium**: Width $6 - 20\text{ mm}$, partial or full lane span, slight chipping.
  - **High**: Major fracture $> 20\text{ mm}$, full lane span with severe edge spalling and perceptible bump to traffic.

### 4. 🐊 Alligator (Fatigue) Crack
- **Definition**: Interconnected fatigue cracks forming a series of small, polygonal blocks resembling chicken wire or alligator skin.
- **Severity Criteria**:
  - **Low**: Fine parallel hairline cracks with very few interconnecting branches, no spalling.
  - **Medium**: Well-defined interconnected chicken-wire pattern, area $0.8\% - 2.2\%$, minor edge spalling.
  - **High**: Severely spalled, loose polygonal block network, edge density $> 0.28$, surface disintegration indicating sub-base fatigue failure.

---

## 🧮 Mathematical Severity Formulation

For each detected defect $i$ of class $c$:

$$\text{DSI}_i = w_{\text{area}} \cdot f_{\text{area}}(A_{\text{rel}}) + w_{\text{extent}} \cdot f_{\text{dim}}(L_{\text{norm}}) + w_{\text{texture}} \cdot \text{EdgeDensity} + w_{\text{depth}} \cdot \Delta I$$

Where:
- $A_{\text{rel}} = \frac{W_{\text{box}} \times H_{\text{box}}}{W_{\text{img}} \times H_{\text{img}}}$ is the relative road surface area.
- $L_{\text{norm}} = \frac{\max(W_{\text{box}}, H_{\text{box}})}{\max(W_{\text{img}}, H_{\text{img}})}$ is the normalized primary dimension.
- $\Delta I = \bar{I}_{\text{surrounding}} - \bar{I}_{\text{defect}}$ captures shadow depth in depressions.
- **Thresholds**:
  - $\text{DSI} < 0.35 \implies \mathbf{Low}$ (Green `#22c55e`)
  - $0.35 \le \text{DSI} < 0.65 \implies \mathbf{Medium}$ (Amber `#f59e0b`)
  - $\text{DSI} \ge 0.65 \implies \mathbf{High}$ (Red `#ef4444`)

### Overall Pavement Condition Index (PCI)
$$\text{PCI} = \max\left(0, 100 - \sum_{i} \text{Deduct}(c_i, \text{Severity}_i)\right)$$

- **85 – 100**: Good (Routine inspection cycle)
- **65 – 84**: Fair (Preventative maintenance within 60–90 days)
- **40 – 64**: Poor (Corrective rehabilitation within 30 days)
- **0 – 39**: Critical (Immediate emergency hazard intervention)

---

## 📁 Repository Structure

```
├── models/
│   ├── rdd2022_india_trained.onnx    # Fine-tuned ONNX model (~40ms CPU)
│   ├── rdd2022_india_trained.pt      # Fine-tuned PyTorch weights
│   ├── rdd2022_yolov8n.onnx          # Base RDD2022 ONNX model
│   └── rdd2022_yolov8n.pt            # Base RDD2022 PyTorch weights
├── services/                         # Domain-Driven Microservices Layer
│   ├── common/                       # Shared schemas (DTOs), config, tracing middleware & client
│   ├── detection_service/            # Port 8001: YOLOv8 Inference & NMS Microservice
│   ├── severity_service/             # Port 8002: ASTM D6433 & PCI Microservice
│   ├── visualization_service/        # Port 8003: HUD & Thumbnail Rendering Microservice
│   ├── reporting_service/            # Port 8004: JSON/CSV/Markdown & Audit Microservice
│   └── api_gateway/                  # Port 8000: API Gateway & Pipeline Orchestrator
├── road_damage_vision/               # Core Computer Vision & Severity Domain Library
│   ├── __init__.py
│   ├── config.py
│   ├── detector.py
│   ├── severity.py
│   ├── visualizer.py
│   └── report.py
├── samples/                          # Curated benchmark test images
├── tests/
│   ├── test_pipeline.py              # Core domain unit tests (8 test cases)
│   └── test_microservices.py         # Microservices & API Gateway test suite (4 test cases)
├── static/                           # Next-Gen Cyber-Glassmorphic Frontend
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── run_microservices.py              # Multi-process cluster launcher (ports 8000-8004)
├── docker-compose.yml                # Containerized 5-service deployment definition
├── Dockerfile                        # Lightweight container image definition
├── web_server.py                     # Single-command API Gateway entrypoint
├── app.py                            # Alternative Streamlit dashboard
├── cli.py                            # Command-line interface for single/batch processing
├── requirements.txt                  # Pinned Python dependencies
└── README.md                         # Comprehensive documentation
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup

Ensure Python 3.10+ is available:

```bash
# Activate existing virtual environment
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate (Linux/macOS)

# Install dependencies if starting fresh
pip install -r requirements.txt
```

---

### 2. Launch the Microservices Application

#### Option A: Single-Command Gateway Mode (Recommended for Local Dev)
Runs the API Gateway and orchestrates all 4 microservices via the built-in ASGI Microservice Bus:
```bash
python web_server.py
```

#### Option B: Distributed Multi-Process Cluster (Ports 8000–8004)
Spawns each microservice in its own dedicated OS process on ports `8001`–`8004` with the API Gateway on `8000`:
```bash
python run_microservices.py
```

#### Option C: Containerized Docker Compose Deployment
```bash
docker compose up --build
```

👉 **Access in your browser at**: [**http://127.0.0.1:8000**](http://127.0.0.1:8000) (or [**http://localhost:8000**](http://localhost:8000))  
👉 **Interactive OpenAPI Docs**: [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

**Key Website Features:**
- **Cinematic Cyber-Glassmorphic UI**: Dynamic particle background, holographic glass panels, and glowing laser scanner animation.
- **Photo Upload & Camera**: Drag & drop road photos, clipboard paste (`Ctrl+V`), live device camera, or 1-click curated test showcase.
- **Interactive Before/After Split Slider**: Drag a glowing neon divider to peel back the raw road surface and reveal AI defect detections underneath.
- **2.5x Forensic Inspection Loupe**: Move your cursor over the road to magnify crack spalling and pothole depth with tactical crosshairs.
- **Procedural Sound FX Engine**: Futuristic synthesizer audio feedback for scans, button clicks, and completion chimes via Web Audio API.
- **Radial PCI Health Gauge**: Animated speedometer dial tracking Pavement Condition Index (0–100) with dynamic color transitions.
- **Forensic Defect Cards & Filters**: Individual defect zoom thumbnails, animated severity progress bars, and ASTM D6433 rationale.
- **1-Click Export Center**: Download annotated images (JPG), diagnostic reports (JSON), GIS tables (CSV), or print an official inspection certificate.

---

### 3. Alternative Streamlit Analytics Dashboard

An alternative Streamlit dashboard is also provided (accessible at [**http://localhost:8501**](http://localhost:8501) or via [**Streamlit Cloud**](https://share.streamlit.io/deploy?repository=drkanurag/Road-Damage-Detection-and-Severity-Assessment&branch=main&mainModule=app.py)):

```bash
streamlit run app.py
```

---

### 4. Command-Line Interface (CLI)

#### Analyze a Single Image:
```bash
python cli.py --image samples/pothole_sample.jpg --output results/ --save-crops
```

#### Batch Analyze an Entire Directory:
```bash
python cli.py --dir samples/ --conf 0.25 --backend onnx --output results/
```

**CLI Output Example:**
```text
======================================================================
  Road Damage Detection and Severity Assessment Pipeline
======================================================================
[*] Initializing ONNX detector...

[+] Analyzing: samples/pothole_sample.jpg
    - Resolution: 570x570
    - Latency: 34.0ms (Engine: ONNX (CPU-optimized))
    - Health Index: 33/100 [Critical]
    - Total Defects: 4 (High: 2, Med: 1, Low: 1)
    - Annotated image saved: results/pothole_sample_annotated.jpg
    - Extracted 4 defect crops to: results/pothole_sample_crops

    Detections Breakdown:
      #01 | Transverse crack   | Sev: High   (Score: 0.84) | Conf:  57% | Area:  2.35%
      #02 | Pothole            | Sev: High   (Score: 0.57) | Conf:  56% | Area:  1.44%
      #03 | Pothole            | Sev: Medium (Score: 0.56) | Conf:  30% | Area:  1.35%
      #04 | Pothole            | Sev: Low    (Score: 0.12) | Conf:  66% | Area:  0.20%
```

---

### 4. Python SDK Usage

```python
from road_damage_vision import RoadDamageDetector, RoadDamageVisualizer, save_json_report
import cv2

# Initialize detector (ONNX backend for ultra-fast CPU inference)
detector = RoadDamageDetector(backend="onnx", conf_threshold=0.25)
visualizer = RoadDamageVisualizer(show_hud=True)

# Run prediction & severity estimation
report = detector.predict("samples/multi_defect_pavement.jpg")

print(f"Pavement Condition Index: {report.summary.health_score}/100 ({report.summary.status})")
print(f"Total Defects Found: {report.summary.total_defects}")

for det in report.detections:
    print(f"#{det.id}: {det.class_name} | Severity: {det.severity.level} ({det.severity.score:.2f})")
    print(f"    Bounding Box: {det.bbox} | Confidence: {det.confidence:.2%}")
    print(f"    Rationale: {det.severity.rationale}")
    print(f"    Action: {det.severity.recommended_action}")

# Draw and save annotated inspection image
annotated = visualizer.draw("samples/multi_defect_pavement.jpg", report)
cv2.imwrite("annotated_road.jpg", annotated)

# Export structured report
save_json_report(report, "inspection_report.json")
```

---

### 5. Running the Test Suite

Execute the unit test suite:

```bash
python -m unittest tests/test_pipeline.py
```

All 8 tests verify:
- Class catalog presence (Pothole, Longitudinal, Transverse, Alligator).
- ONNX and PyTorch inference pipelines.
- Bounding box coordinates and non-maximum suppression.
- ASTM D6433 severity scaling boundary conditions.
- Road Health Index calculations.
- Visualization rendering and thumbnail extraction.
- JSON, CSV, and Markdown report generation.

---

## ⚡ Performance Benchmarks

Tested on standard Intel Core i7 CPU (13th Gen, 0 GPU required):

| Component | Metric | Value |
|---|---|---|
| **Model Size** | Disk / RAM Footprint | **11.7 MB** (ONNX) / **6.25 MB** (PyTorch) |
| **Startup Time** | Initialization Latency | **0.37 seconds** |
| **CPU Latency** | Single Image (640x640) | **35 – 55 ms** |
| **CPU Throughput** | Real-Time Frame Rate | **~20 – 28 FPS** |
| **Defect Classes** | Categories Detected | **4 (Pothole, Longitudinal, Transverse, Alligator)** |
| **Severity Levels** | Distinctions Computed | **3 (Low, Medium, High)** |
