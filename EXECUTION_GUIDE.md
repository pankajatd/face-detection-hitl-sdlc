# Multi-Agent Face Detection & Diagnostic Platform
## Complete Getting Started & Execution Guide for New Users

Welcome! This guide is designed for **anyone new to this project** who wants to set up, execute, test, and explore the **Multi-Agent Face Detection & Diagnostic Platform** from scratch in Visual Studio Code or any terminal.

---

## 1. What is This Project?

Unlike traditional face detection scripts that execute a single pass and fail when a photo is blurry, dark, or has multiple faces, this project is an **Agentic AI platform** built on the **LangGraph StateGraph** pattern:

```
[ Input Photo / Frame ]
         │
         ▼
[ Agent 1: Face Detector (YuNet DNN) ] ──► [ Agent 2: Quality Inspector ]
         ▲                                           │
         │                                           ▼
[ Agent 3: Image Enhancer (Self-Healing) ] ◄── [ Is Image Degraded? ]
  (CLAHE Brightness, Unsharp Mask Blur Fix)          │
                                                     ▼ NO / Clean / Max Retries
                                        [ Agent 4: Test & Quality Auditor ]
                                                     │
                                                     ▼
                                        [ Side-by-Side Visual Dashboard ]
```

### The 4 Autonomous Agents:
1. **Agent 1 (`FaceDetectorAgent`)**: Uses OpenCV's **YuNet Deep Neural Network** (`face_detection_yunet.onnx`) with 5 facial landmarks to achieve high-precision detection without false positives on knitwear or shirts.
2. **Agent 2 (`QualityInspectorAgent`)**: Evaluates mathematical blur (Laplacian variance), exposure (mean luminance), and contrast, while suppressing false spectacle sub-boxes.
3. **Agent 3 (`ImageEnhancerAgent`)**: The **Autonomous Self-Healing Engine**. When Agent 2 flags low light or blur, Agent 3 enhances the image buffer (CLAHE brightness boost, unsharp sharpening) and loops back to Agent 1 to re-detect!
4. **Agent 4 (`TestAuditorAgent`)**: Compares detections against ground truth (IoU calculation), scores quality (0-100), and assigns a certification verdict (`PASSED`, `WARNING`, `FAILED`).

---

## 2. Prerequisites & Quick Setup

### System Requirements:
- **Operating System**: Windows 10/11, macOS, or Linux.
- **Python**: Version 3.8, 3.9, 3.10, or 3.11 (Anaconda or standard Python).
- **Editor**: Visual Studio Code (recommended) or any standard terminal.

### Step 1: Open the Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File ➔ Open Folder...** and select:
   ```
   C:\Users\panka\.gemini\antigravity\scratch\multi_agent_face_detection
   ```
3. Open an integrated terminal in VS Code:
   - Press **`Ctrl + ` `** (backtick) or select **Terminal ➔ New Terminal**.

### Step 2: Install Required Dependencies
In the VS Code terminal, execute:
```powershell
pip install -r requirements.txt
```
*(Dependencies include: `opencv-python`, `numpy`, `pytest`, `python-pptx`, and `scikit-learn`.)*

### Step 3: Verify the YuNet Deep Learning Model
Ensure the ONNX deep learning model exists in the `models/` folder:
```powershell
dir models\face_detection_yunet.onnx
```
*(The system includes an automatic fallback to OpenCV Haar Cascades if the model is ever moved.)*

---

## 3. How to Run the Project (3 Execution Modes)

### Mode A: Launch the Interactive Web Dashboard & Upload Tool (Recommended Demo)
This is the **primary interactive experience**. It launches a local web server with a real-time side-by-side comparison dashboard, multi-photo uploader, and auto-play slideshow.

1. **In your VS Code terminal, run:**
   ```powershell
   python server.py
   ```
2. **What happens:**
   - The local API server starts on port `8050`.
   - Your default browser automatically opens:
     👉 **`http://localhost:8050/output_multiframe/side_by_side_dashboard.html`**
3. **How to test and interact in the UI:**
   - **Upload Photos**: Drag-and-drop or select any picture (group photos, couples, selfies, dark portraits). The system will process it through all 4 agents immediately.
   - **Auto Play All**: Click to watch an automated slideshow cycling through all test cases and uploads.
   - **Play Uploads Only**: Cycles exclusively through the images you have uploaded.
   - **Adjust Speed**: Use the speed selector (`1s`, `2s`, `3s`, `5s`) to control auto-play timing.
   - **Delete Uploads**: Click the **"Delete Uploads"** button at any time to clear uploaded images and reset your session.
   - **Inspect HUD**: Look at the top HUD showing:
     - **Blur Variance**: Sharpness level (green = crisp, amber = blurred).
     - **Luminance**: Brightness level (green = optimal, blue = underexposed).
     - **Self-Healing Iterations**: Number of auto-fix cycles applied.
     - **Audit Verdict**: `PASSED` or `WARNING`.

4. **To Stop the Server:**
   - Press **`Ctrl + C`** in your VS Code terminal.

---

