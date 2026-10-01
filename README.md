# 👁️ Multi-Agent Face Detection, Quality Diagnostic & Self-Healing Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/OpenCV-YuNet%20%7C%20DNN-green?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV YuNet" />
  <img src="https://img.shields.io/badge/Orchestration-LangGraph%20StateGraph-orange?style=for-the-badge" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Unit%20Tests-5%2F5%20PASSED%20%E2%9C%85-brightgreen?style=for-the-badge&logo=pytest&logoColor=white" alt="PyTest" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="License" />
</p>

---

## 💡 What is This Project? (In Simple Plain English)

Have you ever tried using Face ID or uploading an ID photo in a dark room or with a blurry camera, only for the app to give up and say **"Face Not Detected"**?

Most computer vision systems work like a **single-shot camera**: they look at an image once. If the photo is too dark, blurry, or noisy, they fail immediately.

**This platform is completely different.** It works like a team of specialized AI doctors who work together to diagnose and **heal** the photo:

1. 🔍 **Agent 1 (Detector)** finds where the face is.
2. 🔬 **Agent 2 (Inspector)** checks the health of the photo: *Is it too dark? Is it blurry? Is the contrast weak?*
3. 🩺 **Agent 3 (Enhancer - The Healer)** automatically repairs the photo: brightens dark shadows using **CLAHE**, sharpens blurry edges using **Unsharp Masking**, and sends the repaired image **back to Agent 1 to re-detect!**
4. 📋 **Agent 4 (Auditor)** double-checks the final result against ground truth, calculates mathematical accuracy (IoU), and issues a certified audit report.
5. 🎨 **Synthetic Generator** creates challenging test faces (dark, blurry, noisy, with glasses) so the entire platform can be benchmarked 100% offline.

---

## 📂 Project Architecture & Directory Layout

Here is the clean, modular structure of the entire repository:

```text
multi_agent_face_detection/
├── README.md                      <-- Comprehensive System Guide & Flowcharts
├── requirements.txt               <-- Python Dependencies
├── conftest.py                    <-- Pytest Path Configuration
├── main.py                        <-- Master Entry Point & Interactive Visual HUD
├── server.py                      <-- Local Web Server & Drag-and-Drop Uploader
├── run_multiframe.py              <-- Batch Multi-Frame Pipeline & Report Exporter
├── run_headless.py                <-- Single-Frame Headless CLI Runner
├── generate_corporate_deck.py     <-- 16-Slide Corporate PowerPoint Deck Generator
├── Multi_Agent_Face_Detection_Corporate_Presentation.pptx <-- Executive Presentation Deck
├── Multi_Agent_Face_Detection_Corporate_Presentation.html <-- Interactive Browser Slides
│
├── FaceDetection_Test_images/     <-- Real-world biometric test photo suite
│
├── models/
│   └── face_detection_yunet.onnx  <-- OpenCV YuNet Deep Neural Network weights
│
├── src/
│   ├── generator/
│   │   └── face_streamer.py       <-- Synthetic test face generator (Offline testing)
│   │
│   ├── detection/
│   │   └── face_detector.py       <-- Face Detector Agent (YuNet DNN + Haar + Geometry fallback)
│   │
│   ├── quality/
│   │   └── quality_inspector.py   <-- Quality Inspector Agent (Blur, Illumination, Contrast)
│   │
│   ├── enhancement/
│   │   └── image_enhancer.py      <-- Auto-Fix Agent (CLAHE, Unsharp Mask, Gamma Correction)
│   │
│   ├── audit/
│   │   └── test_auditor.py        <-- Test & Audit Agent (IoU metrics against ground truth)
│   │
│   └── graph/
│       ├── state.py               <-- AgentState TypedDict Schema
│       └── workflow.py            <-- LangGraph Multi-Agent State Machine
│
└── tests/
    └── test_system.py             <-- Unit Tests (5/5 PASSED ✅)
```

---

## 🔄 How the Multi-Agent System Works (Flowcharts)

### 1. High-Level Concept Diagram

