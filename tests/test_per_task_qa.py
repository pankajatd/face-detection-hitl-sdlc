import pytest
from sdlc_engine.qa_evaluator import TaskQAEvaluator

def test_qa_evaluator_all_tasks():
    evaluator = TaskQAEvaluator()

    for task_id in range(1, 6):
        report = evaluator.evaluate_task(task_id)
        assert report["task_id"] == task_id
        assert report["tests_total"] > 0
        assert report["tests_passed"] == report["tests_total"]
        assert report["tests_failed"] == 0
        assert report["pass_rate_pct"] == 100.0
        assert report["verdict"] == "CERTIFIED"
        assert len(report["test_cases"]) == report["tests_total"]
        assert "QA TEST REPORT" in report["formatted_report"]
