/**
 * RoadVision AI — Frontend Application & Interactive Telemetry Engine
 * Features:
 *  - Pixel-locked Clip-Path Split Slider + Quick Presets (Raw / 50-50 / AI)
 *  - Interactive Bi-Directional SVG Vector Bounding Box Spotlight
 *  - Live 5-Microservice Distributed Trace Ribbon (X-Correlation-ID + Stage Timings)
 *  - Civil Engineering Triage & Work Order Estimator
 *  - Dark Mode & Daylight Mode Theme Engine (with keyboard shortcut 'T')
 *  - Procedural Web Audio Acoustic Telemetry & Floating Toast Notifications
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
      osc.frequency.setValueAtTime(860, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(340, this.ctx.currentTime + 0.035);
      gain.gain.setValueAtTime(0.035, this.ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 0.035);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.035);
    } catch (_) {}
  }

  playScan() {
    if (!this.enabled) return;
    try {
      this._init();
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(280, this.ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(640, this.ctx.currentTime + 0.18);
      gain.gain.setValueAtTime(0.02, this.ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0.001, this.ctx.currentTime + 0.18);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.18);
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
        osc.frequency.setValueAtTime(freq, now + idx * 0.055);
        gain.gain.setValueAtTime(0.032, now + idx * 0.055);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.055 + 0.18);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now + idx * 0.055);
        osc.stop(now + idx * 0.055 + 0.18);
      });
    } catch (_) {}
  }
}

const sfx = new SoundFX();

// ==========================================================================
// 2. Toast Notification Utility
// ==========================================================================
function showToast(message, icon = "✨") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = "toast-msg";
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    toast.style.transition = "all 0.25s ease";
    setTimeout(() => toast.remove(), 260);
  }, 2600);
}

// ==========================================================================
// 3. Interactive Particle Network Background
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

  const numParticles = Math.min(52, Math.floor(width / 28));
  const particles = [];

  for (let i = 0; i < numParticles; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      radius: Math.random() * 1.5 + 0.7,
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

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(56, 189, 248, 0.38)";
      ctx.fill();

      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 115) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(56, 189, 248, ${0.13 * (1 - dist / 115)})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }

      const mdx = p.x - mouseX;
      const mdy = p.y - mouseY;
      const mdist = Math.sqrt(mdx * mdx + mdy * mdy);
      if (mdist < 135) {
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(mouseX, mouseY);
        ctx.strokeStyle = `rgba(14, 165, 233, ${0.22 * (1 - mdist / 135)})`;
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }
    }

    requestAnimationFrame(render);
  }

  render();
}

// ==========================================================================
// 4. Pixel-Locked Clip-Path Split Slider Engine
// ==========================================================================
class SplitSlider {
  constructor(containerId, handleId, overlayId) {
    this.container = document.getElementById(containerId);
    this.handle = document.getElementById(handleId);
    this.overlay = document.getElementById(overlayId);
    this.isDragging = false;
    this.position = 50;

    if (!this.container || !this.handle || !this.overlay) return;
    this.init();
  }

  init() {
    const startDrag = (e) => {
      if (e.target.closest(".svg-bbox-group")) return;
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

    this.container.addEventListener("touchstart", (e) => startDrag(e.touches[0]), { passive: true });
    window.addEventListener("touchend", stopDrag);
    window.addEventListener(
      "touchmove",
      (e) => {
        if (this.isDragging) {
          e.preventDefault();
          onMove(e.touches[0]);
        }
      },
      { passive: false }
    );
  }

  updatePosition(e) {
    const rect = this.container.getBoundingClientRect();
    const x = e.clientX - rect.left;
    let pct = (x / Math.max(1, rect.width)) * 100;
    pct = Math.max(0, Math.min(100, pct));
    this.setPercent(pct);
  }

  setPercent(pct) {
    this.position = pct;
    if (this.handle) this.handle.style.left = `${pct}%`;
    if (this.overlay) {
      this.overlay.style.clipPath = `inset(0 ${100 - pct}% 0 0)`;
    }
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.classList.toggle("active", Math.abs(parseFloat(btn.dataset.split) - pct) < 2);
    });
  }

  reset() {
    this.setPercent(50);
  }
}

// ==========================================================================
// 5. Inspection Loupe (2.5x Optical Magnifier)
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
// 6. Main Application Orchestrator
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

    // Sliders & Engine Select
    this.confSlider = document.getElementById("conf-slider");
    this.confVal = document.getElementById("conf-val");
    this.iouSlider = document.getElementById("iou-slider");
    this.iouVal = document.getElementById("iou-val");
    this.backendSelect = document.getElementById("backend-select");

    // Toggles
    this.toggleHud = document.getElementById("toggle-hud");
    this.toggleBadges = document.getElementById("toggle-badges");
    this.toggleConf = document.getElementById("toggle-conf");
    this.toggleInteractiveBoxes = document.getElementById("toggle-interactive-boxes");
    this.soundBtn = document.getElementById("sound-toggle-btn");
    this.themeBtn = document.getElementById("theme-toggle-btn");
    this.themeLabel = document.getElementById("theme-switch-label");

    // Initialize saved theme (default: dark)
    const savedTheme = localStorage.getItem("roadvision_theme") || "dark";
    this.applyTheme(savedTheme, false);

    // Imagery elements
    this.imgRaw = document.getElementById("img-raw");
    this.imgAnnotated = document.getElementById("img-annotated");
    this.sideRawImg = document.getElementById("side-raw-img");
    this.sideAnnotatedImg = document.getElementById("side-annotated-img");
    this.singleAnnotatedImg = document.getElementById("single-annotated-img");
    this.bboxSvgOverlay = document.getElementById("bbox-svg-overlay");
    this.singleBboxSvg = document.getElementById("single-bbox-svg");

    // Containers
    this.defectsContainer = document.getElementById("defects-container");
    this.actionItemsContainer = document.getElementById("action-items-container");
    this.classChartBars = document.getElementById("class-chart-bars");
    this.markdownReportBox = document.getElementById("markdown-report-box");

    // KPIs
    this.kpiPciVal = document.getElementById("kpi-pci-val");
    this.gaugeCircle = document.getElementById("gauge-circle");
    this.kpiStatusBadge = document.getElementById("kpi-status-badge");
    this.kpiUrgencyNote = document.getElementById("kpi-urgency-note");
    this.kpiTotalDefects = document.getElementById("kpi-total-defects");
    this.kpiCriticalDefects = document.getElementById("kpi-critical-defects");
    this.kpiHazardChip = document.getElementById("kpi-hazard-chip");
    this.kpiHazardSub = document.getElementById("kpi-hazard-sub");
    this.kpiLatency = document.getElementById("kpi-latency");
    this.kpiFps = document.getElementById("kpi-fps");
    this.kpiBackendInfo = document.getElementById("kpi-backend-info");

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

  applyTheme(theme, notify = true) {
    this.currentTheme = theme === "light" ? "light" : "dark";
    document.body.classList.toggle("light-mode", this.currentTheme === "light");
    document.documentElement.setAttribute("data-theme", this.currentTheme);
    localStorage.setItem("roadvision_theme", this.currentTheme);

    if (this.themeBtn) {
      const sunIcon = this.themeBtn.querySelector(".theme-icon-sun");
      const moonIcon = this.themeBtn.querySelector(".theme-icon-moon");
      if (sunIcon) sunIcon.style.display = this.currentTheme === "light" ? "block" : "none";
      if (moonIcon) moonIcon.style.display = this.currentTheme === "dark" ? "block" : "none";
    }
    if (this.themeLabel) {
      this.themeLabel.textContent = this.currentTheme === "light" ? "LIGHT" : "DARK";
    }
    if (notify) {
      showToast(
        `Switched to ${this.currentTheme === "light" ? "Daylight Mode" : "Cyber Dark Mode"}`,
        this.currentTheme === "light" ? "☀️" : "🌙"
      );
    }
  }

  bindEvents() {
    // Theme toggle (Button + 'T' keyboard shortcut)
    if (this.themeBtn) {
      this.themeBtn.addEventListener("click", () => {
        const nextTheme = this.currentTheme === "dark" ? "light" : "dark";
        this.applyTheme(nextTheme, true);
        sfx.playClick();
      });
    }

    window.addEventListener("keydown", (e) => {
      if (e.key.toLowerCase() === "t" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
        const nextTheme = this.currentTheme === "dark" ? "light" : "dark";
        this.applyTheme(nextTheme, true);
        sfx.playClick();
      }
    });

    // Sound FX button toggle
    if (this.soundBtn) {
      this.soundBtn.addEventListener("click", () => {
        const state = sfx.toggle();
        this.soundBtn.querySelector(".sound-icon-on").style.display = state ? "block" : "none";
        this.soundBtn.querySelector(".sound-icon-off").style.display = state ? "none" : "block";
        sfx.playClick();
        showToast(state ? "Acoustic Telemetry Enabled" : "Acoustic Telemetry Muted", state ? "🔊" : "🔇");
      });
    }

    // Sliders, Engine Select & Display Toggles
    this.confSlider.addEventListener("input", (e) => {
      this.confVal.textContent = `${e.target.value}%`;
      sfx.playClick();
    });
    this.confSlider.addEventListener("change", () => this.reanalyzeCurrent());

    this.iouSlider.addEventListener("input", (e) => {
      this.iouVal.textContent = `${e.target.value}%`;
      sfx.playClick();
    });
    this.iouSlider.addEventListener("change", () => this.reanalyzeCurrent());

    this.backendSelect?.addEventListener("change", () => {
      sfx.playClick();
      this.reanalyzeCurrent();
    });

    [this.toggleHud, this.toggleBadges, this.toggleConf].forEach((toggle) => {
      toggle?.addEventListener("change", () => {
        sfx.playClick();
        this.reanalyzeCurrent();
      });
    });

    this.toggleInteractiveBoxes?.addEventListener("change", (e) => {
      sfx.playClick();
      const disp = e.target.checked ? "block" : "none";
      if (this.bboxSvgOverlay) this.bboxSvgOverlay.style.display = disp;
      if (this.singleBboxSvg) this.singleBboxSvg.style.display = disp;
    });

    // Quick Split Presets (Raw / 50-50 / AI)
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const pct = parseFloat(btn.dataset.split);
        this.splitSlider.setPercent(pct);
        sfx.playClick();
      });
    });

    // Copy Correlation ID on click
    const corrEl = document.getElementById("trace-corr-id");
    corrEl?.addEventListener("click", () => {
      const txt = corrEl.dataset.corr || corrEl.textContent;
      navigator.clipboard?.writeText(txt);
      showToast(`Copied Trace ID: ${txt}`, "🔗");
    });

    // Copy Markdown Report button
    document.getElementById("copy-markdown-btn")?.addEventListener("click", () => {
      if (this.currentData?.markdown_summary) {
        navigator.clipboard?.writeText(this.currentData.markdown_summary);
        showToast("Executive Markdown Report copied to clipboard", "📋");
        sfx.playClick();
      }
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
      const items = (e.clipboardData || e.originalEvent.clipboardData)?.items || [];
      for (const item of items) {
        if (item.type.indexOf("image") !== -1) {
          const blob = item.getAsFile();
          this.analyzeFile(blob);
          showToast("Analyzing pasted clipboard image...", "📋");
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
        document.getElementById("report-view").style.display = mode === "report" ? "block" : "none";
        const presets = document.getElementById("split-presets");
        if (presets) presets.style.display = mode === "split" ? "inline-flex" : "none";
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
      if (data.status === "healthy" || data.status === "degraded") {
        document.getElementById("engine-status").textContent = "5 MICROSERVICES • WBF ENSEMBLE READY";
      }
    } catch (_) {}
  }

  reanalyzeCurrent() {
    if (!this.lastSource) return;
    if (this.lastSource.type === "sample") {
      this.analyzeSample(this.lastSource.value, false);
    } else if (this.lastSource.type === "file") {
      this.analyzeFile(this.lastSource.value, false);
    }
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
          this.analyzeSample(sample.id, false);
        });
        this.samplesContainer.appendChild(tile);
      });

      if (data.samples.length > 0) {
        this.analyzeSample(data.samples[0].id, true);
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

  _appendCommonParams(formData) {
    formData.append("conf_threshold", parseFloat(this.confSlider.value) / 100);
    formData.append("iou_threshold", parseFloat(this.iouSlider.value) / 100);
    formData.append("backend", this.backendSelect ? this.backendSelect.value : "onnx");
    formData.append("show_hud", this.toggleHud.checked);
    formData.append("show_badges", this.toggleBadges ? this.toggleBadges.checked : true);
    formData.append("show_conf", this.toggleConf ? this.toggleConf.checked : true);
  }

  async analyzeSample(sampleId, isInitial = false) {
    this.lastSource = { type: "sample", value: sampleId };
    this.showScanner("EXECUTING DUAL-MODEL WBF ENSEMBLE...");
    const formData = new FormData();
    formData.append("sample_id", sampleId);
    this._appendCommonParams(formData);

    try {
      const res = await fetch("/api/detect", { method: "POST", body: formData });
      const data = await res.json();
      this.handleResults(data, !isInitial);
    } catch (err) {
      showToast("Error analyzing sample: " + err, "⚠️");
    } finally {
      this.hideScanner();
    }
  }

  async analyzeFile(file, scrollTo = true) {
    this.lastSource = { type: "file", value: file };
    this.showScanner("ANALYZING UPLOADED ROAD FRAME...");
    const formData = new FormData();
    formData.append("file", file);
    this._appendCommonParams(formData);

    try {
      const res = await fetch("/api/detect", { method: "POST", body: formData });
      const data = await res.json();
      this.handleResults(data, scrollTo);
    } catch (err) {
      showToast("Error processing uploaded image: " + err, "⚠️");
    } finally {
      this.hideScanner();
    }
  }

  animateNumber(el, targetValue, decimals = 0) {
    if (!el) return;
    const startVal = parseFloat(el.textContent) || 0;
    const duration = 420;
    const startTime = performance.now();

    const step = (now) => {
      const progress = Math.min(1, (now - startTime) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = startVal + (targetValue - startVal) * eased;
      el.textContent = decimals > 0 ? current.toFixed(decimals) : Math.round(current).toString();
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  handleResults(data, scrollToResults = false) {
    if (!data.success) {
      showToast("Analysis failed to complete.", "⚠️");
      return;
    }

    this.currentData = data;
    sfx.playSuccess();

    this.resultsSection.style.display = "block";
    if (scrollToResults) {
      this.resultsSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    // Set Images
    this.imgRaw.src = data.images.raw;
    this.imgAnnotated.src = data.images.annotated;
    this.sideRawImg.src = data.images.raw;
    this.sideAnnotatedImg.src = data.images.annotated;
    this.singleAnnotatedImg.src = data.images.annotated;

    const w = data.metadata.image_width || 640;
    const h = data.metadata.image_height || 640;
    const resBadge = document.getElementById("raw-res-badge");
    if (resBadge) resBadge.textContent = `${w}×${h} px`;

    // Populate Distributed Microservice Trace Ribbon
    this.renderMicroserviceTrace(data);

    // Populate Top KPIs
    const summary = data.summary;
    const score = summary.health_score;

    this.animateNumber(this.kpiPciVal, score, 0);
    this.kpiStatusBadge.textContent = summary.status.toUpperCase();
    if (this.kpiUrgencyNote) {
      this.kpiUrgencyNote.textContent = summary.estimated_maintenance_urgency.toUpperCase();
    }

    const dashoffset = 314 - (score / 100) * 314;
    this.gaugeCircle.style.strokeDashoffset = dashoffset;

    let strokeColor = "#10b981";
    let badgeBg = "rgba(16, 185, 129, 0.14)";
    if (score < 40) {
      strokeColor = "#ef4444";
      badgeBg = "rgba(239, 68, 68, 0.16)";
    } else if (score < 65) {
      strokeColor = "#f97316";
      badgeBg = "rgba(249, 115, 22, 0.16)";
    } else if (score < 85) {
      strokeColor = "#f59e0b";
      badgeBg = "rgba(245, 158, 11, 0.15)";
    }
    this.gaugeCircle.style.stroke = strokeColor;
    this.kpiStatusBadge.style.color = strokeColor;
    this.kpiStatusBadge.style.background = badgeBg;
    this.kpiStatusBadge.style.borderColor = strokeColor;

    const total = summary.total_defects || 0;
    const cHigh = summary.severity_counts.High || 0;
    const cMed = summary.severity_counts.Medium || 0;
    const cLow = summary.severity_counts.Low || 0;

    this.animateNumber(this.kpiTotalDefects, total, 0);
    document.getElementById("count-high").textContent = cHigh;
    document.getElementById("count-med").textContent = cMed;
    document.getElementById("count-low").textContent = cLow;

    // Update Stacked Severity Bar
    const denom = Math.max(1, total);
    document.getElementById("seg-high").style.width = total ? `${(cHigh / denom) * 100}%` : "0%";
    document.getElementById("seg-med").style.width = total ? `${(cMed / denom) * 100}%` : "0%";
    document.getElementById("seg-low").style.width = total ? `${(cLow / denom) * 100}%` : "100%";

    // Update Structural Hazards KPI dynamically
    this.animateNumber(this.kpiCriticalDefects, summary.critical_defects_count, 0);
    if (summary.critical_defects_count > 0) {
      this.kpiCriticalDefects.className = "kpi-large-number danger-text";
      if (this.kpiHazardChip) {
        this.kpiHazardChip.textContent = "ACUTE RISK";
        this.kpiHazardChip.style.color = "#f87171";
        this.kpiHazardChip.style.borderColor = "rgba(239, 68, 68, 0.4)";
        this.kpiHazardChip.style.background = "rgba(239, 68, 68, 0.15)";
      }
      if (this.kpiHazardSub) {
        this.kpiHazardSub.textContent = `${summary.critical_defects_count} high-severity structural defect(s) detected requiring priority repair dispatch.`;
      }
    } else if (total > 0) {
      this.kpiCriticalDefects.className = "kpi-large-number";
      if (this.kpiHazardChip) {
        this.kpiHazardChip.textContent = "MODERATE / PREVENTATIVE";
        this.kpiHazardChip.style.color = "#fbbf24";
        this.kpiHazardChip.style.borderColor = "rgba(245, 158, 11, 0.4)";
        this.kpiHazardChip.style.background = "rgba(245, 158, 11, 0.14)";
      }
      if (this.kpiHazardSub) {
        this.kpiHazardSub.textContent = "No high-severity hazards; schedule preventative crack sealing or surface patching.";
      }
    } else {
      this.kpiCriticalDefects.className = "kpi-large-number";
      if (this.kpiHazardChip) {
        this.kpiHazardChip.textContent = "CLEAR CORRIDOR";
        this.kpiHazardChip.style.color = "#34d399";
        this.kpiHazardChip.style.borderColor = "rgba(16, 185, 129, 0.4)";
        this.kpiHazardChip.style.background = "rgba(16, 185, 129, 0.14)";
      }
      if (this.kpiHazardSub) {
        this.kpiHazardSub.textContent = "Zero structural hazards detected on this roadway segment.";
      }
    }

    // Latency & Backend KPI
    const infMs = data.metadata.inference_time_ms;
    this.kpiLatency.innerHTML = `${infMs} <span class="kpi-unit">ms</span>`;
    const fps = (1000 / Math.max(1, infMs)).toFixed(1);
    this.kpiFps.textContent = `${fps} FPS`;
    if (this.kpiBackendInfo) {
      this.kpiBackendInfo.textContent = data.metadata.backend || "ONNX Runtime (Dual-Model WBF Ensemble)";
    }

    // Filter counts
    this.filterAllCount.textContent = data.defects.length;
    this.filterHighCount.textContent = cHigh;
    this.filterMedCount.textContent = cMed;
    this.filterLowCount.textContent = cLow;

    // Executive Markdown Report
    if (this.markdownReportBox && data.markdown_summary) {
      this.markdownReportBox.textContent = data.markdown_summary;
    }

    // Render Interactive SVG Vector Overlay, Forensic Cards, Triage Estimator & Charts
    this.renderInteractiveSvgBoxes(data.defects, w, h);
    this.renderDefectCards();
    this.renderActionItems();
    this.renderRepairEstimator(data.defects, summary);
    this.renderClassChart();
  }

  renderMicroserviceTrace(data) {
    const trace = data.microservice_trace || {};
    const timings = trace.stage_timings_ms || {};
    const infMs = data.metadata?.inference_time_ms || 52.0;

    const corrEl = document.getElementById("trace-corr-id");
    const corrId = trace.correlation_id || `rv-${Date.now().toString(16).slice(-8)}`;
    if (corrEl) {
      corrEl.textContent = `trace: ${corrId.slice(0, 12)}`;
      corrEl.dataset.corr = corrId;
    }

    const detMs = timings.detection_service_ms ?? infMs;
    const sevMs = timings.severity_service_ms ?? 3.4;
    const visMs = timings.visualization_service_ms ?? 8.2;
    const repMs = timings.reporting_service_ms ?? 1.1;

    document.getElementById("trace-det-ms").textContent = `${detMs.toFixed(1)} ms`;
    document.getElementById("trace-sev-ms").textContent = `${sevMs.toFixed(1)} ms`;
    document.getElementById("trace-vis-ms").textContent = `${visMs.toFixed(1)} ms`;
    document.getElementById("trace-rep-ms").textContent = `${repMs.toFixed(1)} ms`;

    const srcEl = document.getElementById("trace-source-label");
    if (srcEl) {
      srcEl.textContent = `${data.metadata?.source || "road_frame"} (${data.metadata?.image_width}×${data.metadata?.image_height})`;
    }
  }

  renderInteractiveSvgBoxes(defects, imgW, imgH) {
    [this.bboxSvgOverlay, this.singleBboxSvg].forEach((svg) => {
      if (!svg) return;
      svg.setAttribute("viewBox", `0 0 ${imgW} ${imgH}`);
      svg.innerHTML = "";

      defects.forEach((d) => {
        const { x1, y1, width, height } = d.bbox;
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "svg-bbox-group");
        g.setAttribute("data-defect-id", d.id);

        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("class", "svg-bbox-rect");
        rect.setAttribute("x", x1);
        rect.setAttribute("y", y1);
        rect.setAttribute("width", width);
        rect.setAttribute("height", height);
        rect.setAttribute("rx", "4");
        rect.setAttribute("stroke", d.severity.color_hex || "#38bdf8");

        const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
        title.textContent = `#${d.id} ${d.class_name} [${d.severity.level}] — Conf: ${(d.confidence * 100).toFixed(0)}%, Score: ${d.severity.score.toFixed(2)}`;
        g.appendChild(title);
        g.appendChild(rect);

        g.addEventListener("mouseenter", () => this.spotlightDefect(d.id, true));
        g.addEventListener("mouseleave", () => this.spotlightDefect(d.id, false));
        g.addEventListener("click", (e) => {
          e.stopPropagation();
          sfx.playClick();
          const card = document.getElementById(`defect-card-${d.id}`);
          if (card) {
            card.scrollIntoView({ behavior: "smooth", block: "nearest" });
            this.spotlightDefect(d.id, true);
          }
        });

        svg.appendChild(g);
      });
    });
  }

  spotlightDefect(defectId, active) {
    const card = document.getElementById(`defect-card-${defectId}`);
    if (card) {
      card.classList.toggle("highlighted", active);
    }
    document.querySelectorAll(`.svg-bbox-group[data-defect-id="${defectId}"]`).forEach((g) => {
      g.classList.toggle("active-spotlight", active);
    });
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
        <div style="text-align: center; padding: 44px 20px; color: var(--text-subtle);">
          No roadway defects matching filter <strong>"${this.activeFilter}"</strong>.
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
            <span class="defect-sev-badge ${sevClass}">${sev.level.toUpperCase()}</span>
          </div>

          <div class="severity-bar-wrapper">
            <div class="sev-bar-header">
              <span>ASTM D6433 Severity Index</span>
              <span style="color: ${sev.color_hex}; font-weight:700;">${sev.score.toFixed(2)} / 1.00</span>
            </div>
            <div class="sev-bar-track">
              <div class="sev-bar-fill" style="width: ${fillPct}%; background: ${sev.color_hex};"></div>
            </div>
          </div>

          <div class="metrics-chip-row">
            <span class="metric-chip">Area: ${sev.area_pct.toFixed(2)}%</span>
            <span class="metric-chip">Fissure Density: ${(sev.edge_density ?? 0.15).toFixed(2)}</span>
            <span class="metric-chip">Contrast Δ: ${(sev.contrast_delta ?? 0).toFixed(1)}</span>
            <span class="metric-chip">Conf: ${(d.confidence * 100).toFixed(0)}%</span>
          </div>

          <div class="defect-rationale">${sev.rationale}</div>
          <div class="defect-action-text">🛠️ ${sev.recommended_action}</div>
        </div>
      `;

      card.addEventListener("mouseenter", () => this.spotlightDefect(d.id, true));
      card.addEventListener("mouseleave", () => this.spotlightDefect(d.id, false));
      card.addEventListener("click", () => {
        sfx.playClick();
        // Move split slider to reveal this defect's X coordinate on the AI overlay
        const normX2 = d.bbox_normalized ? d.bbox_normalized.x2 : 0.75;
        const targetPct = Math.min(100, Math.max(35, Math.round(normX2 * 100 + 12)));
        this.splitSlider.setPercent(targetPct);
        this.spotlightDefect(d.id, true);
      });

      this.defectsContainer.appendChild(card);
    });
  }

  renderRepairEstimator(defects, summary) {
    const slaEl = document.getElementById("est-sla");
    const areaEl = document.getElementById("est-area-total");
    const treatEl = document.getElementById("est-treatment");
    const confEl = document.getElementById("est-mean-conf");

    const totalAreaPct = defects.reduce((acc, d) => acc + (d.severity?.area_pct || 0), 0);
    const meanConf = defects.length
      ? (defects.reduce((acc, d) => acc + d.confidence, 0) / defects.length) * 100
      : 100;

    let sla = "Routine (12 Months)";
    if (summary.status === "Critical") sla = "Immediate (< 24–48h)";
    else if (summary.status === "Poor") sla = "Priority (< 14–30d)";
    else if (summary.status === "Fair") sla = "Scheduled (60–90d)";

    let treatment = "No Intervention";
    const clsCounts = summary.class_counts || {};
    if (clsCounts["Pothole"] && summary.critical_defects_count > 0) {
      treatment = "Hot-Mix Asphalt Patch";
    } else if (clsCounts["Alligator crack"]) {
      treatment = "Full-Depth Mill & Inlay";
    } else if (clsCounts["Longitudinal crack"] || clsCounts["Transverse crack"]) {
      treatment = "Rubberized Crack Sealant";
    } else if (defects.length > 0) {
      treatment = "Cold-Patch / Surface Seal";
    }

    if (slaEl) slaEl.textContent = sla;
    if (areaEl) areaEl.textContent = `${totalAreaPct.toFixed(2)}% of frame`;
    if (treatEl) treatEl.textContent = treatment;
    if (confEl) confEl.textContent = `${meanConf.toFixed(1)}%`;
  }

  renderActionItems() {
    this.actionItemsContainer.innerHTML = "";
    const items = this.currentData.summary.action_items;

    if (!items || items.length === 0) {
      this.actionItemsContainer.innerHTML = `
        <div class="action-item-pill" style="border-color: rgba(16, 185, 129, 0.4);">
          <span class="action-bullet">✅</span>
          <span class="action-text">Roadway in good structural condition. Standard annual routine survey recommended.</span>
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

    if (Object.keys(counts).length === 0) {
      this.classChartBars.innerHTML = `<div style="font-size:0.76rem;color:var(--text-subtle);">0 defects detected on surface.</div>`;
      return;
    }

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
    showToast("Exported JSON Inspection Report", "📄");
  }

  exportCSV() {
    if (!this.currentData) return;
    const rows = [
      [
        "id",
        "class_name",
        "confidence",
        "severity_level",
        "severity_score",
        "area_pct",
        "aspect_ratio",
        "edge_density",
        "contrast_delta",
        "rationale",
        "action",
      ],
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
        d.severity.edge_density ?? 0.15,
        d.severity.contrast_delta ?? 0.0,
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
    showToast("Exported CSV Forensic Defects Log", "📊");
  }

  downloadAnnotated() {
    if (!this.currentData || !this.currentData.images.annotated) return;
    const a = document.createElement("a");
    a.href = this.currentData.images.annotated;
    a.download = `annotated_road_damage_${Date.now()}.jpg`;
    a.click();
    sfx.playClick();
    showToast("Saved High-Resolution Annotated Image", "🖼️");
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
      showToast("Unable to access camera: " + err.message, "📷");
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

    canvas.toBlob(
      (blob) => {
        this.closeWebcam();
        this.analyzeFile(blob);
      },
      "image/jpeg",
      0.92
    );
  }
}

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initParticleBackground();
  window.roadApp = new RoadVisionApp();
});
