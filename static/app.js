/**
 * RoadVision AI - Frontend Application & Interactive Engine
 * Handles particle canvas, Web Audio synth, split slider, loupe magnifier,
 * real-time inference API, and forensic defect inspection.
 */

// ==========================================================================
// 1. Web Audio Procedural Sound Synthesizer
// ==========================================================================
class SoundFX {
  constructor() {
    this.enabled = true;
    this.ctx = null;
    const saved = localStorage.getItem("roadvision_sound");
    if (saved !== null) {
      this.enabled = saved === "true";
    }
  }

  _init() {
    if (!this.ctx && typeof AudioContext !== "undefined") {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume();
    }
  }

  toggle() {
    this.enabled = !this.enabled;
    localStorage.setItem("roadvision_sound", this.enabled.toString());
    return this.enabled;
  }

  playClick() {
    if (!this.enabled) return;
    try {
      this._init();
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(850, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(320, this.ctx.currentTime + 0.04);
      gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.04);
    } catch (_) {}
  }

  playScan() {
    if (!this.enabled) return;
    try {
      this._init();
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(240, this.ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(680, this.ctx.currentTime + 0.25);
      gain.gain.setValueAtTime(0.02, this.ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 0.25);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.25);
    } catch (_) {}
  }

  playSuccess() {
    if (!this.enabled) return;
    try {
      this._init();
      const now = this.ctx.currentTime;
      [523.25, 659.25, 783.99, 1046.5].forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, now + idx * 0.06);
        gain.gain.setValueAtTime(0.04, now + idx * 0.06);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.06 + 0.2);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now + idx * 0.06);
        osc.stop(now + idx * 0.06 + 0.2);
      });
    } catch (_) {}
  }
}

const sfx = new SoundFX();

// ==========================================================================
// 2. Interactive Particle Network Background
// ==========================================================================
function initParticleBackground() {
  const canvas = document.getElementById("bg-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener("resize", () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const numParticles = Math.min(60, Math.floor(width / 24));
  const particles = [];

  for (let i = 0; i < numParticles; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      radius: Math.random() * 1.6 + 0.8,
    });
  }

  let mouseX = -1000;
  let mouseY = -1000;
  window.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function render() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      // Draw particle
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(56, 189, 248, 0.4)";
      ctx.fill();

      // Connect near particles
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(56, 189, 248, ${0.15 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }

      // Mouse influence
      const mdx = p.x - mouseX;
      const mdy = p.y - mouseY;
      const mdist = Math.sqrt(mdx * mdx + mdy * mdy);
      if (mdist < 140) {
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(mouseX, mouseY);
        ctx.strokeStyle = `rgba(14, 165, 233, ${0.25 * (1 - mdist / 140)})`;
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }
    }

    requestAnimationFrame(render);
  }

  render();
}

// ==========================================================================
// 3. Interactive Split Slider Engine
// ==========================================================================
class SplitSlider {
  constructor(containerId, handleId, overlayId) {
    this.container = document.getElementById(containerId);
    this.handle = document.getElementById(handleId);
    this.overlay = document.getElementById(overlayId);
    this.isDragging = false;
    this.position = 50; // percentage

    if (!this.container || !this.handle || !this.overlay) return;
    this.init();
  }

  init() {
    const startDrag = (e) => {
      this.isDragging = true;
      this.updatePosition(e);
      sfx.playClick();
    };

    const stopDrag = () => {
      this.isDragging = false;
    };

    const onMove = (e) => {
      if (!this.isDragging) return;
      this.updatePosition(e);
    };

    this.container.addEventListener("mousedown", startDrag);
    window.addEventListener("mouseup", stopDrag);
    window.addEventListener("mousemove", onMove);

    this.container.addEventListener("touchstart", (e) => startDrag(e.touches[0]));
    window.addEventListener("touchend", stopDrag);
    window.addEventListener("touchmove", (e) => {
      if (this.isDragging) {
        e.preventDefault();
        onMove(e.touches[0]);
      }
    }, { passive: false });
  }

