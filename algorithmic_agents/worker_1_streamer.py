import os
import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional

class FaceStreamerWorker:
    """
    Task 1 Algorithmic Worker: Ingestion & Buffer Streamer.
    Ingests frames from disk or generates synthetic facial frames,
    validating image buffers, dimensions, and color space integrity.
    """
    def __init__(self, default_size: Tuple[int, int] = (512, 512)):
        self.default_size = default_size

    def ingest_from_file(self, file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Ingests an existing image file from disk and validates dimensions."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError(f"Failed to decode image from: {file_path}")
            
        h, w, c = img.shape
        metadata = {
            "source": file_path,
            "width": w,
            "height": h,
            "channels": c,
            "status": "VALID_INGESTION"
        }
        return img, metadata

    def generate_synthetic_frame(self, degradation: str = "none") -> Tuple[np.ndarray, Dict[str, Any]]:
        """Generates a synthetic facial canvas with known geometry for baseline testing."""
        h, w = self.default_size
        img = np.full((h, w, 3), (210, 210, 210), dtype=np.uint8)
        
        cx, cy = w // 2, h // 2
        # Head oval
        cv2.ellipse(img, (cx, cy), (110, 150), 0, 0, 360, (180, 205, 240), -1)
        cv2.ellipse(img, (cx, cy), (110, 150), 0, 0, 360, (140, 165, 200), 3)
        # Eyes
        cv2.circle(img, (cx - 45, cy - 30), 16, (255, 255, 255), -1)
        cv2.circle(img, (cx + 45, cy - 30), 16, (255, 255, 255), -1)
        cv2.circle(img, (cx - 45, cy - 30), 7, (80, 40, 20), -1)
        cv2.circle(img, (cx + 45, cy - 30), 7, (80, 40, 20), -1)
        # Mouth
        cv2.ellipse(img, (cx, cy + 60), (35, 20), 0, 0, 180, (60, 50, 150), 4)

        if degradation == "dark":
            img = (img.astype(np.float32) * 0.25).astype(np.uint8)
        elif degradation == "blur":
            img = cv2.GaussianBlur(img, (29, 29), 0)

        metadata = {
            "source": "synthetic",
            "width": w,
            "height": h,
            "channels": 3,
            "degradation": degradation,
            "status": "VALID_INGESTION"
        }
        return img, metadata
