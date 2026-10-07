import cv2
import numpy as np
from typing import Tuple, Dict, Any

class ImageEnhancerWorker:
    """
    Task 2 Algorithmic Worker: Auto-Fix / Enhancer.
    Applies adaptive histogram equalization (CLAHE) on Lab color space,
    gamma correction for underexposed shadows, and unsharp masking for defocus blur.
    """
    def enhance_image(self, image: np.ndarray, issue_type: str = "auto") -> Tuple[np.ndarray, str]:
        if image is None:
            raise ValueError("Input image cannot be None")
            
        enhanced = image.copy()
        
        # If auto, compute brightness & blur to choose enhancement
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_lum = float(np.mean(gray))
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        if issue_type == "dark" or (issue_type == "auto" and mean_lum < 80.0):
            # CLAHE on Lab luminance channel + Gamma brightening
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l)
            lab_enhanced = cv2.merge((l_enhanced, a, b))
            enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
            
            gamma = 1.6
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
            enhanced = cv2.LUT(enhanced, table)
            action = "CLAHE_BRIGHTNESS_BOOST"
            
        elif issue_type == "blur" or (issue_type == "auto" and laplacian_var < 100.0):
            # High-pass sharpening & unsharp masking
            gaussian = cv2.GaussianBlur(enhanced, (0, 0), sigmaX=3.0)
            enhanced = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            action = "UNSHARP_MASK_SHARPENING"
            
        else:
            # Contrast normalization
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l)
            enhanced = cv2.cvtColor(cv2.merge((l_enhanced, a, b)), cv2.COLOR_LAB2BGR)
            action = "STANDARD_CONTRAST_NORMALIZATION"
            
        return enhanced, action
