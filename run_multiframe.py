"""
Multi-Frame Face Detection Demo with Dashboard
Uses synthetic emoji faces with varied conditions to simulate a video stream.
Produces a multi-frame grid dashboard showing detection results across all frames.
"""
import cv2
import numpy as np
import time
import os
import json

from src.detection.face_detector import FaceDetectorAgent
from src.quality.quality_inspector import QualityInspectorAgent
from src.enhancement.image_enhancer import ImageEnhancerAgent
from src.audit.test_auditor import TestAuditorAgent
from src.graph.workflow import MultiAgentFaceOrchestrator


class MultiFaceStreamer:
    """Generates diverse synthetic face frames simulating a video feed."""

    def __init__(self, img_size=(400, 400)):
        self.height, self.width = img_size

    def _draw_face(self, img, cx, cy, scale=1.0, skin_color=(180, 205, 240),
                   eye_style="normal", mouth_style="smile", has_glasses=False):
        """Draws a single emoji-style face at given position and scale."""
        # Head oval
        ax = int(80 * scale)
        ay = int(110 * scale)
        cv2.ellipse(img, (cx, cy), (ax, ay), 0, 0, 360, skin_color, -1)
        cv2.ellipse(img, (cx, cy), (ax, ay), 0, 0, 360, 
                    tuple(max(0, c - 40) for c in skin_color), 2)

        # Eyes
        eye_y = cy - int(25 * scale)
        left_x = cx - int(30 * scale)
        right_x = cx + int(30 * scale)
        eye_r = int(12 * scale)
        pupil_r = int(5 * scale)

        # White of eyes
        cv2.circle(img, (left_x, eye_y), eye_r, (255, 255, 255), -1)
        cv2.circle(img, (right_x, eye_y), eye_r, (255, 255, 255), -1)

        if eye_style == "normal":
            cv2.circle(img, (left_x, eye_y), pupil_r, (60, 30, 10), -1)
            cv2.circle(img, (right_x, eye_y), pupil_r, (60, 30, 10), -1)
        elif eye_style == "surprised":
            cv2.circle(img, (left_x, eye_y), pupil_r + 2, (60, 30, 10), -1)
            cv2.circle(img, (right_x, eye_y), pupil_r + 2, (60, 30, 10), -1)
        elif eye_style == "closed":
            cv2.line(img, (left_x - eye_r, eye_y), (left_x + eye_r, eye_y), (60, 30, 10), 2)
            cv2.line(img, (right_x - eye_r, eye_y), (right_x + eye_r, eye_y), (60, 30, 10), 2)
        elif eye_style == "wink":
            cv2.circle(img, (left_x, eye_y), pupil_r, (60, 30, 10), -1)
            cv2.line(img, (right_x - eye_r, eye_y), (right_x + eye_r, eye_y), (60, 30, 10), 2)

        # Eyebrows
        brow_y = eye_y - int(18 * scale)
        cv2.line(img, (left_x - int(15*scale), brow_y), (left_x + int(15*scale), brow_y - 3),
                 (40, 30, 20), max(2, int(3*scale)))
        cv2.line(img, (right_x - int(15*scale), brow_y - 3), (right_x + int(15*scale), brow_y),
                 (40, 30, 20), max(2, int(3*scale)))

        # Nose
        nose_y = cy + int(5 * scale)
        nose_pts = np.array([
            [cx, nose_y - int(8*scale)],
            [cx - int(8*scale), nose_y + int(15*scale)],
            [cx + int(8*scale), nose_y + int(15*scale)]
        ], np.int32)
        cv2.polylines(img, [nose_pts], False, tuple(max(0, c-30) for c in skin_color), 2)

        # Mouth
        mouth_y = cy + int(45 * scale)
        if mouth_style == "smile":
            cv2.ellipse(img, (cx, mouth_y), (int(25*scale), int(15*scale)),
                        0, 0, 180, (50, 50, 180), max(2, int(3*scale)))
        elif mouth_style == "open":
            cv2.ellipse(img, (cx, mouth_y), (int(20*scale), int(18*scale)),
                        0, 0, 360, (50, 50, 180), -1)
            cv2.ellipse(img, (cx, mouth_y - int(5*scale)), (int(15*scale), int(8*scale)),
                        0, 0, 360, (100, 60, 60), -1)
        elif mouth_style == "neutral":
            cv2.line(img, (cx - int(20*scale), mouth_y), (cx + int(20*scale), mouth_y),
                     (50, 50, 180), max(2, int(3*scale)))
        elif mouth_style == "frown":
            cv2.ellipse(img, (cx, mouth_y + int(15*scale)), (int(25*scale), int(15*scale)),
                        0, 180, 360, (50, 50, 180), max(2, int(3*scale)))

        # Glasses
        if has_glasses:
            g_y = eye_y
            g_r = int(16 * scale)
            cv2.circle(img, (left_x, g_y), g_r, (40, 40, 40), 2)
            cv2.circle(img, (right_x, g_y), g_r, (40, 40, 40), 2)
            cv2.line(img, (left_x + g_r, g_y), (right_x - g_r, g_y), (40, 40, 40), 2)
            cv2.line(img, (left_x - g_r, g_y), (left_x - g_r - int(10*scale), g_y - int(5*scale)),
                     (40, 40, 40), 2)
            cv2.line(img, (right_x + g_r, g_y), (right_x + g_r + int(10*scale), g_y - int(5*scale)),
                     (40, 40, 40), 2)

        return [cx - ax, cy - ay, ax * 2, ay * 2]

    def generate_frames(self):
        """Generate 8 diverse frames simulating a video feed."""
        frames = []

        # --- Frame 1: Single face, clear ---
        img = np.full((self.height, self.width, 3), (220, 220, 230), dtype=np.uint8)
        gt = self._draw_face(img, 200, 200, scale=1.0, mouth_style="smile")
        frames.append(("F01_Single_Clear", img, "none", 0.0, [gt]))

        # --- Frame 2: Single face, different position ---
        img = np.full((self.height, self.width, 3), (200, 215, 230), dtype=np.uint8)
        gt = self._draw_face(img, 150, 180, scale=0.9, skin_color=(160, 190, 230),
                             eye_style="wink", mouth_style="smile")
        frames.append(("F02_Offset_Wink", img, "none", 0.0, [gt]))

        # --- Frame 3: Face with glasses ---
        img = np.full((self.height, self.width, 3), (210, 210, 220), dtype=np.uint8)
        gt = self._draw_face(img, 200, 200, scale=1.1, skin_color=(190, 210, 240),
                             has_glasses=True, mouth_style="neutral")
        frames.append(("F03_Glasses", img, "none", 0.0, [gt]))

        # --- Frame 4: Under-exposed / dark ---
        img = np.full((self.height, self.width, 3), (210, 210, 220), dtype=np.uint8)
        gt = self._draw_face(img, 200, 200, scale=1.0, mouth_style="frown")
        img = np.clip(img.astype(np.float32) * 0.25, 0, 255).astype(np.uint8)
        frames.append(("F04_Dark_Underexposed", img, "under_exposed", 0.85, [gt]))

        # --- Frame 5: Blurry frame ---
        img = np.full((self.height, self.width, 3), (215, 220, 225), dtype=np.uint8)
        gt = self._draw_face(img, 200, 200, scale=1.0, eye_style="surprised",
                             mouth_style="open")
        img = cv2.GaussianBlur(img, (21, 21), 0)
        frames.append(("F05_Blurry", img, "blur", 0.8, [gt]))

        # --- Frame 6: Two faces ---
        img = np.full((self.height, self.width, 3), (200, 210, 225), dtype=np.uint8)
        gt1 = self._draw_face(img, 120, 200, scale=0.7, skin_color=(180, 205, 240),
                              mouth_style="smile")
        gt2 = self._draw_face(img, 290, 190, scale=0.75, skin_color=(165, 195, 225),
                              eye_style="wink", mouth_style="open", has_glasses=True)
        frames.append(("F06_Two_Faces", img, "none", 0.0, [gt1, gt2]))

        # --- Frame 7: Noisy frame ---
        img = np.full((self.height, self.width, 3), (210, 215, 220), dtype=np.uint8)
        gt = self._draw_face(img, 200, 200, scale=1.0, eye_style="closed",
                             mouth_style="neutral")
        noise = np.random.normal(0, 30, img.shape).astype(np.float32)
        img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        frames.append(("F07_Noisy", img, "noise", 0.7, [gt]))

        # --- Frame 8: Small face, far away ---
        img = np.full((self.height, self.width, 3), (225, 225, 230), dtype=np.uint8)
        gt = self._draw_face(img, 200, 200, scale=0.55, skin_color=(175, 200, 235),
                             mouth_style="smile", has_glasses=True)
        frames.append(("F08_Small_Distant", img, "none", 0.0, [gt]))

        return frames


