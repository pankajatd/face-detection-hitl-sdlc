from typing import Dict, Any
from sdlc_engine.qa_evaluator import TaskQAEvaluator

class QATaskAgent:
    """
    Stage 4 SDLC Agent: QA Engineer (Task-Level Continuous Testing).
    Immediately tests each task completed by the Developer, executing normal and
    edge cases, and returning an official QA Test Report Card for Human Approval.
    """
    def __init__(self, test_images_dir: str = None):
        self.evaluator = TaskQAEvaluator(test_images_dir)

    def test_task(self, task_id: int) -> Dict[str, Any]:
        """Runs the test suite for Task ID and returns formatted report."""
        return self.evaluator.evaluate_task(task_id)