  updatePosition(e) {
    const rect = this.container.getBoundingClientRect();
    const x = e.clientX - rect.left;
    let pct = (x / rect.width) * 100;
    pct = Math.max(0, Math.min(100, pct));
    this.position = pct;

    this.handle.style.left = `${pct}%`;
    this.overlay.style.width = `${pct}%`;
  }

  reset() {
    this.position = 50;
    if (this.handle) this.handle.style.left = "50%";
    if (this.overlay) this.overlay.style.width = "50%";
  }
}

// ==========================================================================
// 4. Inspection Loupe (2.5x Magnifier)
// ==========================================================================
class InspectionLoupe {
  constructor(wrapperId, magnifierId, targetImgId) {
    this.wrapper = document.getElementById(wrapperId);
    this.magnifier = document.getElementById(magnifierId);
    this.targetImg = document.getElementById(targetImgId);
    this.enabled = true;
    this.zoom = 2.5;

    if (!this.wrapper || !this.magnifier || !this.targetImg) return;
    this.init();
  }

  init() {
    this.wrapper.addEventListener("mousemove", (e) => this.onMove(e));
    this.wrapper.addEventListener("mouseleave", () => this.hide());
  }

  onMove(e) {
    if (!this.enabled || !this.targetImg.src) return;

    const rect = this.wrapper.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (x < 0 || y < 0 || x > rect.width || y > rect.height) {
      this.hide();
      return;
    }

    this.magnifier.style.display = "block";
    this.magnifier.style.left = `${x - this.magnifier.offsetWidth / 2}px`;
    this.magnifier.style.top = `${y - this.magnifier.offsetHeight / 2}px`;

    this.magnifier.style.backgroundImage = `url('${this.targetImg.src}')`;
    this.magnifier.style.backgroundSize = `${rect.width * this.zoom}px ${rect.height * this.zoom}px`;

    const bgX = -x * this.zoom + this.magnifier.offsetWidth / 2;
    const bgY = -y * this.zoom + this.magnifier.offsetHeight / 2;
    this.magnifier.style.backgroundPosition = `${bgX}px ${bgY}px`;
  }

  hide() {
    if (this.magnifier) this.magnifier.style.display = "none";
  }
}

// ==========================================================================
// 5. Main Application Orchestrator
// ==========================================================================
class RoadVisionApp {
  constructor() {
    this.currentData = null;
    this.activeFilter = "all";
    this.splitSlider = null;
    this.loupe = null;
    this.stream = null;

    this.initElements();
    this.bindEvents();
    this.loadSamples();
    this.checkHealth();
  }

  initElements() {
    this.dropZone = document.getElementById("drop-zone");
    this.fileInput = document.getElementById("file-input");
    this.webcamBtn = document.getElementById("webcam-btn");
    this.scannerOverlay = document.getElementById("scanner-overlay");
    this.scannerStatusText = document.getElementById("scanner-status-text");

    this.samplesContainer = document.getElementById("samples-container");
    this.resultsSection = document.getElementById("results-section");

    // Slider inputs
    this.confSlider = document.getElementById("conf-slider");
    this.confVal = document.getElementById("conf-val");
    this.iouSlider = document.getElementById("iou-slider");
    this.iouVal = document.getElementById("iou-val");

    // Toggles
    this.toggleHud = document.getElementById("toggle-hud");
    this.toggleBadges = document.getElementById("toggle-badges");
    this.toggleConf = document.getElementById("toggle-conf");
    this.soundBtn = document.getElementById("sound-toggle-btn");

    // Imagery elements
    this.imgRaw = document.getElementById("img-raw");
    this.imgAnnotated = document.getElementById("img-annotated");
    this.sideRawImg = document.getElementById("side-raw-img");
    this.sideAnnotatedImg = document.getElementById("side-annotated-img");
    this.singleAnnotatedImg = document.getElementById("single-annotated-img");

    // Containers
    this.defectsContainer = document.getElementById("defects-container");
    this.actionItemsContainer = document.getElementById("action-items-container");
    this.classChartBars = document.getElementById("class-chart-bars");

    // KPIs
    this.kpiPciVal = document.getElementById("kpi-pci-val");
    this.gaugeCircle = document.getElementById("gauge-circle");
    this.kpiStatusBadge = document.getElementById("kpi-status-badge");
    this.kpiTotalDefects = document.getElementById("kpi-total-defects");
    this.kpiCriticalDefects = document.getElementById("kpi-critical-defects");
    this.kpiLatency = document.getElementById("kpi-latency");
    this.kpiFps = document.getElementById("kpi-fps");

    // Filters
    this.filterAllCount = document.getElementById("filter-all-count");
    this.filterHighCount = document.getElementById("filter-high-count");
    this.filterMedCount = document.getElementById("filter-med-count");
    this.filterLowCount = document.getElementById("filter-low-count");

    // Camera modal
    this.cameraModal = document.getElementById("camera-modal");
    this.webcamVideo = document.getElementById("webcam-video");
    this.cameraCloseBtn = document.getElementById("camera-close-btn");
    this.snapBtn = document.getElementById("snap-btn");

    // Stage components
    this.splitSlider = new SplitSlider("split-wrapper", "split-handle", "split-overlay");
    this.loupe = new InspectionLoupe("split-wrapper", "magnifier", "img-annotated");
  }

