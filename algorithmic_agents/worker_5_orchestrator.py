import time
import cv2
import numpy as np
from typing import Dict, Any, List

from .worker_1_streamer import FaceStreamerWorker
from .worker_2_enhancer import ImageEnhancerWorker
from .worker_3_detector import FaceDetectorWorker
from .worker_4_inspector import QualityInspectorWorker

class MultiAgentFacePipeline:
    """
    Task 5 Algorithmic Worker: End-to-End Multi-Agent Pipeline.
    Orchestrates Streamer -> Enhancer -> Detector -> Quality Inspector
    with an autonomous self-healing closed loop.
    """
    def __init__(self):
        self.streamer = FaceStreamerWorker()
        self.enhancer = ImageEnhancerWorker()
        self.detector = FaceDetectorWorker()
        self.inspector = QualityInspectorWorker()

    def run_pipeline(self, image_path_or_array, auto_heal: bool = True) -> Dict[str, Any]:
        start_time = time.time()
        trace = []

        # 1. Ingestion
        if isinstance(image_path_or_array, str):
            raw_img, meta = self.streamer.ingest_from_file(image_path_or_array)
            trace.append(f"[Worker 1: Streamer] Ingested file: {meta['source']} ({meta['width']}x{meta['height']}).")
        elif isinstance(image_path_or_array, np.ndarray):
            raw_img = image_path_or_array.copy()
            h, w = raw_img.shape[:2]
            meta = {"source": "in-memory", "width": w, "height": h}
            trace.append(f"[Worker 1: Streamer] Ingested buffer ({w}x{h}).")
        else:
            raw_img, meta = self.streamer.generate_synthetic_frame()
            trace.append(f"[Worker 1: Streamer] Ingested synthetic frame ({meta['width']}x{meta['height']}).")

        # 2. Initial Face Detection
        detections = self.detector.detect_faces(raw_img)
        trace.append(f"[Worker 3: Detector] Initial scan detected {len(detections)} face(s).")

        # 3. Quality Inspection
        quality = self.inspector.inspect(raw_img, detections)
        trace.append(f"[Worker 4: Inspector] Quality: {quality['status']} (Sharpness: {quality['sharpness_score']}/100, Issues: {quality['issues']}).")

        processed_img = raw_img.copy()
        healed = False
        action_taken = "NONE"

        # 4. Self-Healing Condition (if quality degraded or 0 faces with issues)
        if auto_heal and (quality["status"] == "DEGRADED" or len(detections) == 0):
            issue = quality["issues"][0] if quality["issues"] and quality["issues"][0] != "NO_FACE_FOUND" else "auto"
            processed_img, action_taken = self.enhancer.enhance_image(raw_img, issue)
            healed = True
            trace.append(f"[Worker 2: Enhancer] Self-Healing triggered: Applied {action_taken}.")

            # Re-detect after healing
            re_detections = self.detector.detect_faces(processed_img)
            trace.append(f"[Worker 3: Detector] Post-heal scan detected {len(re_detections)} face(s).")
            if len(re_detections) >= len(detections):
                detections = re_detections
                quality = self.inspector.inspect(processed_img, detections)
                trace.append(f"[Worker 4: Inspector] Post-heal Quality: {quality['status']}.")

        # 5. Visual Rendering
        annotated_img = self.detector.draw_detections(processed_img, detections)
        total_latency_ms = round((time.time() - start_time) * 1000, 1)
        trace.append(f"[Pipeline Complete] End-to-end latency: {total_latency_ms}ms.")

        return {
            "raw_image": raw_img,
            "processed_image": processed_img,
            "annotated_image": annotated_img,
            "detections": detections,
            "quality": quality,
            "healed": healed,
            "heal_action": action_taken,
            "latency_ms": total_latency_ms,
            "execution_trace": trace,
            "status": "SUCCESS"
        }
