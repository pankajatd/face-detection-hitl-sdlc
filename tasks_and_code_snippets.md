# Multi-Agent Face Detection & Diagnostic Platform
## Engineering Tasks & Code Snippets Reference

This document provides a comprehensive breakdown of all engineering tasks performed to build the autonomous multi-agent face detection platform, accompanied by exact code snippets for each task.

---

### Task 1: Define the Shared Agent State Machine Schema

**Objective**: Create a strongly-typed state schema that carries image buffers, detections, quality reports, and self-healing telemetry between all graph nodes.

**File**: [`src/graph/state.py`](file:///C:/Users/panka/.gemini/antigravity/scratch/multi_agent_face_detection/src/graph/state.py)

```python
from typing import TypedDict, List, Dict, Any
import numpy as np

class AgentState(TypedDict):
    """
    Immutable State schema passed across all nodes in the LangGraph workflow.
    """
    current_image: np.ndarray       # Active image buffer (modified by enhancer)
    original_image: np.ndarray      # Untouched input frame for audit comparison
    metadata: Dict[str, Any]        # Ground truth bounding boxes, resolution, degradation
    detections: List[Dict[str, Any]] # Detected face coordinates [x, y, w, h] + confidence
    quality_report: Dict[str, Any]  # Blur, luminance, contrast, and issue flags
    iteration_count: int            # Current cycle count in the self-healing loop
    max_iterations: int             # Maximum allowed retries before forced completion (default: 3)
    enhancement_history: List[str]  # Log of programmatic fixes applied (e.g. CLAHE, Unsharp)
    audit_report: Dict[str, Any]    # Final precision metrics, IoU, and gate verdict
```

---

### Task 2: Build the Face Detector Agent with OpenCV YuNet DNN

**Objective**: Implement Agent 1 using OpenCV's deep learning model (YuNet) for high-accuracy face detection, eliminating false positives on clothing and backgrounds.

**File**: [`src/detection/face_detector.py`](file:///C:/Users/panka/.gemini/antigravity/scratch/multi_agent_face_detection/src/detection/face_detector.py)

```python
import os
import cv2
import numpy as np
from typing import List, Dict, Any

class FaceDetectorAgent:
    def __init__(self):
        # 1. Primary Engine: OpenCV YuNet Deep Neural Network Face Detector
        self.yunet_detector = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        model_path = os.path.join(project_root, "models", "face_detection_yunet.onnx")

        if os.path.exists(model_path) and hasattr(cv2, "FaceDetectorYN"):
            try:
                self.yunet_detector = cv2.FaceDetectorYN.create(
                    model=model_path,
                    config="",
                    input_size=(320, 320),
                    score_threshold=0.60,
                    nms_threshold=0.30,
                    top_k=5000
                )
            except Exception:
                self.yunet_detector = None

    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        h, w = image.shape[:2]
        results = []

        # YuNet Deep Learning Detection
        if self.yunet_detector is not None:
            try:
                self.yunet_detector.setInputSize((w, h))
                _, faces = self.yunet_detector.detect(image)
                if faces is not None and len(faces) > 0:
                    for f in faces:
                        bx = max(0, int(f[0]))
                        by = max(0, int(f[1]))
                        bw = min(w - bx, int(f[2]))
                        bh = min(h - by, int(f[3]))
                        conf = round(float(f[-1]), 2)
                        if bw >= 16 and bh >= 16:
                            results.append({
                                "bbox": [bx, by, bw, bh],
                                "confidence": conf,
                                "detection_method": "yunet_dnn"
                            })
                    if results:
                        return results
            except Exception:
                pass

        return results
```

---

### Task 3: Build the Quality Inspector Agent

**Objective**: Implement Agent 2 to measure mathematical image flaws on detected face Regions of Interest (ROI): sharpness (Laplacian variance), illumination (luminance), and contrast.

**File**: [`src/quality/quality_inspector.py`](file:///C:/Users/panka/.gemini/antigravity/scratch/multi_agent_face_detection/src/quality/quality_inspector.py)

```python
import cv2
import numpy as np
from typing import Dict, Any, List

class QualityInspectorAgent:
    def inspect_quality(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not detections:
            return {"status": "NO_FACE_DETECTED", "quality_score": 0.0, "issues": ["NO_FACE_FOUND"]}

        bbox = detections[0]["bbox"]
        x, y, w, h = bbox
        img_h, img_w = image.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(img_w, x + w), min(img_h, y + h)

        face_crop = image[y1:y2, x1:x2]
        if face_crop.size == 0:
            face_crop = image

        gray_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)

        # 1. Blur Detection via Variance of Laplacian
        laplacian_var = float(cv2.Laplacian(gray_face, cv2.CV_64F).var())

        # 2. Mean Luminance Check
        mean_luminance = float(np.mean(gray_face))

        # 3. Contrast Standard Deviation
        contrast_std = float(np.std(gray_face))

        issues = []
        if laplacian_var < 110.0:
            issues.append("BLURRY")
        if mean_luminance < 75.0:
            issues.append("UNDER_EXPOSED")
        elif mean_luminance > 215.0:
            issues.append("OVER_EXPOSED")
        if contrast_std < 25.0:
            issues.append("LOW_CONTRAST")

        # Composite quality score calculation (0 - 100)
        quality_score = min(100.0, round(
            (min(laplacian_var, 300) / 300 * 40) +
            (max(0, 100 - abs(mean_luminance - 128)) / 100 * 35) +
            (min(contrast_std, 60) / 60 * 25), 1
        ))

        return {
            "status": "ACCEPTABLE" if not issues else "NEEDS_ENHANCEMENT",
            "quality_score": quality_score,
            "blur_score": laplacian_var,
            "luminance": mean_luminance,
            "contrast": contrast_std,
            "issues": issues
        }
```

---

### Task 4: Build the Autonomous Self-Healing Image Enhancer Agent

**Objective**: Implement Agent 3 to autonomously fix defects diagnosed by Agent 2 before re-testing.

**File**: [`src/enhancement/image_enhancer.py`](file:///C:/Users/panka/.gemini/antigravity/scratch/multi_agent_face_detection/src/enhancement/image_enhancer.py)

```python
import cv2
import numpy as np
from typing import Dict, Any, Tuple

class ImageEnhancerAgent:
    def enhance_image(self, image: np.ndarray, quality_report: Dict[str, Any]) -> Tuple[np.ndarray, str]:
        issues = quality_report.get("issues", [])
        enhanced = image.copy()
        applied_action = "NO_ACTION"

        # Fix 1: Under-exposure / Darkness -> Apply CLAHE in LAB color space
        if "UNDER_EXPOSED" in issues:
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)
            applied_action = "CLAHE_BRIGHTNESS_BOOST"

        # Fix 2: Blur -> Apply Unsharp Masking
        elif "BLURRY" in issues:
            gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
            enhanced = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
            applied_action = "UNSHARP_MASK_SHARPENING"

        # Fix 3: Low Contrast -> Apply Histogram Equalization
        elif "LOW_CONTRAST" in issues:
            ycrcb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2YCrCb)
            channels = list(cv2.split(ycrcb))
            channels[0] = cv2.equalizeHist(channels[0])
            enhanced = cv2.cvtColor(cv2.merge(channels), cv2.COLOR_YCrCb2BGR)
            applied_action = "HISTOGRAM_EQUALIZATION"

        return enhanced, applied_action
```

---

### Task 5: Build the Test Auditor Agent

**Objective**: Implement Agent 4 to evaluate precision, compute IoU against ground truth, and assign final gate verdicts.

**File**: [`src/audit/test_auditor.py`](file:///C:/Users/panka/.gemini/antigravity/scratch/multi_agent_face_detection/src/audit/test_auditor.py)

```python
from typing import Dict, Any, List

class TestAuditorAgent:
    @staticmethod
    def calculate_iou(boxA: List[int], boxB: List[int]) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]
        denom = float(boxAArea + boxBArea - interArea)
        return round(interArea / denom, 3) if denom > 0 else 0.0

    def generate_audit_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        detections = state.get("detections", [])
        quality = state.get("quality_report", {})
        meta = state.get("metadata", {})
        iterations = state.get("iteration_count", 1)

        detected_bbox = detections[0]["bbox"] if detections else None
        gt_bbox = meta.get("ground_truth_bbox", None)
        iou_score = self.calculate_iou(detected_bbox, gt_bbox) if (detected_bbox and gt_bbox) else 0.0

        if detections and (quality.get("quality_score", 0) >= 60.0 or iou_score > 0.4):
            verdict = "PASSED_FIRST_TRY" if iterations == 1 else "PASSED_AFTER_SELF_HEALING"
        else:
            verdict = "FAILED_QUALITY_GATE"

        return {
            "verdict": verdict,
            "face_detected": len(detections) > 0,
            "detection_count": len(detections),
            "primary_bbox": detected_bbox,
            "iou_vs_ground_truth": iou_score,
            "final_quality_score": quality.get("quality_score", 0.0),
            "self_healing_iterations": iterations - 1,
            "applied_enhancements": state.get("enhancement_history", [])
        }
```

---

### Task 6: Assemble the Multi-Agent Orchestrator Graph

**Objective**: Wire all 4 agents into a LangGraph StateGraph with conditional self-healing edges.

**File**: [`src/graph/workflow.py`](file:///C:/Users/panka/.gemini/antigravity/scratch/multi_agent_face_detection/src/graph/workflow.py)

```python
class MultiAgentFaceOrchestrator:
    def __init__(self):
        self.detector_agent = FaceDetectorAgent()
        self.quality_agent = QualityInspectorAgent()
        self.enhancer_agent = ImageEnhancerAgent()
        self.auditor_agent = TestAuditorAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = GraphClass(AgentState)

        # 1. Register Agents as Graph Nodes
        workflow.add_node("detector_node", self.node_detector)
        workflow.add_node("quality_node", self.node_quality_inspector)
        workflow.add_node("enhancer_node", self.node_enhancer)
        workflow.add_node("auditor_node", self.node_auditor)

        # 2. Linear & Conditional Edge Connections
        workflow.set_entry_point("detector_node")
        workflow.add_edge("detector_node", "quality_node")

        # Conditional Self-Healing Decision Gate
        workflow.add_conditional_edges(
            "quality_node",
            self.route_quality_decision,
            {
                "retry_enhancement": "enhancer_node",
                "proceed_to_audit": "auditor_node"
            }
        )

        # Cyclic Edge: Loop back from Enhancer Agent to Detector Agent
        workflow.add_edge("enhancer_node", "detector_node")
        workflow.add_edge("auditor_node", END_NODE)

        return workflow.compile()

    def route_quality_decision(self, state: AgentState) -> str:
        quality_status = state["quality_report"].get("status", "ACCEPTABLE")
        iterations = state.get("iteration_count", 1)
        max_iters = state.get("max_iterations", 3)

        if quality_status in ["EXCELLENT", "ACCEPTABLE"] or iterations >= max_iters:
            return "proceed_to_audit"
        else:
            return "retry_enhancement"
```

---

### Task 7: Spectacle Artifact Suppression & Multi-Face Preservation

**Objective**: Prevent duplicate sub-boxes from appearing on spectacles while ensuring distinct people standing next to each other are never merged.

**File**: [`src/detection/face_detector.py`](file:///C:/Users/panka/.gemini/antigravity/scratch/multi_agent_face_detection/src/detection/face_detector.py)

```python
    @staticmethod
    def suppress_nested_and_overlapping_boxes(boxes: List[List[int]], iou_thresh: float = 0.55, containment_thresh: float = 0.70) -> List[List[int]]:
        """
        Suppresses nested boxes (spectacle sub-boxes) while preserving distinct adjacent faces.
        """
        if len(boxes) <= 1:
            return boxes

        boxes = sorted(boxes, key=lambda b: b[2] * b[3], reverse=True)
        keep = []

        for boxA in boxes:
            xA, yA, wA, hA = boxA
            areaA = wA * hA
            is_duplicate = False

            for kept in keep:
                xK, yK, wK, hK = kept
                areaK = wK * hK

                ix1 = max(xA, xK)
                iy1 = max(yA, yK)
                ix2 = min(xA + wA, xK + wK)
                iy2 = min(yA + hA, yK + hK)

                inter_w = max(0, ix2 - ix1)
                inter_h = max(0, iy2 - iy1)
                inter_area = inter_w * inter_h

                if inter_area > 0:
                    iou = inter_area / float(areaA + areaK - inter_area)
                    containmentA = inter_area / float(areaA)

                    # Only suppress if boxA is largely nested INSIDE an existing face box
                    if containmentA >= containment_thresh or iou >= iou_thresh:
                        is_duplicate = True
                        break

            if not is_duplicate:
                keep.append(boxA)

        return keep
```

---

### Task 8: Build the HTTP Server with Persistent Upload Storage & Delete API

**Objective**: Provide a local HTTP server that exposes `/api/upload_detect`, `/api/delete_uploads`, and `/api/slides` with CORS support and automated browser launch.

**File**: [`server.py`](file:///C:/Users/panka/.gemini/antigravity/scratch/multi_agent_face_detection/server.py)

```python
    def do_POST(self):
        url_path = urllib.parse.urlparse(self.path).path
        
        # Endpoint: Delete all uploads and reset folder
        if url_path == "/api/delete_uploads":
            deleted_count = 0
            if os.path.exists(UPLOAD_DIR):
                for fname in os.listdir(UPLOAD_DIR):
                    fpath = os.path.join(UPLOAD_DIR, fname)
                    if os.path.isfile(fpath):
                        os.remove(fpath)
                        deleted_count += 1
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Cleaned fresh!"}).encode("utf-8"))
            return

        # Endpoint: Process uploaded gallery picture through Multi-Agent Graph
        elif url_path == "/api/upload_detect":
            content_len = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(content_len).decode("utf-8"))

            img_b64 = data.get("image", "").split(",")[-1]
            img = cv2.imdecode(np.frombuffer(base64.b64decode(img_b64), np.uint8), cv2.IMREAD_COLOR)

            # Execute Multi-Agent Graph
            final_state = orchestrator.run(img, metadata={"filename": data.get("name")}, max_iterations=3)
            detections = final_state.get("detections", [])

            # Draw separate bounding boxes for each face
            output_img = final_state.get("current_image", img).copy()
            for det in detections:
                bx, by, bw, bh = det["bbox"]
                cv2.rectangle(output_img, (bx, by), (bx + bw, by + bh), (0, 255, 0), 3)

            # Save and send JSON response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "faces_count": len(detections),
                "detections": detections,
                "quality_score": final_state["audit_report"]["final_quality_score"],
                "verdict": final_state["audit_report"]["verdict"]
            }).encode("utf-8"))
```