  bindEvents() {
    // Sound FX button toggle
    if (this.soundBtn) {
      this.soundBtn.addEventListener("click", () => {
        const state = sfx.toggle();
        this.soundBtn.querySelector(".sound-icon-on").style.display = state ? "block" : "none";
        this.soundBtn.querySelector(".sound-icon-off").style.display = state ? "none" : "block";
        sfx.playClick();
      });
    }

    // Sliders
    this.confSlider.addEventListener("input", (e) => {
      this.confVal.textContent = `${e.target.value}%`;
      sfx.playClick();
    });
    this.iouSlider.addEventListener("input", (e) => {
      this.iouVal.textContent = `${e.target.value}%`;
      sfx.playClick();
    });

    // File Drag & Drop
    ["dragenter", "dragover"].forEach((event) => {
      this.dropZone.addEventListener(event, (e) => {
        e.preventDefault();
        this.dropZone.classList.add("drag-over");
      });
    });

    ["dragleave", "drop"].forEach((event) => {
      this.dropZone.addEventListener(event, (e) => {
        e.preventDefault();
        this.dropZone.classList.remove("drag-over");
      });
    });

    this.dropZone.addEventListener("drop", (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0 && files[0].type.startsWith("image/")) {
        this.analyzeFile(files[0]);
      }
    });

