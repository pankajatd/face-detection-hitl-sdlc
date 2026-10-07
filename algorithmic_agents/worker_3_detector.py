import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple

class FaceDetectorWorker:
    """
    Task 3 Algorithmic Worker: Deep Learning Face Detector (YuNet + Haar fallback).
    Detects faces, computes confidence scores, and returns bounding boxes & 5 facial landmarks.
    """
    def __init__(self, model_path: str = None):
        if model_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            model_path = os.path.join(project_root, "models", "face_detection_yunet.onnx")

        self.model_path = model_path
        self.yunet_available = False
        self.haar_cascade = None

        # 1. Primary: YuNet Deep Learning ONNX
        if os.path.exists(self.model_path) and hasattr(cv2, "FaceDetectorYN"):
            try:
                # Initialize placeholder detector; will set input_size on detect
                self.yunet_detector = cv2.FaceDetectorYN.create(
                    model=self.model_path,
                    config="",
                    input_size=(320, 320),
                    score_threshold=0.55,
                    nms_threshold=0.30,
                    top_k=5000
                )
                self.yunet_available = True
            except Exception:
                self.yunet_available = False

        # 2. Secondary: Haar Cascade Fallback
        if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data"):
            try:
                p = cv2.data.haarcascades
                alt_path = os.path.join(p, 'haarcascade_frontalface_alt2.xml')
                def_path = os.path.join(p, 'haarcascade_frontalface_default.xml')
                chosen = alt_path if os.path.exists(alt_path) else def_path
                if os.path.exists(chosen):
                    c = cv2.CascadeClassifier(chosen)
                    if not c.empty():
                        self.haar_cascade = c
            except Exception:
                pass

    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detects faces in BGR image and returns bounding boxes and landmarks."""
        if image is None:
            return []

        h, w = image.shape[:2]
        detections = []

        # Try YuNet first
        if self.yunet_available:
            try:
                self.yunet_detector.setInputSize((w, h))
                ret, faces = self.yunet_detector.detect(image)
                if faces is not None:
                    for face in faces:
                        box = [int(face[0]), int(face[1]), int(face[2]), int(face[3])]
                        conf = float(face[-1])
                        # 5 facial landmarks (right eye, left eye, nose tip, right mouth, left mouth)
                        landmarks = []
                        if len(face) >= 14:
                            for i in range(4, 14, 2):
                                landmarks.append([int(face[i]), int(face[i+1])])
                        detections.append({
                            "bbox": box,
                            "confidence": round(conf, 4),
                            "landmarks": landmarks,
                            "engine": "YuNet_DNN"
                        })
                    return detections
            except Exception:
                pass

        # Haar fallback
        if self.haar_cascade is not None:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            for (x, y, fw, fh) in faces:
                detections.append({
                    "bbox": [int(x), int(y), int(fw), int(fh)],
                    "confidence": 0.88,
                    "landmarks": [],
                    "engine": "Haar_Cascade"
                })

        return detections

    def draw_detections(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """Renders green bounding boxes and facial landmark points on the image."""
        vis = image.copy()
        for det in detections:
            x, y, w, h = det["bbox"]
            conf = det["confidence"]
            engine = det.get("engine", "Detector")
            
            # Green bounding box
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Label banner
            label = f"{engine}: {int(conf * 100)}%"
            cv2.putText(vis, label, (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw landmarks if present (cyan dots)
            for pt in det.get("landmarks", []):
                cv2.circle(vis, (pt[0], pt[1]), 3, (255, 255, 0), -1)

        return vis
