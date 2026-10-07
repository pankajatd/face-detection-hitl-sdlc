import datetime
from typing import Dict, Any, List

class TechLeadAgent:
    """
    Stage 3 SDLC Agent: Tech Lead / Task Planner.
    Breaks the development lifecycle into 5 concrete Algorithmic Tasks,
    specifying acceptance criteria and test parameters for each task.
    """
    def run(self, arch_blueprint: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tasks = [
            {
                "task_id": 1,
                "title": "Task 1: Ingestion & Buffer Streamer",
                "target_worker": "algorithmic_agents/worker_1_streamer.py",
                "deliverables": "FaceStreamerWorker class with disk ingestion and synthetic generator.",
                "acceptance_criteria": "Loads 1080p frames, validates 3-channel buffers, traps missing files."
            },
            {
                "task_id": 2,
                "title": "Task 2: Adaptive Lighting & Blur Enhancer",
                "target_worker": "algorithmic_agents/worker_2_enhancer.py",
                "deliverables": "ImageEnhancerWorker class with Lab CLAHE and unsharp masking.",
                "acceptance_criteria": "Boosts dark frame luminance > 25%, restores blurred edge gradients."
            },
            {
                "task_id": 3,
                "title": "Task 3: Deep Learning Face Detector",
                "target_worker": "algorithmic_agents/worker_3_detector.py",
                "deliverables": "FaceDetectorWorker class with YuNet ONNX & Haar fallback.",
                "acceptance_criteria": "Detects frontal faces with > 90% confidence, returns 5 landmarks."
            },
            {
                "task_id": 4,
                "title": "Task 4: Quality & 5-Point Pose Inspector",
                "target_worker": "algorithmic_agents/worker_4_inspector.py",
                "deliverables": "QualityInspectorWorker class with Laplacian variance & pose estimator.",
                "acceptance_criteria": "Measures sharpness, flags blur (<50 var), classifies frontal vs profile."
            },
            {
                "task_id": 5,
                "title": "Task 5: End-to-End Multi-Agent Orchestrator",
                "target_worker": "algorithmic_agents/worker_5_orchestrator.py",
                "deliverables": "MultiAgentFacePipeline class with self-healing feedback loop.",
                "acceptance_criteria": "Executes full pipeline in < 150ms, auto-heals degraded frames."
            }
        ]

        roadmap = {
            "title": "5-Task Algorithmic Development Roadmap",
            "generated_at": timestamp,
            "optical_calibrations": {
                "blur_cutoff_laplacian": 50.0,
                "yunet_score_threshold": 0.55,
                "clahe_clip_limit": 3.5,
                "latency_budget_ms": 150.0
            },
            "tasks": tasks,
            "status": "READY_FOR_HUMAN_APPROVAL"
        }
        return roadmap

    def revise(self, current_roadmap: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Revises the 5-task roadmap and optical calibration parameters
        in response to human lead feedback and rejection notes.
        """
        roadmap = dict(current_roadmap)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        roadmap["revised_at"] = timestamp
        roadmap["revision_feedback"] = feedback

        fb_lower = feedback.lower() if feedback else ""
        blur_target = 30.0 if "blur" in fb_lower else 35.0
        clahe_target = 5.0 if ("bright" in fb_lower or "light" in fb_lower or "dark" in fb_lower) else 4.5
        conf_target = 0.60
        speed_target = 120.0

        # Recalibrate standards per human review
        roadmap["optical_calibrations"] = {
            "blur_cutoff_laplacian": blur_target,
            "yunet_score_threshold": conf_target,
            "clahe_clip_limit": clahe_target,
            "latency_budget_ms": speed_target
        }

        # Update acceptance criteria on tasks with reviewer requirements
        updated_tasks = []
        for t in roadmap.get("tasks", []):
            task_copy = dict(t)
            if task_copy.get("task_id") == 1:
                task_copy["acceptance_criteria"] = "Loads 1080p frames, enforces strict 3-channel BGR verification, traps corrupted headers."
            elif task_copy.get("task_id") == 2:
                task_copy["acceptance_criteria"] = f"Boosts dark shadow luminance with CLAHE {clahe_target}x + Gamma 2.4 and applies adaptive unsharp masking."
            elif task_copy.get("task_id") == 3:
                task_copy["acceptance_criteria"] = "YuNet DNN detection with 60% confidence floor and 5 facial landmark geometry validation."
            elif task_copy.get("task_id") == 4:
                task_copy["acceptance_criteria"] = f"Recalibrated Laplacian threshold (cutoff {blur_target}) with frontal/profile pose classification."
            elif task_copy.get("task_id") == 5:
                task_copy["acceptance_criteria"] = "Continuous multi-agent pipeline with auto-healing executed under 120ms latency budget."
            updated_tasks.append(task_copy)

        roadmap["tasks"] = updated_tasks
        roadmap["revisions_applied"] = [
            f"Recalibrated Sharpness Cutoff: 50.0 ➔ {blur_target} (loosened threshold so blurred/soft frames are deblurred instead of dropped).",
            f"Boosted Contrast/Brightness Limit: 3.5x ➔ {clahe_target}x (lifts dark shadows without washing out facial features).",
            f"Tightened Speed Budget SLA: 150ms ➔ {speed_target}ms (higher real-time throughput).",
            f"Elevated AI Confidence floor: 55% ➔ {int(conf_target*100)}% (minimizes false alarms).",
            "Updated Task 2 (Enhancer) and Task 4 (Inspector) acceptance criteria per reviewer instructions."
        ]
        roadmap["status"] = "REVISED_READY_FOR_APPROVAL"
        return roadmap