def draw_frame_tile(image, detections, quality_report, audit_report, frame_label, tile_size=(350, 300)):
    """Draw a single frame tile with detection overlay and stats for the dashboard."""
    tw, th = tile_size

    # Resize image to fit tile
    img_h, img_w = image.shape[:2]
    scale = min((tw - 20) / img_w, (th - 80) / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    resized = cv2.resize(image, (new_w, new_h))

    # Create tile canvas
    tile = np.full((th, tw, 3), (35, 35, 40), dtype=np.uint8)

    # Center image in tile
    x_off = (tw - new_w) // 2
    y_off = 5
    tile[y_off:y_off + new_h, x_off:x_off + new_w] = resized

    # Draw scaled bounding boxes
    for det in detections:
        bbox = det["bbox"]
        x, y, w, h = bbox
        sx = int(x * scale) + x_off
        sy = int(y * scale) + y_off
        sw = int(w * scale)
        sh = int(h * scale)
        conf = det.get("confidence", 0)

        verdict = audit_report.get("verdict", "")
        color = (0, 255, 0) if "PASSED" in verdict else (0, 165, 255)
        cv2.rectangle(tile, (sx, sy), (sx + sw, sy + sh), color, 2)
        cv2.putText(tile, f"{conf*100:.0f}%", (sx, max(12, sy - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    # Stats bar at bottom
    bar_y = th - 70
    cv2.rectangle(tile, (0, bar_y), (tw, th), (25, 25, 30), -1)

    # Frame label
    cv2.putText(tile, frame_label, (5, bar_y + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Quality score
    score = quality_report.get("quality_score", 0)
    score_color = (0, 255, 0) if score >= 75 else (0, 165, 255) if score >= 50 else (0, 0, 255)
    cv2.putText(tile, f"Score: {score:.0f}/100", (5, bar_y + 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, score_color, 1)

    # Verdict
    verdict = audit_report.get("verdict", "N/A")
    short_verdict = verdict.replace("PASSED_", "P:").replace("AFTER_SELF_HEALING", "HEALED").replace("FIRST_TRY", "1ST")
    v_color = (0, 255, 0) if "PASSED" in verdict else (0, 0, 255)
    cv2.putText(tile, short_verdict, (5, bar_y + 48),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, v_color, 1)

    # Faces count & retries
    n_faces = len(detections)
    retries = audit_report.get("self_healing_iterations", 0)
    cv2.putText(tile, f"Faces: {n_faces} | Retries: {retries}", (5, bar_y + 63),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1)

    # Issues
    issues = quality_report.get("issues", [])
    if issues:
        issue_text = ", ".join(issues[:2])
        cv2.putText(tile, issue_text, (tw // 2, bar_y + 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (100, 100, 255), 1)

    # Enhancement applied
    enhancements = audit_report.get("applied_enhancements", [])
    if enhancements:
        enh_short = enhancements[-1][:20]
        cv2.putText(tile, f"Fix: {enh_short}", (tw // 2, bar_y + 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (255, 200, 100), 1)

    return tile


def build_multi_frame_dashboard(frame_results, tile_size=(350, 300)):
    """Build a grid dashboard from all frame results."""
    tw, th = tile_size
    n = len(frame_results)

    # Grid layout: 4 columns
    cols = 4
    rows = (n + cols - 1) // cols

    # Header height
    header_h = 80
    # Summary bar height
    summary_h = 60

    canvas_w = cols * tw + (cols + 1) * 8
    canvas_h = header_h + rows * (th + 8) + 8 + summary_h

    canvas = np.full((canvas_h, canvas_w, 3), (20, 20, 25), dtype=np.uint8)

    # --- Header ---
    cv2.rectangle(canvas, (0, 0), (canvas_w, header_h), (30, 30, 35), -1)
    cv2.putText(canvas, "MULTI-AGENT FACE DETECTION - MULTI-FRAME VIDEO DASHBOARD",
                (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    total_faces = sum(r["detection_count"] for r in frame_results)
    total_passed = sum(1 for r in frame_results if "PASSED" in r.get("verdict", ""))
    avg_score = np.mean([r["quality_score"] for r in frame_results])
    total_retries = sum(r.get("retries", 0) for r in frame_results)

    cv2.putText(canvas,
                f"Frames: {n} | Faces Detected: {total_faces} | "
                f"Passed: {total_passed}/{n} | Avg Score: {avg_score:.1f} | "
                f"Total Retries: {total_retries}",
                (15, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 220, 255), 1)

    # --- Agent Pipeline Legend ---
    cv2.putText(canvas,
                "Pipeline: Detector -> Quality Inspector -> [Self-Healing Loop] -> Auditor",
                (15, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (120, 120, 130), 1)

    # --- Frame Tiles ---
    for idx, result in enumerate(frame_results):
        row = idx // cols
        col = idx % cols
        x = 8 + col * (tw + 8)
        y = header_h + 8 + row * (th + 8)

        tile = draw_frame_tile(
            result["output_image"],
            result["detections"],
            result["quality_report"],
            result["audit_report"],
            result["frame_label"],
            tile_size
        )
        canvas[y:y + th, x:x + tw] = tile

    # --- Summary Bar ---
    sy = canvas_h - summary_h
    cv2.rectangle(canvas, (0, sy), (canvas_w, canvas_h), (30, 35, 30), -1)

    # Per-frame mini score bar
    bar_start_x = 15
    cv2.putText(canvas, "Frame Scores:", (bar_start_x, sy + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    for idx, r in enumerate(frame_results):
        bx = bar_start_x + 120 + idx * (canvas_w - 150) // n
        score = r["quality_score"]
        bar_h = int(score / 100.0 * 35)
        color = (0, 255, 0) if score >= 75 else (0, 165, 255) if score >= 50 else (0, 0, 255)
        cv2.rectangle(canvas, (bx, sy + 45 - bar_h), (bx + 25, sy + 45), color, -1)
        cv2.putText(canvas, f"F{idx+1}", (bx, sy + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1)

    # Overall verdict
    overall = "ALL PASSED" if total_passed == n else f"{total_passed}/{n} PASSED"
    ov_color = (0, 255, 0) if total_passed == n else (0, 165, 255)
    cv2.putText(canvas, f"OVERALL: {overall}", (canvas_w - 250, sy + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, ov_color, 2)

    return canvas


def run_multi_frame_demo():
    print("=" * 70)
    print("  MULTI-AGENT FACE DETECTION - MULTI-FRAME VIDEO DASHBOARD DEMO")
    print("=" * 70)
    print()

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_multiframe")
    os.makedirs(output_dir, exist_ok=True)

    streamer = MultiFaceStreamer(img_size=(400, 400))
    orchestrator = MultiAgentFaceOrchestrator()

    frames = streamer.generate_frames()
    all_results = []

    for idx, (name, img, deg_type, severity, gt_bboxes) in enumerate(frames):
        print(f"  [{idx+1}/{len(frames)}] Processing: {name} ...", end=" ")

        # Save input frame
        input_path = os.path.join(output_dir, f"{name}_input.png")
        cv2.imwrite(input_path, img)

        meta = {
            "ground_truth_bbox": gt_bboxes[0] if gt_bboxes else [0, 0, 0, 0],
            "degradation": deg_type,
            "severity": severity,
            "image_size": [img.shape[1], img.shape[0]]
        }

        start_t = time.time()
        final_state = orchestrator.run(img, metadata=meta, max_iterations=3)
        latency_ms = round((time.time() - start_t) * 1000, 1)

        audit = final_state["audit_report"]
        quality = final_state["quality_report"]
        detections = final_state["detections"]

        # Save output frame with detections drawn
        output_img = final_state["current_image"].copy()
        for det in detections:
            bx, by, bw, bh = det["bbox"]
            verdict = audit.get("verdict", "")
            color = (0, 255, 0) if "PASSED" in verdict else (0, 0, 255)
            cv2.rectangle(output_img, (bx, by), (bx + bw, by + bh), color, 2)
            cv2.putText(output_img, f"{det['confidence']*100:.0f}%",
                        (bx, max(15, by - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        output_path = os.path.join(output_dir, f"{name}_output.png")
        cv2.imwrite(output_path, output_img)

        result = {
            "frame_label": name,
            "output_image": final_state["current_image"],
            "detections": detections,
            "quality_report": quality,
            "audit_report": audit,
            "quality_score": audit["final_quality_score"],
            "verdict": audit["verdict"],
            "detection_count": len(detections),
            "retries": final_state["iteration_count"] - 1,
            "enhancements": final_state["enhancement_history"],
            "latency_ms": latency_ms,
            "degradation": deg_type,
        }
        all_results.append(result)

        v = audit["verdict"]
        s = audit["final_quality_score"]
        n_det = len(detections)
        retries = final_state["iteration_count"] - 1
        print(f"Faces={n_det} | Score={s}/100 | Retries={retries} | {v} | {latency_ms}ms")

    # Build and save the multi-frame dashboard
    print("\n  Building multi-frame dashboard...")
    dashboard = build_multi_frame_dashboard(all_results)
    dashboard_path = os.path.join(output_dir, "MULTI_FRAME_DASHBOARD.png")
    cv2.imwrite(dashboard_path, dashboard)
    print(f"  Dashboard saved: {dashboard_path}")

    # Save JSON report
    json_results = []
    for r in all_results:
        jr = {k: v for k, v in r.items() if k != "output_image"}
        jr["detections"] = [{"bbox": d["bbox"], "confidence": d["confidence"],
                             "method": d.get("detection_method", "unknown")}
                            for d in r["detections"]]
        jr["quality_report"] = {k: v for k, v in r["quality_report"].items()}
        jr["audit_report"] = {k: v for k, v in r["audit_report"].items() if k != "primary_bbox"}
        json_results.append(jr)

    report_path = os.path.join(output_dir, "multiframe_report.json")
    with open(report_path, "w") as f:
        json.dump(json_results, f, indent=2, default=str)
    print(f"  JSON report saved: {report_path}")

    # Summary table
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  {'Frame':<28} {'Faces':>5} {'Score':>8} {'Retries':>8} {'Verdict':<28}")
    print("  " + "-" * 66)
    for r in all_results:
        print(f"  {r['frame_label']:<28} {r['detection_count']:>5} "
              f"{r['quality_score']:>6}/100 {r['retries']:>8} {r['verdict']:<28}")

    total_passed = sum(1 for r in all_results if "PASSED" in r["verdict"])
    avg_score = np.mean([r["quality_score"] for r in all_results])
    print("  " + "-" * 66)
    print(f"  OVERALL: {total_passed}/{len(all_results)} frames PASSED | "
          f"Avg Score: {avg_score:.1f}/100")
    print("=" * 70)
    print(f"\n  All outputs in: {output_dir}")


if __name__ == "__main__":
    run_multi_frame_demo()
