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
        Provides explicit diff between previous and updated FR-05 requirement.
        """
        spec = dict(current_spec)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        spec["revised_at"] = timestamp
        spec["revision_feedback"] = feedback

        prev_fr5 = "FR-05: Execute closed-loop self-healing on degraded frames in <25 milliseconds."
        updated_fr5 = (
            "FR-05 (Elaborated): Autonomous Multi-Stage Self-Healing Engine — "
            "When incoming camera frames exhibit optical degradation (such as heavy shadow underexposure, "
            "defocus blur, or contrast washout), the system must autonomously route the frame through "
            "adaptive Lab CLAHE contrast enhancement and unsharp edge sharpening filters within a strict <25ms "
            "micro-budget, restoring facial visibility and landmark detectability without human intervention."
        )

        spec["previous_requirement"] = prev_fr5
        spec["updated_requirement"] = updated_fr5
        spec["requirement_key"] = "FR-05"

        # Update functional requirements list
        new_frs = []
        for fr in spec.get("functional_requirements", []):
            if "FR-05" in fr:
                new_frs.append(updated_fr5)
            else:
                new_frs.append(fr)
        spec["functional_requirements"] = new_frs

        spec["revisions_applied"] = [
            f"Elaborated FR-05 with detailed algorithmic self-healing criteria, optical anomaly triggers, and performance budget per reviewer notes: '{feedback}'."
        ]
        spec["status"] = "REVISED_READY_FOR_APPROVAL"
        return spec

