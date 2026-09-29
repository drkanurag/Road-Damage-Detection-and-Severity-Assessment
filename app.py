"""
Interactive Web Application for Road Damage Detection and Severity Assessment.
Built with Streamlit and OpenCV / ONNX Runtime.
"""

import io
import json
import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

from road_damage_vision import (
    RoadDamageDetector,
    RoadDamageVisualizer,
    report_to_dict,
    save_csv_report,
)
from road_damage_vision.config import (
    DEFECT_CLASSES,
    ROAD_STATUS_CRITICAL,
    ROAD_STATUS_FAIR,
    ROAD_STATUS_GOOD,
    ROAD_STATUS_POOR,
    SEVERITY_COLORS_HEX,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
)

# Page configuration
st.set_page_config(
    page_title="Road Damage Detection & Severity Assessment",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .badge-high {
        background-color: #fee2e2;
        color: #dc2626;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-med {
        background-color: #fef3c7;
        color: #d97706;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-low {
        background-color: #dcfce7;
        color: #16a34a;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_detector(backend: str):
    """Caches model instances for fast real-time interaction."""
    return RoadDamageDetector(backend=backend)


def main():
    st.markdown('<div class="main-header">🛣️ Road Damage Detection & Severity Assessment</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Lightweight Computer Vision system for real-time defect localization, '
        'ASTM D6433 severity classification (Low / Medium / High), and pavement health scoring.</div>',
        unsafe_allow_html=True,
    )

    # ------------------ Sidebar Controls ------------------
    st.sidebar.header("⚙️ Model & Detection Settings")

    backend = st.sidebar.selectbox(
        "Inference Engine",
        options=["onnx", "pytorch"],
        index=0,
        help="ONNX Runtime is optimized for lightweight CPU execution (~30-60ms) without GPU requirements.",
    )

    conf_thresh = st.sidebar.slider(
        "Confidence Threshold",
        min_value=0.10,
        max_value=0.90,
        value=0.25,
        step=0.05,
        help="Minimum confidence score required to confirm a defect.",
    )

    iou_thresh = st.sidebar.slider(
        "NMS IoU Threshold",
        min_value=0.10,
        max_value=0.80,
        value=0.45,
        step=0.05,
        help="Intersection-over-Union threshold for Non-Maximum Suppression overlap removal.",
    )

    st.sidebar.markdown("---")
    st.sidebar.header("🎨 Display Options")
    show_hud = st.sidebar.checkbox("Executive HUD Banner", value=True)
    show_badges = st.sidebar.checkbox("Severity Badges", value=True)
    show_conf = st.sidebar.checkbox("Confidence Scores", value=True)

    st.sidebar.markdown("---")
    st.sidebar.header("📂 Road Image Source")

    sample_options = {
        "🕳️ Potholes & Transverse Fractures": "samples/pothole_sample.jpg",
        "🐊 Alligator (Fatigue) Cracks": "samples/alligator_crack_sample.jpg",
        "📏 Longitudinal Cracking": "samples/longitudinal_crack_sample.jpg",
        "⚠️ Multi-Defect Roadway": "samples/multi_defect_pavement.jpg",
        "🛣️ Transverse & Longitudinal Joints": "samples/transverse_longitudinal_crack.jpg",
        "📸 Upload Custom Image": None,
    }

    selected_source = st.sidebar.selectbox("Select Test Image", list(sample_options.keys()))

    input_image = None
    source_name = selected_source

    if selected_source == "📸 Upload Custom Image":
        uploaded_file = st.sidebar.file_uploader(
            "Upload Road Image", type=["jpg", "jpeg", "png", "webp", "bmp"]
        )
        if uploaded_file is not None:
            input_image = Image.open(uploaded_file).convert("RGB")
            source_name = uploaded_file.name
    else:
        sample_path = sample_options[selected_source]
        if sample_path and os.path.exists(sample_path):
            input_image = Image.open(sample_path).convert("RGB")
            source_name = os.path.basename(sample_path)

    if input_image is None:
        st.info("👈 Please select a sample road image or upload your own from the sidebar to begin analysis.")
        return

    # ------------------ Detection & Assessment ------------------
    try:
        detector = load_detector(backend=backend)
    except Exception as e:
        st.error(f"Failed to load detector with backend '{backend}': {e}")
        return

    visualizer = RoadDamageVisualizer(
        show_hud=show_hud,
        show_severity_badge=show_badges,
        show_confidence=show_conf,
    )

    with st.spinner("Analyzing pavement surface and computing severity metrics..."):
        report = detector.predict(
            input_image,
            conf_threshold=conf_thresh,
            iou_threshold=iou_thresh,
        )
        report.source_info = source_name
        annotated_bgr = visualizer.draw(input_image, report)
        annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)

    # ------------------ Top KPI Metrics ------------------
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

    # Health score card styling
    status = report.summary.status
    if status == ROAD_STATUS_GOOD:
        status_color = "#22c55e"
    elif status == ROAD_STATUS_FAIR:
        status_color = "#f59e0b"
    elif status == ROAD_STATUS_POOR:
        status_color = "#f97316"
    else:
        status_color = "#ef4444"

    with col_kpi1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="color: #64748b; font-size: 0.9rem; font-weight: 600;">PCI HEALTH SCORE</div>
                <div class="metric-val" style="color: {status_color};">{report.summary.health_score:.0f} <span style="font-size: 1rem; color: #94a3b8;">/ 100</span></div>
                <div style="font-size: 0.85rem; font-weight: 600; color: {status_color};">Status: {status.upper()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_kpi2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="color: #64748b; font-size: 0.9rem; font-weight: 600;">TOTAL DEFECTS</div>
                <div class="metric-val" style="color: #1e293b;">{report.summary.total_defects}</div>
                <div style="font-size: 0.85rem; color: #64748b;">
                    High: {report.summary.severity_counts.get(SEVERITY_HIGH, 0)} | 
                    Med: {report.summary.severity_counts.get(SEVERITY_MEDIUM, 0)} | 
                    Low: {report.summary.severity_counts.get(SEVERITY_LOW, 0)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_kpi3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="color: #64748b; font-size: 0.9rem; font-weight: 600;">CRITICAL DISTRESS</div>
                <div class="metric-val" style="color: #dc2626;">{report.summary.critical_defects_count}</div>
                <div style="font-size: 0.85rem; color: #64748b;">Requires immediate intervention</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_kpi4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div style="color: #64748b; font-size: 0.9rem; font-weight: 600;">INFERENCE SPEED</div>
                <div class="metric-val" style="color: #0284c7;">{report.inference_time_ms:.1f} <span style="font-size: 1rem; color: #94a3b8;">ms</span></div>
                <div style="font-size: 0.85rem; color: #64748b;">{report.backend_used}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ Visual Inspection Tabs ------------------
    tab_view, tab_crops, tab_analytics, tab_actions = st.tabs(
        ["🖼️ Inspection Imagery", "🔍 Defect Crop Gallery", "📊 Distress Analytics", "🛠️ Action Plan & Export"]
    )

    with tab_view:
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.subheader("Original Pavement Surface")
            st.image(input_image, use_container_width=True)

        with col_img2:
            st.subheader("Annotated Detections & Severity")
            st.image(annotated_rgb, use_container_width=True)

    with tab_crops:
        st.subheader("Individual Defect Forensic Analysis")
        if not report.detections:
            st.info("No defects identified to extract.")
        else:
            thumbs = visualizer.create_thumbnail_grid(input_image, report, thumb_size=220)
            cols = st.columns(min(4, max(1, len(thumbs))))
            for idx, (det, thumb_bgr) in enumerate(thumbs):
                thumb_rgb = cv2.cvtColor(thumb_bgr, cv2.COLOR_BGR2RGB)
                col = cols[idx % len(cols)]
                with col:
                    st.image(thumb_rgb, use_container_width=True)
                    s_color = SEVERITY_COLORS_HEX.get(det.severity.level, "#10b981")
                    st.markdown(
                        f"""
                        **#{det.id} {det.class_name}**  
                        Severity: <span style="color:{s_color}; font-weight:700;">{det.severity.level}</span> ({det.severity.score:.2f})  
                        Conf: `{det.confidence*100:.0f}%` | Area: `{det.severity.area_pct:.2f}%`  
                        <small style="color:#64748b;">{det.severity.rationale}</small>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.divider()

    with tab_analytics:
        st.subheader("Distress Distribution & Breakdown")
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.write("##### Defect Category Distribution")
            cls_data = report.summary.class_counts
            if cls_data:
                df_cls = pd.DataFrame(list(cls_data.items()), columns=["Category", "Count"]).set_index("Category")
                st.bar_chart(df_cls, color="#3b82f6")
            else:
                st.write("No defect categories detected.")

        with col_chart2:
            st.write("##### Severity Level Breakdown")
            sev_data = report.summary.severity_counts
            df_sev = pd.DataFrame(list(sev_data.items()), columns=["Severity", "Count"]).set_index("Severity")
            st.bar_chart(df_sev, color="#f97316")

    with tab_actions:
        st.subheader("Recommended Maintenance Action Items")
        if report.summary.action_items:
            for item in report.summary.action_items:
                st.markdown(f"- ⚠️ **{item}**")
        else:
            st.success("✅ Pavement in good condition. Standard routine inspection cycle recommended.")

        st.markdown("---")
        st.subheader("Detailed Defects Log")

        if report.detections:
            table_data = []
            for d in report.detections:
                table_data.append({
                    "ID": d.id,
                    "Category": d.class_name,
                    "Severity Level": d.severity.level,
                    "Severity Score": d.severity.score,
                    "Confidence": f"{d.confidence*100:.1f}%",
                    "Relative Area": f"{d.severity.area_pct:.2f}%",
                    "Aspect Ratio": d.severity.aspect_ratio,
                    "Box (x1, y1, x2, y2)": f"({d.bbox[0]:.0f}, {d.bbox[1]:.0f}, {d.bbox[2]:.0f}, {d.bbox[3]:.0f})",
                    "Recommended Action": d.severity.recommended_action,
                })
            df_table = pd.DataFrame(table_data)
            st.dataframe(df_table, use_container_width=True, hide_index=True)

            # Export Downloads
            st.markdown("##### 📥 Export Reports")
            col_d1, col_d2, col_d3 = st.columns(3)

            # Download annotated image
            is_success, buffer = cv2.imencode(".jpg", annotated_bgr)
            if is_success:
                with col_d1:
                    st.download_button(
                        label="Download Annotated Image (JPG)",
                        data=buffer.tobytes(),
                        file_name=f"{source_name}_annotated.jpg",
                        mime="image/jpeg",
                    )

            # Download JSON report
            report_dict = report_to_dict(report)
            json_str = json.dumps(report_dict, indent=2)
            with col_d2:
                st.download_button(
                    label="Download Full JSON Report",
                    data=json_str,
                    file_name=f"{source_name}_report.json",
                    mime="application/json",
                )

            # Download CSV summary
            csv_buffer = io.StringIO()
            df_table.to_csv(csv_buffer, index=False)
            with col_d3:
                st.download_button(
                    label="Download CSV Defects Table",
                    data=csv_buffer.getvalue(),
                    file_name=f"{source_name}_defects.csv",
                    mime="text/csv",
                )


if __name__ == "__main__":
    main()
