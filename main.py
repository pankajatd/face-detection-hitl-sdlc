import cv2
import numpy as np
import time
import json

from src.generator.face_streamer import SyntheticFaceStreamer
from src.graph.workflow import MultiAgentFaceOrchestrator

def draw_dashboard_hud(original_img, final_img, state_results):
    """Renders a side-by-side visual HUD comparing Before vs After Self-Healing."""
    audit = state_results.get("audit_report", {})
    quality = state_results.get("quality_report", {})
    detections = state_results.get("detections", [])
    history = state_results.get("enhancement_history", [])

    h, w = original_img.shape[:2]

    # Draw detected bounding box on original and final image
    orig_draw = original_img.copy()
    final_draw = final_img.copy()

    if detections:
        bbox = detections[0]["bbox"]
        x, y, bw, bh = bbox
        verdict = audit.get("verdict", "")
        box_color = (0, 255, 0) if "PASSED" in verdict else (0, 0, 255)

        cv2.rectangle(orig_draw, (x, y), (x + bw, y + bh), (255, 200, 0), 2)
        cv2.putText(orig_draw, "INPUT FRAME", (x, max(20, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

        cv2.rectangle(final_draw, (x, y), (x + bw, y + bh), box_color, 3)
        cv2.putText(final_draw, f"FACE DETECTED ({detections[0]['confidence']*100:.0f}%)", (x, max(20, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

    # Combine side-by-side
    combined = np.hstack((orig_draw, final_draw))
    comb_h, comb_w = combined.shape[:2]

    # Draw top header banner
    banner = np.full((90, comb_w, 3), (30, 30, 30), dtype=np.uint8)
    cv2.putText(banner, "MULTI-AGENT FACE DETECTION & QUALITY DIAGNOSTIC PLATFORM", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    verdict_text = audit.get("verdict", "UNKNOWN")
    status_color = (0, 255, 0) if "PASSED" in verdict_text else (0, 0, 255)
    cv2.putText(banner, f"VERDICT: {verdict_text}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)

    iters = state_results.get("iteration_count", 1) - 1
    cv2.putText(banner, f"RETRIES: {iters} | SCORE: {audit.get('final_quality_score', 0.0)}/100", (comb_w - 380, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    full_canvas = np.vstack((banner, combined))
    return full_canvas


def run_demo():
    print("==========================================================")
    print("   MULTI-AGENT FACE DETECTION & DIAGNOSTIC SYSTEM (LangGraph)")
    print("==========================================================\n")

    streamer = SyntheticFaceStreamer(img_size=(450, 450))
    orchestrator = MultiAgentFaceOrchestrator()

    test_scenarios = [
        ("1. STANDARD_FACE", "none", 0.0),
        ("2. UNDER_EXPOSED_DARK_FACE", "under_exposed", 0.85),
        ("3. BLURRY_FACE", "blur", 0.75)
    ]

    for name, deg_type, severity in test_scenarios:
        print("----------------------------------------------------------")
        print(f"📸 SIMULATING TEST SCENARIO: {name}")
        print("----------------------------------------------------------")

        input_img, meta = streamer.generate_face_image(degradation_type=deg_type, severity=severity)

        # Run Multi-Agent Graph
        start_t = time.time()
        final_state = orchestrator.run(input_img, metadata=meta, max_iterations=3)
        latency_ms = round((time.time() - start_t) * 1000, 1)

        audit = final_state["audit_report"]
        quality = final_state["quality_report"]

        print(f"➔ Execution Latency   : {latency_ms} ms")
        print(f"➔ Graph Retries       : {final_state['iteration_count'] - 1} self-healing loop(s)")
        print(f"➔ Fix Transformations : {final_state['enhancement_history']}")
        print(f"➔ Diagnosed Issues    : {quality.get('issues', [])}")
        print(f"➔ Final Quality Score : {audit['final_quality_score']}/100.0 ({audit['final_status']})")
        print(f"➔ Audit Verdict       : {audit['verdict']}")

        if audit['primary_bbox']:
            print(f"➔ Face Bounding Box   : {audit['primary_bbox']}")
            print(f"➔ IoU vs Ground Truth : {audit['iou_vs_ground_truth']}")

        print("\n")

        # Render Dashboard Image
        dashboard_img = draw_dashboard_hud(input_img, final_state["current_image"], final_state)
        
        cv2.imshow("Multi-Agent Face Detection & Diagnostic Platform", dashboard_img)
        print("Press ANY KEY in the image window to advance to the next scenario...\n")
        cv2.waitKey(0)

    cv2.destroyAllWindows()
    print("==========================================================")
    print("   Inspection & Audit Run Completed Successfully!")
    print("==========================================================")

if __name__ == "__main__":
    run_demo()