### Mode B: Run the Multi-Frame Batch Pipeline (Headless Execution)
If you want to run the pipeline without opening a web server (e.g. for batch testing or automated pipelines):

1. **Run:**
   ```powershell
   python run_multiframe.py
   ```
2. **What happens:**
   - Ingests test frames (clean, degraded low-light, motion-blurred, multiple faces).
   - Executes the 4-agent LangGraph self-healing loop.
   - Generates side-by-side before/after comparison images.
   - Saves all output images and metadata inside `output_multiframe/`.
   - Prints a summary report to your terminal showing detection recall, self-healing actions, and audit scores.

---

### Mode C: View the Architecture Presentation Deck (PPT)
To present the architecture, flowcharts, benchmark tables, and agent roles to colleagues or stakeholders:

- **Option 1: Interactive Browser Slide Deck**
  While `python server.py` is running, open:
  👉 **`http://localhost:8050/presentation_deck.html`**
  - Navigate using **`→`** / **`←`** arrow keys or **`Space`**.
  - Press **`F`** for fullscreen presentation mode.
- **Option 2: Microsoft PowerPoint**
  Double-click or open the generated PowerPoint file:
  📁 `presentation_deck.pptx`

---

## 4. How to Run the Automated Test Suite

To verify code integrity, agent state consistency, and self-healing algorithms:

```powershell
pytest tests/ -v
```

### What the Tests Verify:
- `test_state.py`: Confirms that the `AgentState` schema dictionary is immutable and holds all required diagnostic keys.
- `test_detector.py`: Tests the YuNet deep learning face detector and verified discrete boxes for adjacent faces.
- `test_quality_inspector.py`: Tests mathematical blur variance (Laplacian) and exposure metrics.
- `test_enhancer.py`: Verifies CLAHE brightness boost and unsharp mask algorithms.
- `test_auditor.py`: Verifies IoU ground-truth calculation and composite scoring (0–100).

---

## 5. Project Directory & Key Files Reference

| File / Folder | Role & Description |
|---|---|
| **`server.py`** | Fast local HTTP server (Port 8050) providing `/api/health`, `/api/slides`, `/api/upload_detect`, and `/api/delete_uploads`. |
| **`run_multiframe.py`** | Batch multi-frame processing pipeline that runs the 4-agent loop and renders comparison frames. |
| **`presentation_deck.pptx`** | Native 10-slide 16:9 Microsoft PowerPoint presentation deck. |
| **`presentation_deck.html`** | Interactive HTML slide deck for in-browser presentation. |
| **`implementation_plan.md`** | Deep architectural design document detailing the LangGraph agent state machine. |
| **`tasks_and_code_snippets.md`** | Complete engineering document detailing Task 1 through Task 8 with full source code. |
| **`models/`** | Contains `face_detection_yunet.onnx` (OpenCV YuNet Deep Learning model). |
| **`output_multiframe/`** | Stores processed side-by-side images, slideshow data, and user uploads (`user_uploads/`). |
| **`src/detection/`** | `FaceDetectorAgent`: YuNet DNN face detection & multi-scale pyramid scan. |
| **`src/quality/`** | `QualityInspectorAgent`: Laplacian blur, exposure, and spectacle filtering. |
| **`src/enhancement/`** | `ImageEnhancerAgent`: Autonomous self-healing (CLAHE, Unsharp Mask). |
| **`src/auditing/`** | `TestAuditorAgent`: IoU calculation against ground truth and composite scoring. |
| **`src/graph/`** | `state.py`: LangGraph immutable state machine schema and decision routing. |

---

## 6. Frequently Asked Questions & Troubleshooting

### Q1: The terminal says "Address already in use" on port 8050.
- **Cause**: A previous instance of `server.py` is still running in the background.
- **Fix**: Open PowerShell and run:
  ```powershell
  Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
  ```
  Then re-run:
  ```powershell
  python server.py
  ```

### Q2: What happens if someone uploads a dark or blurry photo?
- The **Quality Inspector Agent** detects the low luminance (< 40) or blur (< 100).
- The **Decision Gate** diverts the state to the **Image Enhancer Agent**.
- The Enhancer applies an adaptive CLAHE brightness boost or unsharp mask sharpening.
- The enhanced buffer is fed back into the **Face Detector Agent** for re-detection.
- You will see the iteration count increase from `0` to `1` on the dashboard HUD.

### Q3: How do adjacent faces get detected as 2 separate boxes instead of 1 merged box?
- In `src/detection/face_detector.py`, the Non-Maximum Suppression (NMS) intersection threshold is calibrated to `iou_thresh = 0.55` and the YuNet landmark anchor stride isolates each person independently.
- This prevents two people standing shoulder-to-shoulder from being merged into a single bounding box.

### Q4: How do I delete uploaded photos and start fresh?
- Click the red **"Delete Uploads"** button at the top of the dashboard.
- The server will remove all files in `output_multiframe/user_uploads/` and reset the slideshow to default baseline samples.

---

*Enjoy exploring the Multi-Agent Face Detection & Diagnostic Platform! For any questions, refer to [implementation_plan.md](implementation_plan.md) and [tasks_and_code_snippets.md](tasks_and_code_snippets.md).*
