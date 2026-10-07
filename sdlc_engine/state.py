import datetime
from typing import Dict, Any, List, Optional

STAGES = [
    "1_PM_COORDINATOR",
    "2_SYSTEM_ARCHITECT",
    "3_TECH_LEAD",
    "4_DEVELOPER_TASKS",
    "5_CODE_REVIEWER",
    "6_QA_REGRESSION",
    "7_WATCHDOG_DEPLOY"
]

TASKS = [
    {"id": 1, "name": "Task 1: Ingestion & Buffer Streamer (worker_1_streamer.py)", "worker": "FaceStreamerWorker"},
    {"id": 2, "name": "Task 2: Adaptive Lighting Enhancer (worker_2_enhancer.py)", "worker": "ImageEnhancerWorker"},
    {"id": 3, "name": "Task 3: Deep Learning Face Detector (worker_3_detector.py)", "worker": "FaceDetectorWorker"},
    {"id": 4, "name": "Task 4: Quality & 5-Point Pose Inspector (worker_4_inspector.py)", "worker": "QualityInspectorWorker"},
    {"id": 5, "name": "Task 5: End-to-End Multi-Agent Pipeline (worker_5_orchestrator.py)", "worker": "MultiAgentFacePipeline"}
]

def create_initial_hitl_state(project_name: str = "Multi-Agent Face Detection Platform") -> Dict[str, Any]:
    """Creates the initial Human-In-The-Loop state machine container."""
    return {
        "project_name": project_name,
        "current_stage": STAGES[0],
        "current_stage_idx": 0,
        "current_task_idx": 1,
        "stage_status": "WAITING_FOR_HUMAN", # Initial stage needs human start/approval
        "human_approval_status": "PENDING",
        "human_feedback": "",
        "stages_data": {},
        "task_outputs": {},
        "task_qa_reports": {},
        "human_audit_trail": [],
        "execution_log": [
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Initialized HITL SDLC Platform: {project_name}"
        ],
        "is_completed": False
    }

def record_approval(state: Dict[str, Any], stage_or_task: str, decision: str, approver: str = "Human Lead", feedback: str = "") -> None:
    """Records permanent audit trail entry for human approval gate."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": ts,
        "stage_or_task": stage_or_task,
        "decision": decision,
        "approver": approver,
        "feedback": feedback
    }
    state["human_audit_trail"].append(entry)
    state["execution_log"].append(f"[{ts}] 👤 HUMAN GATE: {decision} on {stage_or_task} by {approver}. Notes: {feedback or 'None'}")