    this.fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        this.analyzeFile(e.target.files[0]);
      }
    });

    // Global Paste (Ctrl + V)
    window.addEventListener("paste", (e) => {
      const items = (e.clipboardData || e.originalEvent.clipboardData).items;
      for (const item of items) {
        if (item.type.indexOf("image") !== -1) {
          const blob = item.getAsFile();
          this.analyzeFile(blob);
          break;
        }
      }
    });

    // Stage View Mode Tabs
    document.querySelectorAll(".stage-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".stage-tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        sfx.playClick();

        const mode = tab.dataset.mode;
        document.getElementById("split-view").style.display = mode === "split" ? "block" : "none";
        document.getElementById("side-view").style.display = mode === "side" ? "grid" : "none";
        document.getElementById("single-view").style.display = mode === "annotated" ? "block" : "none";
      });
    });

    // Loupe toggle
    const loupeToggle = document.getElementById("loupe-toggle");
    if (loupeToggle) {
      loupeToggle.addEventListener("change", (e) => {
        this.loupe.enabled = e.target.checked;
        if (!e.target.checked) this.loupe.hide();
      });
    }

    // Filter Pills
    document.querySelectorAll(".filter-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        this.activeFilter = btn.dataset.filter;
        sfx.playClick();
        this.renderDefectCards();
      });
    });

    // Export Buttons
    document.getElementById("btn-export-json")?.addEventListener("click", () => this.exportJSON());
    document.getElementById("btn-export-csv")?.addEventListener("click", () => this.exportCSV());
    document.getElementById("btn-export-print")?.addEventListener("click", () => window.print());
    document.getElementById("download-annotated-btn")?.addEventListener("click", () => this.downloadAnnotated());

    // Webcam Modal
    this.webcamBtn?.addEventListener("click", () => this.openWebcam());
    this.cameraCloseBtn?.addEventListener("click", () => this.closeWebcam());
    this.snapBtn?.addEventListener("click", () => this.snapWebcam());
  }

  async checkHealth() {
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      if (data.status === "healthy") {
        document.getElementById("engine-status").textContent = "ONNX CPU ENGINE READY (ACTIVE)";
      }
    } catch (_) {}
  }

  async loadSamples() {
    try {
      const res = await fetch("/api/samples");
      const data = await res.json();
      this.samplesContainer.innerHTML = "";

      data.samples.forEach((sample, idx) => {
        const tile = document.createElement("div");
        tile.className = `sample-tile ${idx === 0 ? "active" : ""}`;
        tile.innerHTML = `
          <div class="sample-thumb-wrap">
            <img class="sample-thumb" src="${sample.url}" alt="${sample.title}" loading="lazy">
          </div>
          <span class="sample-name">${sample.title}</span>
        `;
        tile.addEventListener("click", () => {
          document.querySelectorAll(".sample-tile").forEach((t) => t.classList.remove("active"));
          tile.classList.add("active");
          this.analyzeSample(sample.id);
        });
        this.samplesContainer.appendChild(tile);
      });

      // Auto-trigger analysis on the first sample for an instant live showcase
      if (data.samples.length > 0) {
        this.analyzeSample(data.samples[0].id);
      }
    } catch (err) {
      console.error("Failed to load samples:", err);
    }
  }

  showScanner(text = "SCANNING ROAD SURFACE...") {
    this.scannerStatusText.textContent = text;
    this.scannerOverlay.style.display = "flex";
    sfx.playScan();
  }

  hideScanner() {
    this.scannerOverlay.style.display = "none";
  }

  async analyzeSample(sampleId) {
    this.showScanner("ANALYZING ROAD SURFACE...");
    const formData = new FormData();
    formData.append("sample_id", sampleId);
    formData.append("conf_threshold", parseFloat(this.confSlider.value) / 100);
    formData.append("iou_threshold", parseFloat(this.iouSlider.value) / 100);
    formData.append("show_hud", this.toggleHud.checked);

    try {
      const res = await fetch("/api/detect", { method: "POST", body: formData });
      const data = await res.json();
      this.handleResults(data);
    } catch (err) {
      alert("Error analyzing sample: " + err);
    } finally {
      this.hideScanner();
    }
  }

  async analyzeFile(file) {
    this.showScanner("PROCESSING IMAGE & DETECTING DEFECTS...");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("conf_threshold", parseFloat(this.confSlider.value) / 100);
    formData.append("iou_threshold", parseFloat(this.iouSlider.value) / 100);
    formData.append("show_hud", this.toggleHud.checked);

    try {
      const res = await fetch("/api/detect", { method: "POST", body: formData });
      const data = await res.json();
      this.handleResults(data);
    } catch (err) {
      alert("Error processing uploaded image: " + err);
    } finally {
      this.hideScanner();
    }
  }

  handleResults(data) {
    if (!data.success) {
      alert("Analysis failed.");
      return;
    }

    this.currentData = data;
    sfx.playSuccess();

    // Reveal Results Section
    this.resultsSection.style.display = "block";
    this.resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

    // Set Images
    this.imgRaw.src = data.images.raw;
    this.imgAnnotated.src = data.images.annotated;
    this.sideRawImg.src = data.images.raw;
    this.sideAnnotatedImg.src = data.images.annotated;
    this.singleAnnotatedImg.src = data.images.annotated;

    this.splitSlider.reset();

    // Populate Top KPIs
    const summary = data.summary;
    const score = summary.health_score;

    this.kpiPciVal.textContent = Math.round(score);
    this.kpiStatusBadge.textContent = summary.status.toUpperCase();

    // Animate Radial Gauge Circle (circumference = 2 * PI * 50 = 314.15)
    const dashoffset = 314 - (score / 100) * 314;
    this.gaugeCircle.style.strokeDashoffset = dashoffset;

    // Shift gauge color based on condition
    let strokeColor = "#10b981"; // Good
    if (score < 40) strokeColor = "#ef4444"; // Critical
    else if (score < 65) strokeColor = "#f97316"; // Poor
    else if (score < 85) strokeColor = "#f59e0b"; // Fair
    this.gaugeCircle.style.stroke = strokeColor;
    this.kpiStatusBadge.style.color = strokeColor;
    this.kpiStatusBadge.style.borderColor = strokeColor;

    this.kpiTotalDefects.textContent = summary.total_defects;
    document.getElementById("count-high").textContent = summary.severity_counts.High || 0;
    document.getElementById("count-med").textContent = summary.severity_counts.Medium || 0;
    document.getElementById("count-low").textContent = summary.severity_counts.Low || 0;

    this.kpiCriticalDefects.textContent = summary.critical_defects_count;
    this.kpiLatency.innerHTML = `${data.metadata.inference_time_ms} <span class="kpi-unit">ms</span>`;
    const fps = (1000 / Math.max(1, data.metadata.inference_time_ms)).toFixed(1);
    this.kpiFps.textContent = `${fps} FPS`;

    // Filter counts
    this.filterAllCount.textContent = data.defects.length;
    this.filterHighCount.textContent = summary.severity_counts.High || 0;
    this.filterMedCount.textContent = summary.severity_counts.Medium || 0;
    this.filterLowCount.textContent = summary.severity_counts.Low || 0;

    // Render Forensic Cards & Actions
    this.renderDefectCards();
    this.renderActionItems();
    this.renderClassChart();
  }

  renderDefectCards() {
    if (!this.currentData) return;
    this.defectsContainer.innerHTML = "";

    const defects = this.currentData.defects.filter((d) => {
      if (this.activeFilter === "all") return true;
      return d.severity.level === this.activeFilter;
    });

    if (defects.length === 0) {
      this.defectsContainer.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--text-subtle);">
          No defects matching filter "${this.activeFilter}".
        </div>
      `;
      return;
    }

    defects.forEach((d) => {
      const card = document.createElement("div");
      card.className = "defect-card";
      card.id = `defect-card-${d.id}`;

      const sev = d.severity;
      const sevClass = `sev-badge-${sev.level.toLowerCase()}`;
      const fillPct = Math.round(sev.score * 100);

      card.innerHTML = `
        <div class="defect-card-thumb-wrap" style="border-color: ${sev.color_hex};">
          <img class="defect-card-thumb" src="${d.crop_base64 || this.currentData.images.raw}" alt="${d.class_name}">
        </div>
        <div class="defect-meta">
          <div class="defect-top-line">
            <div class="defect-title-group">
              <span class="defect-id-tag">#${d.id}</span>
              <span class="defect-class-name">${d.class_name}</span>
            </div>
            <span class="defect-sev-badge ${sevClass}">[${sev.level.toUpperCase()}]</span>
          </div>

          <div class="severity-bar-wrapper">
            <div class="sev-bar-header">
              <span>ASTM Severity Index:</span>
              <span style="color: ${sev.color_hex}; font-weight:700;">${sev.score.toFixed(2)} / 1.00</span>
            </div>
            <div class="sev-bar-track">
              <div class="sev-bar-fill" style="width: ${fillPct}%; background: ${sev.color_hex};"></div>
            </div>
          </div>

          <div class="metrics-chip-row">
            <span class="metric-chip">Area: ${sev.area_pct.toFixed(2)}%</span>
            <span class="metric-chip">Aspect Ratio: ${sev.aspect_ratio}</span>
            <span class="metric-chip">Confidence: ${(d.confidence * 100).toFixed(0)}%</span>
          </div>

          <div class="defect-rationale">${sev.rationale}</div>
          <div class="defect-action-text">🛠️ ${sev.recommended_action}</div>
        </div>
      `;

      card.addEventListener("mouseenter", () => {
        card.classList.add("highlighted");
      });
      card.addEventListener("mouseleave", () => {
        card.classList.remove("highlighted");
      });

      this.defectsContainer.appendChild(card);
    });
  }

  renderActionItems() {
    this.actionItemsContainer.innerHTML = "";
    const items = this.currentData.summary.action_items;

    if (!items || items.length === 0) {
      this.actionItemsContainer.innerHTML = `
        <div class="action-item-pill" style="border-color: rgba(16, 185, 129, 0.4);">
          <span class="action-bullet">✅</span>
          <span class="action-text">Roadway in good condition. Standard annual routine inspection recommended.</span>
        </div>
      `;
      return;
    }

    items.forEach((item) => {
      const div = document.createElement("div");
      div.className = "action-item-pill";
      div.innerHTML = `
        <span class="action-bullet">⚠️</span>
        <span class="action-text"><strong>${item.split(":")[0]}:</strong> ${item.split(":").slice(1).join(":")}</span>
      `;
      this.actionItemsContainer.appendChild(div);
    });
  }

  renderClassChart() {
    this.classChartBars.innerHTML = "";
    const counts = this.currentData.summary.class_counts || {};
    const total = this.currentData.summary.total_defects || 1;

    for (const [cls, count] of Object.entries(counts)) {
      const pct = Math.round((count / total) * 100);
      const row = document.createElement("div");
      row.className = "chart-row";
      row.innerHTML = `
        <span class="chart-label">${cls}</span>
        <div class="chart-track">
          <div class="chart-bar-fill" style="width: ${pct}%;"></div>
        </div>
        <span class="chart-count">${count}</span>
      `;
      this.classChartBars.appendChild(row);
    }
  }

  exportJSON() {
    if (!this.currentData) return;
    const str = JSON.stringify(this.currentData, null, 2);
    const blob = new Blob([str], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `road_inspection_report_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    sfx.playClick();
  }

  exportCSV() {
    if (!this.currentData) return;
    const rows = [
      ["id", "class_name", "confidence", "severity_level", "severity_score", "area_pct", "aspect_ratio", "rationale", "action"],
    ];
    this.currentData.defects.forEach((d) => {
      rows.push([
        d.id,
        `"${d.class_name}"`,
        d.confidence,
        d.severity.level,
        d.severity.score,
        d.severity.area_pct,
        d.severity.aspect_ratio,
        `"${d.severity.rationale.replace(/"/g, '""')}"`,
        `"${d.severity.recommended_action.replace(/"/g, '""')}"`,
      ]);
    });
    const csvContent = rows.map((e) => e.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pavement_defects_log_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    sfx.playClick();
  }

  downloadAnnotated() {
    if (!this.currentData || !this.currentData.images.annotated) return;
    const a = document.createElement("a");
    a.href = this.currentData.images.annotated;
    a.download = `annotated_road_damage_${Date.now()}.jpg`;
    a.click();
    sfx.playClick();
  }

  async openWebcam() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
      });
      this.webcamVideo.srcObject = this.stream;
      this.cameraModal.style.display = "flex";
      sfx.playClick();
    } catch (err) {
      alert("Unable to access camera: " + err.message);
    }
  }

  closeWebcam() {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
    this.cameraModal.style.display = "none";
  }

  snapWebcam() {
    const canvas = document.getElementById("webcam-canvas");
    canvas.width = this.webcamVideo.videoWidth;
    canvas.height = this.webcamVideo.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(this.webcamVideo, 0, 0);

    canvas.toBlob((blob) => {
      this.closeWebcam();
      this.analyzeFile(blob);
    }, "image/jpeg", 0.92);
  }
}

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initParticleBackground();
  window.roadApp = new RoadVisionApp();
});
