import cv2
import numpy as np
from typing import List, Dict, Any

class QualityInspectorWorker:
    """
    Task 4 Algorithmic Worker: Quality & Pose Inspector.
    Measures facial sharpness, illumination, contrast, and landmark alignment.
    """
    def inspect(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        if image is None:
            return {"status": "ERROR", "message": "Image is None"}
            
        if not detections:
            return {
                "status": "NO_FACE_DETECTED",
                "quality_score": 0.0,
                "sharpness": 0.0,
                "illumination": 0.0,
                "contrast": 0.0,
                "issues": ["NO_FACE_FOUND"]
            }

        # Analyze primary face region
        x, y, w, h = detections[0]["bbox"]
        img_h, img_w = image.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(img_w, x + w), min(img_h, y + h)

        face_crop = image[y1:y2, x1:x2]
        if face_crop.size == 0:
            face_crop = image

        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        
        # 1. Sharpness (Laplacian variance)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        sharpness_norm = min(100.0, (lap_var / 120.0) * 100.0)

        # 2. Illumination & Contrast
        mean_lum = float(np.mean(gray))
        contrast_std = float(np.std(gray))

        issues = []
        if lap_var < 50.0:
            issues.append("DEFOCUS_BLUR")
        if mean_lum < 75.0:
            issues.append("UNDER_EXPOSED")
        elif mean_lum > 220.0:
            issues.append("OVER_EXPOSED")
        if contrast_std < 25.0:
            issues.append("LOW_CONTRAST")

        # Pose assessment using landmarks
        landmarks = detections[0].get("landmarks", [])
        pose = "FRONTAL"
        if len(landmarks) >= 3:
            left_eye, right_eye, nose = landmarks[0], landmarks[1], landmarks[2]
            eye_dist = abs(right_eye[0] - left_eye[0])
            if eye_dist > 0:
                nose_rel_x = (nose[0] - left_eye[0]) / eye_dist
                if nose_rel_x < 0.35:
                    pose = "PROFILE_LEFT"
                elif nose_rel_x > 0.65:
                    pose = "PROFILE_RIGHT"

        status = "HIGH_QUALITY" if not issues else "ACCEPTABLE" if len(issues) == 1 else "DEGRADED"

        return {
            "status": status,
            "sharpness_score": round(sharpness_norm, 1),
            "laplacian_variance": round(lap_var, 1),
            "illumination": round(mean_lum, 1),
            "contrast": round(contrast_std, 1),
            "pose": pose,
            "issues": issues,
            "passed": len(issues) == 0 or status == "ACCEPTABLE"
        }
