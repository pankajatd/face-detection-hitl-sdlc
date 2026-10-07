import datetime
from typing import Dict, Any

class PMCoordinatorAgent:
    """
    Stage 1 SDLC Agent: Product Manager Coordinator.
    Generates functional requirements, accuracy benchmarks, and compliance specs.
    """
    def run(self, project_name: str) -> Dict[str, Any]:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        spec = {
            "title": f"Requirements Specification Document: {project_name}",
            "generated_at": timestamp,
            "version": "1.0.0-PROD",
            "executive_summary": (
                "Deploy an edge-capable, high-speed Face Detection & Landmark Alignment platform "
                "with autonomous self-healing for lighting and defocus blur anomalies."
            ),
            "functional_requirements": [
                "FR-01: Support standard RGB/BGR frame ingestion up to 4K resolution.",
                "FR-02: Detect human faces with >95% precision using deep learning (YuNet ONNX).",
                "FR-03: Extract 5-point facial landmarks (both eyes, nose tip, mouth corners).",
                "FR-04: Diagnose optical quality (sharpness, underexposure, overexposure, pose).",
                "FR-05: Execute closed-loop self-healing on degraded frames in <25 milliseconds."
            ],
            "non_functional_requirements": [
                "NFR-01: End-to-end inference latency budget: < 150ms per frame.",
                "NFR-02: Zero unhandled runtime exceptions (circuit breaker protection).",
                "NFR-03: Zero vertical scroll control dashboard for operator ergonomics."
            ],
            "acceptance_criteria": [
                "100% automated test pass rate across all developer tasks.",
                "Human approval gate verified at every stage of the lifecycle."
            ],
            "status": "READY_FOR_HUMAN_APPROVAL"
        }
        return spec

    def revise(self, current_spec: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Revises the specifications document based on human reviewer notes.
        Dynamically detects which requirement the human requested (e.g., FR-02, FR-05),
        updates only that requirement with an elaborate definition, and preserves others.
        """
        spec = dict(current_spec)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        spec["revised_at"] = timestamp
        spec["revision_feedback"] = feedback

        fb_upper = feedback.upper() if feedback else ""

        # Default standard definitions
        original_specs = {
            "FR-01": "FR-01: Support standard RGB/BGR frame ingestion up to 4K resolution.",
            "FR-02": "FR-02: Detect human faces with >95% precision using deep learning (YuNet ONNX).",
            "FR-03": "FR-03: Extract 5-point facial landmarks (both eyes, nose tip, mouth corners).",
            "FR-04": "FR-04: Diagnose optical quality (sharpness, underexposure, overexposure, pose).",
            "FR-05": "FR-05: Execute closed-loop self-healing on degraded frames in <25 milliseconds."
        }

        elaborated_specs = {
            "FR-01": "FR-01 (Elaborated): High-Throughput Media Buffer Ingestion — Support digital image ingestion (JPEG, PNG, WebP) and live video streaming up to 4K resolution (3840x2160), validating 3-channel BGR memory buffers and trapping missing or corrupt file headers cleanly.",
            "FR-02": "FR-02 (Elaborated): Deep Learning Neural Inference Engine — Detect frontal, profile, and partially occluded human faces with >95% precision across variable lighting conditions utilizing OpenCV YuNet ONNX deep neural network inference, outputting validated 2D bounding box coordinates [x, y, width, height] and confidence scores.",
            "FR-03": "FR-03 (Elaborated): Multi-Point Geometric Landmark Localization — Accurately extract and triangulate 5 facial landmark anchor points (right eye center, left eye center, nose apex, right mouth corner, left mouth corner) to facilitate precise facial alignment and tilt correction.",
            "FR-04": "FR-04 (Elaborated): Optical Health & Head Pose Diagnostics — Calculate mathematical Laplacian sharpness score (scale 0-100), diagnose photographic defects (motion blur, underexposure, glare wash), and classify head rotation angles (yaw, pitch, roll) to ensure quality compliance.",
            "FR-05": "FR-05 (Elaborated): Autonomous Multi-Stage Self-Healing Engine — Autonomously route degraded frames through adaptive Lab CLAHE contrast enhancement and unsharp edge sharpening filters within <25ms, restoring facial visibility and landmark detectability without human intervention."
        }

        # Detect target requirement from reviewer feedback
        target_key = "FR-02"  # Default to FR-02 if ambiguous
        if "FR-01" in fb_upper or "FR-1" in fb_upper or "INGESTION" in fb_upper:
            target_key = "FR-01"
        elif "FR-02" in fb_upper or "FR-2" in fb_upper or "PRECISION" in fb_upper or "YUNET" in fb_upper or "FACE" in fb_upper:
            target_key = "FR-02"
        elif "FR-03" in fb_upper or "FR-3" in fb_upper or "LANDMARK" in fb_upper:
            target_key = "FR-03"
        elif "FR-04" in fb_upper or "FR-4" in fb_upper or "QUALITY" in fb_upper or "POSE" in fb_upper:
            target_key = "FR-04"
        elif "FR-05" in fb_upper or "FR-5" in fb_upper or "HEALING" in fb_upper:
            target_key = "FR-05"

        prev_req = original_specs[target_key]
        updated_req = elaborated_specs[target_key]

        spec["previous_requirement"] = prev_req
        spec["updated_requirement"] = updated_req
        spec["requirement_key"] = target_key
        spec["target_key"] = target_key

        # Rebuild functional requirements: Keep all original except the targeted one
        new_frs = []
        for k in ["FR-01", "FR-02", "FR-03", "FR-04", "FR-05"]:
            if k == target_key:
                new_frs.append(updated_req)
            else:
                new_frs.append(original_specs[k])

        spec["functional_requirements"] = new_frs
        spec["revisions_applied"] = [
            f"Elaborated {target_key} with comprehensive operational and accuracy definitions per reviewer notes: '{feedback}'."
        ]
        spec["status"] = "REVISED_READY_FOR_APPROVAL"
        return spec