```mermaid
flowchart LR
    A["📸 Input Photo<br/>(Dark / Blurry / Upload)"] --> B["🔍 Agent 1: Detector<br/>(YuNet Deep Learning)"]
    B --> C["🔬 Agent 2: Inspector<br/>(Blur & Luminance Check)"]
    C --> D{"Quality Check<br/>Passed?"}
    
    D -- "❌ NO: Image Degraded" --> E["🩺 Agent 3: Auto-Fix Enhancer<br/>(CLAHE Brightness / Sharpening)"]
    E -- "🔁 Self-Healing Loop<br/>(Re-try detection on fixed frame)" --> B
    
    D -- "✅ YES: Good Quality OR Max Retries" --> F["📋 Agent 4: Test & Auditor<br/>(IoU & Verification Score)"]
    F --> G["📊 Diagnostic Dashboard<br/>(Side-by-Side Before/After)"]

    style A fill:#334155,stroke:#64748b,stroke-width:2px,color:#fff
    style B fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff
    style C fill:#854d0e,stroke:#eab308,stroke-width:2px,color:#fff
    style D fill:#4c1d95,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style E fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#fff
    style F fill:#701a75,stroke:#d946ef,stroke-width:2px,color:#fff
    style G fill:#0f766e,stroke:#14b8a6,stroke-width:2px,color:#fff
```

---

### 2. Detailed LangGraph State Machine & Decision Logic

```mermaid
flowchart TD
    START(["🚀 Start: Image Received"]) --> DETECT["<b>Node 1: Detector Agent</b><br/>• OpenCV YuNet ONNX DNN<br/>• Predicts 5 landmarks (eyes, nose, mouth)<br/>• Suppresses false glasses & collar boxes"]
    
    DETECT --> INSPECT["<b>Node 2: Quality Inspector Agent</b><br/>• Computes Laplacian Variance (Sharpness)<br/>• Computes Mean Luminance (Brightness)<br/>• Computes Contrast Standard Deviation"]
    
    INSPECT --> ROUTE{"<b>Conditional Router</b><br/>Is Image Degraded?<br/>(Blur &lt; 110 OR Luminance &lt; 75)<br/>AND Iteration &lt; 3?"}
    
    ROUTE -- "YES (Needs Repair)" --> ENHANCE["<b>Node 3: Auto-Fix Enhancer Agent</b><br/>• If UNDER_EXPOSED: LAB CLAHE + Gamma 1.6 LUT<br/>• If BLURRY: Unsharp Mask Filter + Gaussian Diff<br/>• If LOW_CONTRAST: Histogram Equalization<br/>• Increment Iteration Counter (+1)"]
    
    ENHANCE -- "Loop back with repaired image" --> DETECT
    
    ROUTE -- "NO (Quality Passed or Max Retries)" --> AUDIT["<b>Node 4: Test & Audit Agent</b><br/>• Calculates Intersection-over-Union (IoU)<br/>• Assigns Final Certification Verdict<br/>• Generates JSON Audit Ticket"]
    
    AUDIT --> FINISH(["🏁 End: Emits Telemetry & Visual Dashboard"])

    style DETECT fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff
    style INSPECT fill:#854d0e,stroke:#eab308,stroke-width:2px,color:#fff
    style ROUTE fill:#312e81,stroke:#6366f1,stroke-width:2px,color:#fff
    style ENHANCE fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#fff
    style AUDIT fill:#581c87,stroke:#a855f7,stroke-width:2px,color:#fff
    style START fill:#1e293b,stroke:#475569,stroke-width:2px,color:#fff
    style FINISH fill:#064e3b,stroke:#059669,stroke-width:2px,color:#fff
```

---

