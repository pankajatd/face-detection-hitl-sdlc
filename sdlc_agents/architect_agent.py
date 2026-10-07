import datetime
from typing import Dict, Any

class SystemArchitectAgent:
    """
    Stage 2 SDLC Agent: System Architect.
    Presents the software plan and introduces all 12 agents
    in plain, user-friendly language.
    """
    def run(self, pm_spec: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        arch = {
            "title": "Software Architecture Plan & Agent Organization",
            "responsible_agent": "System Architect Agent (The Blueprint Designer)",
            "generated_at": timestamp,
            "how_the_agents_are_organized": (
                "The System Architect Agent organizes our 12 AI agents into two specialized teams: "
                "Team A (7 Quality & Planning Agents) to monitor and test, and "
                "Team B (5 Face Detection Workers) to process the photos."
            ),
            "team_a_the_7_planning_and_quality_agents": [
                "1. PM Coordinator Agent: Defined the project requirements in Stage 1",
                "2. System Architect Agent: Presenting this blueprint & team structure in Stage 2",
                "3. Tech Lead Agent: Prepares the 5 coding tasks you will review next in Stage 3",
                "4. Developer Agent: Writes the code for each task one-by-one in Stage 4",
                "5. Reviewer Agent: Audits code safety, memory, and clean standards in Stage 5",
                "6. QA Engineer Agent: Tests each task and issues test reports in Stage 6",
                "7. Watchdog Agent: Monitors speed, memory, and system health in Stage 7"
            ],
            "team_b_the_5_face_detection_workers": [
                "Worker 1 (Face Streamer): Opens and reads the photo files into the computer",
                "Worker 2 (Image Enhancer): Automatically fixes dark shadows and blur",
                "Worker 3 (Face Detector): Spots human faces using YuNet AI and draws green boxes",
                "Worker 4 (Quality Inspector): Measures photo sharpness and checks head angles",
                "Worker 5 (Pipeline Orchestrator): Connects all 4 workers into one continuous pipeline"
            ],
            "the_3_step_photo_flow": [
                "Step 1: Open the photo (handled by Worker 1)",
                "Step 2: Enhance lighting & fix blur (handled by Worker 2)",
                "Step 3: Detect faces & draw green boxes (handled by Workers 3 & 4)"
            ],
            "what_goes_in_and_what_comes_out": {
                "input": "Any normal digital color photo (JPG, PNG, WebP).",
                "output": "The photo with green boxes around all faces, confidence score (e.g. 98%), and 5 facial points."
            },
            "status": "READY_FOR_HUMAN_APPROVAL"
        }
        return arch
