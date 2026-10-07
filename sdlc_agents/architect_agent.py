import datetime
from typing import Dict, Any

class SystemArchitectAgent:
    """
    Stage 2 SDLC Agent: System Architect.
    Presents the software plan in simple everyday words:
    how photos are handled, who builds what, and what outputs are produced.
    """
    def run(self, pm_spec: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        arch = {
            "title": "Software Plan: How This Face Tool Works (In 3 Simple Steps)",
            "generated_at": timestamp,
            "the_3_simple_steps": [
                "1. Step 1 (Open Photo): Reads any normal digital photo (JPG, PNG, WebP) into the computer.",
                "2. Step 2 (Fix Lighting & Blur): If the photo is too dark or blurry, automatically brightens and sharpens it.",
                "3. Step 3 (Find Faces): Detects human faces, draws a bright green box around each face, and marks the eyes, nose, and mouth."
            ],
            "the_7_quality_assistants": [
                "1. PM Coordinator: Defined the project goals and accuracy targets",
                "2. System Architect: Designed this simple 3-step software plan",
                "3. Tech Lead: Prepared the 5 coding tasks you will review next",
                "4. Developer: Writes the code for each task one-by-one",
                "5. Reviewer: Checks the code for safety, bugs, and clean standards",
                "6. QA Engineer: Tests each task and gives you a pass/fail report",
                "7. Watchdog: Monitors system health and speed in production"
            ],
            "the_5_tools_we_will_build": [
                "Tool 1: Photo Reader (loads and checks image files)",
                "Tool 2: Lighting & Blur Fixer (brightens dark shadows)",
                "Tool 3: Face Finder (spots faces and draws green boxes)",
                "Tool 4: Quality Checker (rates photo sharpness and pose)",
                "Tool 5: Complete Pipeline (connects all tools into one smooth system)"
            ],
            "what_goes_in_and_what_comes_out": {
                "what_you_put_in": "Any normal digital color photo.",
                "what_you_get_out": "The photo with green boxes around all faces, confidence percentage (e.g. 98%), and 5 facial points."
            },
            "status": "READY_FOR_HUMAN_APPROVAL"
        }
        return arch