### 3. Step-by-Step Data Flow Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Camera Stream
    participant Graph as LangGraph Orchestrator
    participant D as Agent 1: Detector
    participant Q as Agent 2: Quality Inspector
    participant E as Agent 3: Enhancer (Self-Healing)
    participant A as Agent 4: Auditor

    User->>Graph: Submit Image (e.g. Dark Under-Exposed Photo)
    Graph->>D: 1. Detect faces in raw image
    D-->>Graph: Found weak face box [x, y, w, h] (Confidence: 62%)
    
    Graph->>Q: 2. Check quality of face region
    Note over Q: Measures Luminance = 32.4 (Threshold: 75.0)<br/>Result: UNDER_EXPOSED
    Q-->>Graph: Quality Report: Status = DEGRADED
    
    Note over Graph: Routing Decision: Image is degraded! Call Healer.
    Graph->>E: 3. Repair image (Target: UNDER_EXPOSED)
    Note over E: Applies CLAHE in LAB Color Space + Gamma 1.6 LUT<br/>Luminance boosted from 32.4 ➔ 84.1!
    E-->>Graph: Enhanced image buffer + Iteration = 2
    
    Note over Graph: 🔁 SELF-HEALING LOOP: Re-run Detector on Fixed Image
    Graph->>D: 4. Detect faces in repaired image
    D-->>Graph: Strong Face Detected! (Confidence: 94%)
    
    Graph->>Q: 5. Re-check quality
    Q-->>Graph: Quality Report: Status = ACCEPTABLE (Score: 92/100)
    
    Note over Graph: Routing Decision: Quality PASSED! Proceed to Audit.
    Graph->>A: 6. Run audit and compute IoU
    A-->>Graph: Verdict = PASSED_AFTER_SELF_HEALING (IoU: 0.94)
    
    Graph-->>User: Display Side-by-Side Before/After HUD
```

---

## 🤖 Deep Dive: The 5 Agents Explained

| Agent | Module | What It Does | Why It Matters |
|---|---|---|---|
| **Synthetic Streamer** | `src/generator/face_streamer.py` | Programmatically creates test faces with custom degradations (dark, blurry, noisy, glasses) and ground-truth boxes. | Allows 100% automated offline testing without needing external photo datasets. |
| **Face Detector** | `src/detection/face_detector.py` | Detects faces using OpenCV's **YuNet Deep Neural Network** (`.onnx`) with 5 landmark points; includes Haar Cascade fallback and spectacle box suppression. | Eliminates false double boxes on eyeglasses, collars, and knitwear. |
| **Quality Inspector** | `src/quality/quality_inspector.py` | Calculates Laplacian variance (blur), mean luminance (exposure), and contrast on the face ROI. | Acts as the "diagnostic brain" that decides whether the photo is clean or degraded. |
| **Auto-Fix Enhancer** | `src/enhancement/image_enhancer.py` | Applies targeted mathematical fixes: **CLAHE** for darkness, **Unsharp Masking** for blur, and **Histogram Equalization** for contrast. | **The Self-Healing Engine**: dynamically fixes the image instead of failing. |
| **Test Auditor** | `src/audit/test_auditor.py` | Measures **Intersection-over-Union (IoU)** against ground truth, calculates score (0-100), and issues the final audit verdict. | Provides auditable, enterprise-ready compliance logs for every photo processed. |

---

## 🧪 Unit Tests: 5/5 PASSED ✅

The repository includes a comprehensive test suite in [`tests/test_system.py`](tests/test_system.py) that verifies every single agent individually and tests the entire multi-agent loop end-to-end:

```bash
pytest -v
```

### What Each Test Proves:

| Test Case | Agent Tested | What It Verifies | Status |
|---|---|---|---|
| `test_face_streamer` | **Synthetic Streamer** | Verifies synthetic images generate correct dimensions `(256, 256, 3)` with valid ground-truth bounding box coordinates. | ✅ **PASSED** |
| `test_detector_agent` | **Face Detector** | Verifies that YuNet DNN locates the face and outputs valid bounding boxes `[x, y, w, h]` and confidence scores. | ✅ **PASSED** |
| `test_quality_inspector_agent` | **Quality Inspector** | Verifies that sharpness, luminance, and contrast calculations work correctly and assign a quality score > 50 on standard images. | ✅ **PASSED** |
| `test_enhancer_agent` | **Auto-Fix Enhancer** | Verifies that an underexposed dark frame triggers `CLAHE_BRIGHTNESS_BOOST` and mathematically increases mean pixel luminance. | ✅ **PASSED** |
| `test_multi_agent_workflow` | **LangGraph Orchestrator** | Verifies the **full self-healing loop**: a degraded dark image enters the graph, fails iteration 1, gets repaired by the enhancer, passes on iteration 2, and receives verdict `PASSED_AFTER_SELF_HEALING`. | ✅ **PASSED** |

```text
============================= test session starts =============================
platform win32 -- Python 3.8.8, pytest-6.2.3
rootdir: multi_agent_face_detection
collected 5 items

