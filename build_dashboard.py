import os
import cv2
import json
import base64
import numpy as np

def img_to_base64(img_path_or_array):
    if isinstance(img_path_or_array, str):
        with open(img_path_or_array, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    else:
        success, encoded = cv2.imencode(".png", img_path_or_array)
        if success:
            return "data:image/png;base64," + base64.b64encode(encoded.tobytes()).decode("utf-8")
    return ""

def generate_interactive_dashboard():
    output_dir = r"C:\Users\panka\.gemini\antigravity\scratch\multi_agent_face_detection\output_multiframe"
    report_file = os.path.join(output_dir, "multiframe_report.json")
    
    with open(report_file, "r") as f:
        report = json.load(f)

    frame_data_list = []

    for r in report:
        label = r["frame_label"]
        input_path = os.path.join(output_dir, f"{label}_input.png")
        output_path = os.path.join(output_dir, f"{label}_output.png")

        input_b64 = img_to_base64(input_path) if os.path.exists(input_path) else ""
        output_b64 = img_to_base64(output_path) if os.path.exists(output_path) else ""

        # Crop detected face if present
        cropped_face_b64 = ""
        output_cv = cv2.imread(output_path) if os.path.exists(output_path) else None

        if output_cv is not None and r.get("detections"):
            primary_det = r["detections"][0]
            bbox = primary_det.get("bbox", [0, 0, 0, 0])
            x, y, w, h = bbox
            ih, iw = output_cv.shape[:2]

            # Margin around face crop
            margin_x = int(w * 0.15)
            margin_y = int(h * 0.15)
            x1 = max(0, x - margin_x)
            y1 = max(0, y - margin_y)
            x2 = min(iw, x + w + margin_x)
            y2 = min(ih, y + h + margin_y)

            crop = output_cv[y1:y2, x1:x2]
            if crop.size > 0:
                cropped_face_b64 = img_to_base64(crop)

        frame_data_list.append({
            "label": label,
            "input_img": input_b64,
            "output_img": output_b64,
            "cropped_face": cropped_face_b64,
            "detection_count": r.get("detection_count", 0),
            "detections": r.get("detections", []),
            "quality_report": r.get("quality_report", {}),
            "audit_report": r.get("audit_report", {}),
            "verdict": r.get("verdict", "UNKNOWN"),
            "quality_score": r.get("quality_score", 0.0),
            "retries": r.get("retries", 0),
            "enhancements": r.get("enhancements", []),
            "latency_ms": r.get("latency_ms", 0.0),
            "degradation": r.get("degradation", "none")
        })

    json_payload = json.dumps(frame_data_list)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Multi-Agent Face Detection Live Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @keyframes pulse-slow {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.6; }}
    }}
    .live-dot {{
      animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}
  </style>
</head>
<body class="bg-[#0f172a] text-slate-100 min-h-screen p-4 md:p-6 font-sans">
  <div class="max-w-7xl mx-auto space-y-6">

    <!-- Top Navigation / Header -->
    <header class="bg-[#1e293b] border border-slate-700/60 rounded-2xl p-5 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-3">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span class="w-2 h-2 rounded-full bg-emerald-400 live-dot"></span>
            ACTIVE MONITORING
          </span>
          <span class="text-xs text-slate-400 font-mono">LANGGRAPH ORCHESTRATOR v2.4</span>
        </div>
        <h1 class="text-2xl font-bold text-white tracking-tight mt-1">Multi-Agent Face Detection & Diagnostic Platform</h1>
        <p class="text-sm text-slate-400">Autonomous Self-Healing Video Stream Diagnostics</p>
      </div>

      <!-- Quick Metrics Ribbon -->
      <div class="flex items-center gap-3">
        <div class="bg-slate-900/80 border border-slate-700/50 rounded-xl px-4 py-2 text-center">
          <div class="text-xs text-slate-400 uppercase font-medium">Frames</div>
          <div id="stat-total-frames" class="text-lg font-bold text-white">8</div>
        </div>
        <div class="bg-slate-900/80 border border-slate-700/50 rounded-xl px-4 py-2 text-center">
          <div class="text-xs text-slate-400 uppercase font-medium">Passed</div>
          <div id="stat-passed-frames" class="text-lg font-bold text-emerald-400">6 / 8</div>
        </div>
        <div class="bg-slate-900/80 border border-slate-700/50 rounded-xl px-4 py-2 text-center">
          <div class="text-xs text-slate-400 uppercase font-medium">Avg Score</div>
          <div id="stat-avg-score" class="text-lg font-bold text-cyan-400">61.1</div>
        </div>
        <div class="bg-slate-900/80 border border-slate-700/50 rounded-xl px-4 py-2 text-center">
          <div class="text-xs text-slate-400 uppercase font-medium">Healed</div>
          <div id="stat-healed" class="text-lg font-bold text-amber-400">3 frames</div>
        </div>
      </div>
    </header>

    <!-- Interactive Video Stream Player Bar -->
    <div class="bg-[#1e293b] border border-slate-700/60 rounded-2xl p-4 shadow-lg flex flex-col md:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <button id="btn-play" onclick="togglePlay()" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm transition-all shadow-md">
          <span id="play-icon">▶</span>
          <span id="play-text">Play Stream</span>
        </button>
        <button onclick="prevFrame()" class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition">
          ◀ Prev
        </button>
        <button onclick="nextFrame()" class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition">
          Next ▶
        </button>
      </div>

      <!-- Frame Buttons Strip -->
      <div class="flex items-center gap-1.5 flex-wrap justify-center" id="frame-pill-container">
        <!-- Rendered via JS -->
      </div>

      <div class="text-xs text-slate-400 font-mono">
        Frame: <span id="current-frame-idx" class="text-cyan-400 font-bold">1</span> / 8
      </div>
    </div>

    <!-- Main Live Visual Stage (3-Column Layout: Input | Detected Output | Cropped Detected Face) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

      <!-- Left Stage: Raw Input Frame (4 Cols) -->
      <div class="lg:col-span-4 bg-[#1e293b] border border-slate-700/60 rounded-2xl p-4 shadow-xl flex flex-col">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Raw Input Frame</span>
          <span id="badge-degradation" class="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">none</span>
        </div>
        <div class="relative aspect-square w-full bg-slate-900 rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center">
          <img id="view-input-img" src="" alt="Input Frame" class="w-full h-full object-contain" />
          <div class="absolute bottom-2 left-2 bg-black/70 backdrop-blur px-2 py-1 rounded text-[11px] font-mono text-slate-300">
            Resolution: 400x400
          </div>
        </div>
        <p class="text-xs text-slate-400 mt-2 text-center">Unprocessed synthetic camera feed</p>
      </div>

      <!-- Center Stage: Final Image with Bounding Box & HUD (5 Cols) -->
      <div class="lg:col-span-5 bg-[#1e293b] border border-slate-700/60 rounded-2xl p-4 shadow-xl flex flex-col">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            Detected Face with Bounding Box
          </span>
          <span id="badge-verdict" class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            PASSED
          </span>
        </div>
        <div class="relative aspect-square w-full bg-slate-900 rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center">
          <img id="view-output-img" src="" alt="Detected Output Frame" class="w-full h-full object-contain" />
          <div id="hud-overlay" class="absolute top-2 left-2 bg-black/75 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700 text-xs font-mono space-y-0.5">
            <div class="text-cyan-400 font-semibold" id="hud-conf">Face Detected: 65%</div>
            <div class="text-slate-300 text-[11px]" id="hud-bbox">BBox: [118, 78, 215, 295]</div>
          </div>
        </div>
        <div class="flex items-center justify-between mt-2 text-xs text-slate-400">
          <span>Latency: <strong id="val-latency" class="text-slate-200">12 ms</strong></span>
          <span>Quality Score: <strong id="val-score" class="text-emerald-400">98.3 / 100</strong></span>
        </div>
      </div>

      <!-- Right Stage: Zoomed Detected Face Crop & Primary Verdict (3 Cols) -->
      <div class="lg:col-span-3 bg-[#1e293b] border border-slate-700/60 rounded-2xl p-4 shadow-xl flex flex-col">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Cropped Face (ROI)</span>
          <span class="text-[11px] font-mono text-slate-400">FOCUSED</span>
        </div>

        <div class="relative aspect-square w-full bg-slate-900 rounded-xl overflow-hidden border border-cyan-500/30 flex items-center justify-center shadow-inner group">
          <img id="view-crop-img" src="" alt="Detected Face Crop" class="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105" />
          <div id="no-crop-placeholder" class="hidden absolute inset-0 flex flex-col items-center justify-center text-slate-500 p-4 text-center">
            <svg class="w-12 h-12 mb-2 text-rose-500/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <span class="text-xs font-semibold text-rose-400">No Face Detected</span>
            <span class="text-[10px] text-slate-500 mt-1">Quality gate rejected frame</span>
          </div>
        </div>

        <!-- Quick Summary Cards -->
        <div class="mt-4 space-y-2 text-xs">
          <div class="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800">
            <span class="text-slate-400 block text-[11px]">Primary Detection Status</span>
            <span id="crop-status-text" class="font-bold text-white">Detected with High Confidence</span>
          </div>
          <div class="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800">
            <span class="text-slate-400 block text-[11px]">Self-Healing Transformations</span>
            <span id="crop-heal-text" class="font-mono text-amber-300">HISTOGRAM_EQUALIZATION</span>
          </div>
        </div>
      </div>

    </div>

    <!-- Multi-Agent Telemetry Grid (4 Agents in Parallel Pipeline) -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

      <!-- Agent 1: Detector Agent -->
      <div class="bg-[#1e293b] border border-slate-700/60 rounded-2xl p-4 shadow-lg">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-xs">
            1
          </div>
          <div>
            <h3 class="text-sm font-semibold text-white">Face Detector Agent</h3>
            <p class="text-[11px] text-slate-400">Cascade + Color Geometry</p>
          </div>
        </div>
        <div class="space-y-1.5 text-xs font-mono bg-slate-900/70 p-3 rounded-xl border border-slate-800">
          <div class="flex justify-between">
            <span class="text-slate-400">Faces Found:</span>
            <span id="ag1-faces" class="text-cyan-400 font-bold">1</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Confidence:</span>
            <span id="ag1-conf" class="text-emerald-400">65%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Method:</span>
            <span id="ag1-method" class="text-slate-200 text-[10px]">color_geometry</span>
          </div>
        </div>
      </div>

      <!-- Agent 2: Quality Inspector Agent -->
      <div class="bg-[#1e293b] border border-slate-700/60 rounded-2xl p-4 shadow-lg">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold text-xs">
            2
          </div>
          <div>
            <h3 class="text-sm font-semibold text-white">Quality Inspector Agent</h3>
            <p class="text-[11px] text-slate-400">Blur, Illumination, Contrast</p>
          </div>
        </div>
        <div class="space-y-1.5 text-xs font-mono bg-slate-900/70 p-3 rounded-xl border border-slate-800">
          <div class="flex justify-between">
            <span class="text-slate-400">Sharpness:</span>
            <span id="ag2-sharp" class="text-slate-200">145.2</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Luminance:</span>
            <span id="ag2-lum" class="text-slate-200">182.0</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Contrast:</span>
            <span id="ag2-contrast" class="text-slate-200">34.8</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Diagnosed:</span>
            <span id="ag2-issues" class="text-amber-400 font-bold">None</span>
          </div>
        </div>
      </div>

      <!-- Agent 3: Enhancer Agent -->
      <div class="bg-[#1e293b] border border-slate-700/60 rounded-2xl p-4 shadow-lg">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 font-bold text-xs">
            3
          </div>
          <div>
            <h3 class="text-sm font-semibold text-white">Auto-Fix Enhancer Agent</h3>
            <p class="text-[11px] text-slate-400">Autonomous Self-Healing Loop</p>
          </div>
        </div>
        <div class="space-y-1.5 text-xs font-mono bg-slate-900/70 p-3 rounded-xl border border-slate-800">
          <div class="flex justify-between">
            <span class="text-slate-400">Retries Taken:</span>
            <span id="ag3-retries" class="text-amber-400 font-bold">1</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Last Action:</span>
            <span id="ag3-action" class="text-slate-200 text-[10px]">HIST_EQUALIZE</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Loop Status:</span>
            <span id="ag3-status" class="text-emerald-400">COMPLETED</span>
          </div>
        </div>
      </div>

      <!-- Agent 4: Test Auditor Agent -->
      <div class="bg-[#1e293b] border border-slate-700/60 rounded-2xl p-4 shadow-lg">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold text-xs">
            4
          </div>
          <div>
            <h3 class="text-sm font-semibold text-white">Test Auditor Agent</h3>
            <p class="text-[11px] text-slate-400">IoU Verification & Final Gate</p>
          </div>
        </div>
        <div class="space-y-1.5 text-xs font-mono bg-slate-900/70 p-3 rounded-xl border border-slate-800">
          <div class="flex justify-between">
            <span class="text-slate-400">Quality Score:</span>
            <span id="ag4-score" class="text-emerald-400 font-bold">98.3 / 100</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">IoU vs Truth:</span>
            <span id="ag4-iou" class="text-cyan-400">0.961</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Verdict:</span>
            <span id="ag4-verdict" class="text-emerald-400 font-bold text-[10px]">PASSED_HEALED</span>
          </div>
        </div>
      </div>

    </div>

    <!-- All 8 Frames Gallery Grid (Click to Inspect) -->
    <div class="bg-[#1e293b] border border-slate-700/60 rounded-2xl p-5 shadow-xl">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-base font-bold text-white">Full Video Stream Frame Gallery</h2>
          <p class="text-xs text-slate-400">Click any frame below to inspect its detected face and agent diagnostics</p>
        </div>
        <span class="text-xs font-mono text-slate-400 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">8 FRAMES TOTAL</span>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-3" id="gallery-container">
        <!-- Rendered via JS -->
      </div>
    </div>

  </div>

  <script>
    const frames = {json_payload};
    let currentIndex = 0;
    let isPlaying = false;
    let playInterval = null;

    function renderFrame(index) {{
      currentIndex = index;
      const data = frames[index];

      // Update frame indicators
      document.getElementById('current-frame-idx').innerText = (index + 1);

      // Images
      document.getElementById('view-input-img').src = data.input_img;
      document.getElementById('view-output-img').src = data.output_img;

      // Crop
      const cropImg = document.getElementById('view-crop-img');
      const placeholder = document.getElementById('no-crop-placeholder');
      if (data.cropped_face) {{
        cropImg.src = data.cropped_face;
        cropImg.classList.remove('hidden');
        placeholder.classList.add('hidden');
        document.getElementById('crop-status-text').innerText = `Face Detected (${{data.detection_count}} Face)`;
        document.getElementById('crop-status-text').className = "font-bold text-emerald-400";
      }} else {{
        cropImg.classList.add('hidden');
        placeholder.classList.remove('hidden');
        document.getElementById('crop-status-text').innerText = "No Face Detected";
        document.getElementById('crop-status-text').className = "font-bold text-rose-400";
      }}

      // Enhancements
      const enhText = (data.enhancements && data.enhancements.length > 0)
        ? data.enhancements.join(', ')
        : 'NONE_NEEDED';
      document.getElementById('crop-heal-text').innerText = enhText;

      // Badges & HUD
      document.getElementById('badge-degradation').innerText = `deg: ${{data.degradation}}`;
      
      const vBadge = document.getElementById('badge-verdict');
      vBadge.innerText = data.verdict;
      if (data.verdict.includes('PASSED')) {{
        vBadge.className = "text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
      }} else {{
        vBadge.className = "text-xs font-bold px-2.5 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20";
      }}

      // HUD
      const det = data.detections && data.detections[0];
      if (det) {{
        document.getElementById('hud-conf').innerText = `Face Detected: ${{(det.confidence * 100).toFixed(0)}}%`;
        document.getElementById('hud-bbox').innerText = `BBox: [${{det.bbox.join(', ')}}]`;
      }} else {{
        document.getElementById('hud-conf').innerText = "Face Detected: 0%";
        document.getElementById('hud-bbox').innerText = "BBox: None";
      }}

      document.getElementById('val-latency').innerText = `${{data.latency_ms}} ms`;
      document.getElementById('val-score').innerText = `${{data.quality_score.toFixed(1)}} / 100`;

      // Agent 1
      document.getElementById('ag1-faces').innerText = data.detection_count;
      document.getElementById('ag1-conf').innerText = det ? `${{(det.confidence * 100).toFixed(0)}}%` : '0%';
      document.getElementById('ag1-method').innerText = det ? (det.method || 'cascade') : 'none';

      // Agent 2
      const q = data.quality_report || {{}};
      document.getElementById('ag2-sharp').innerText = q.blur_score ? q.blur_score.toFixed(1) : '0';
      document.getElementById('ag2-lum').innerText = q.luminance ? q.luminance.toFixed(1) : '0';
      document.getElementById('ag2-contrast').innerText = q.contrast ? q.contrast.toFixed(1) : '0';
      const issues = (q.issues && q.issues.length > 0) ? q.issues.join(', ') : 'None';
      document.getElementById('ag2-issues').innerText = issues;

      // Agent 3
      document.getElementById('ag3-retries').innerText = data.retries;
      document.getElementById('ag3-action').innerText = (data.enhancements && data.enhancements.length > 0)
        ? data.enhancements[data.enhancements.length - 1]
        : 'NONE';
      document.getElementById('ag3-status').innerText = data.retries > 0 ? 'SELF_HEALED' : 'CLEAN';

      // Agent 4
      const a = data.audit_report || {{}};
      document.getElementById('ag4-score').innerText = `${{data.quality_score.toFixed(1)}} / 100`;
      document.getElementById('ag4-iou').innerText = a.iou_vs_ground_truth !== undefined ? a.iou_vs_ground_truth : 'N/A';
      document.getElementById('ag4-verdict').innerText = data.verdict;

      // Update pills
      document.querySelectorAll('.frame-pill').forEach((btn, idx) => {{
        if (idx === index) {{
          btn.className = "frame-pill px-3 py-1 rounded-lg text-xs font-semibold bg-cyan-500 text-slate-900 border border-cyan-400 shadow-md";
        }} else {{
          btn.className = "frame-pill px-3 py-1 rounded-lg text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700";
        }}
      }});

      // Update gallery cards
      document.querySelectorAll('.gallery-card').forEach((card, idx) => {{
        if (idx === index) {{
          card.classList.add('ring-2', 'ring-cyan-400');
        }} else {{
          card.classList.remove('ring-2', 'ring-cyan-400');
        }}
      }});
    }}

    function nextFrame() {{
      const next = (currentIndex + 1) % frames.length;
      renderFrame(next);
    }}

    function prevFrame() {{
      const prev = (currentIndex - 1 + frames.length) % frames.length;
      renderFrame(prev);
    }}

    function togglePlay() {{
      isPlaying = !isPlaying;
      const btnText = document.getElementById('play-text');
      const btnIcon = document.getElementById('play-icon');
      if (isPlaying) {{
        btnText.innerText = "Pause";
        btnIcon.innerText = "⏸";
        playInterval = setInterval(nextFrame, 1800);
      }} else {{
        btnText.innerText = "Play Stream";
        btnIcon.innerText = "▶";
        clearInterval(playInterval);
      }}
    }}

    // Init UI controls
    function init() {{
      const pillContainer = document.getElementById('frame-pill-container');
      const gallery = document.getElementById('gallery-container');

      frames.forEach((f, idx) => {{
        // Pill
        const pill = document.createElement('button');
        pill.innerText = `F0${{idx + 1}}`;
        pill.onclick = () => renderFrame(idx);
        pillContainer.appendChild(pill);

        // Gallery item
        const card = document.createElement('div');
        const passed = f.verdict.includes('PASSED');
        card.className = "gallery-card bg-slate-900 rounded-xl p-2 border border-slate-800 cursor-pointer hover:border-slate-600 transition flex flex-col items-center";
        card.onclick = () => renderFrame(idx);

        card.innerHTML = `
          <div class="relative w-full aspect-square bg-slate-950 rounded-lg overflow-hidden mb-1.5 flex items-center justify-center">
            <img src="${{f.output_img}}" class="w-full h-full object-contain" />
            <span class="absolute top-1 right-1 text-[9px] px-1 py-0.2 rounded font-bold ${{passed ? 'bg-emerald-500 text-slate-900' : 'bg-rose-500 text-white'}}">
              ${{passed ? 'PASS' : 'FAIL'}}
            </span>
          </div>
          <span class="text-[11px] font-mono text-slate-300 font-semibold truncate w-full text-center">F0${{idx + 1}}</span>
          <span class="text-[10px] text-slate-400 font-mono">${{f.quality_score.toFixed(0)}}/100</span>
        `;
        gallery.appendChild(card);
      }});

      renderFrame(0);
    }}

    window.onload = init;
  </script>
</body>
</html>
"""

    # 1. Save to output_multiframe folder
    target_path = os.path.join(output_dir, "dashboard.html")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated dashboard at: {target_path}")

    # 2. Save to artifact directory
    artifact_dir = r"C:\Users\panka\.gemini\antigravity\brain\276eabb5-2a3c-49db-b06a-11253f52eae1"
    artifact_path = os.path.join(artifact_dir, "face_detection_dashboard.html")
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated artifact at: {artifact_path}")

if __name__ == "__main__":
    generate_interactive_dashboard()