tests/test_system.py::test_face_streamer PASSED                          [ 20%]
tests/test_system.py::test_detector_agent PASSED                        [ 40%]
tests/test_system.py::test_quality_inspector_agent PASSED               [ 60%]
tests/test_system.py::test_enhancer_agent PASSED                        [ 80%]
tests/test_system.py::test_multi_agent_workflow PASSED                 [100%]

======================== 5 passed in 0.61s ====================================
```

---

## ⚡ Comparison: Traditional Single-Pass vs. Multi-Agent Platform

| Real-World Challenge | Traditional Single-Pass CV | This Multi-Agent Platform |
|---|---|---|
| **Low Light / Dark Room** | ❌ Fails to detect face ($0\%$ confidence) | ✅ **Self-Heals**: CLAHE + Gamma LUT recovers face ($91\%$ confidence) |
| **Motion or Camera Blur** | ❌ Faces missed due to blurred edges | ✅ **Self-Heals**: Unsharp mask kernel sharpens facial contours |
| **Wearing Eyeglasses** | ⚠️ Often detects 2 boxes (face + glasses) | ✅ **Suppressed**: NMS containment filter rejects nested sub-boxes |
| **Group Photos** | ❌ Often drops secondary faces | ✅ **Resolved**: Multi-ROI pass isolates and scores each subject |
| **Auditability** | ❌ Raw coordinates only | ✅ **Certified**: JSON audit ticket with IoU, blur score, and retry history |

---

## 🚀 Quick Start in 60 Seconds

### 1. Clone & Install

```bash
# Clone the repository
git clone https://github.com/pankajatd/multi-agent-face-detection.git
cd multi-agent-face-detection

# Install dependencies
pip install -r requirements.txt
```

### 2. Choose How You Want to Run It

#### Option A: Interactive Web Dashboard & Photo Uploader (Recommended! ⭐)
Launch the local web application:
```bash
python server.py
```
- Open your browser at: 👉 **`http://localhost:8050/output_multiframe/side_by_side_dashboard.html`**
- **Drag and drop any photo** (selfies, dark photos, group pictures) to see the Before vs. After self-healing results live!
- Use **Auto-Play** to watch an automated slideshow of test cases and uploads.

#### Option B: Interactive OpenCV Desktop HUD
```bash
python main.py
```
- Opens a desktop window showing the Before vs. After HUD.
- Press **ANY KEY** on your keyboard to cycle through:
  1. Standard Clean Face
  2. Dark Underexposed Face (Watch CLAHE heal it!)
  3. Blurry Face (Watch Unsharp Mask sharpen it!)

#### Option C: Batch Multi-Frame Pipeline
```bash
python run_multiframe.py
```
- Processes all 8 benchmark test suites and exports side-by-side comparison images and `multiframe_report.json`.

#### Option D: Run Unit Tests
```bash
pytest
```

---

## 📋 Data Contract: `AgentState` Schema

All agents communicate via a unified, immutable dictionary schema (`AgentState` in `src/graph/state.py`):

```python
class AgentState(TypedDict):
    current_image: np.ndarray          # Active working image (modified by Healer)
    original_image: np.ndarray         # Untouched input image (for side-by-side comparison)
    metadata: Dict[str, Any]           # Ground truth coordinates and test parameters
    detections: List[Dict[str, Any]]   # Bounding boxes [x, y, w, h], landmarks, confidence
    quality_report: Dict[str, Any]     # Blur score, mean luminance, contrast, status
    iteration_count: int               # Current loop counter (starts at 1)
    max_iterations: int                # Maximum self-healing attempts (default: 3)
    enhancement_history: List[str]     # Log of repairs applied (e.g. ['CLAHE_BRIGHTNESS_BOOST'])
    audit_report: Dict[str, Any]       # Final verdict, IoU score, and compliance certification
```

---

## 📜 License

Distributed under the **MIT License**. You are free to use, modify, and distribute this codebase for academic, personal, and commercial projects.
