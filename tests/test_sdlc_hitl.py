import pytest
from sdlc_engine.controller import HITLSDLCController

def test_hitl_initialization():
    controller = HITLSDLCController()
    state = controller.initialize_pipeline("Test Face Platform")
    assert state["current_stage"] == "1_PM_COORDINATOR"
    assert state["stage_status"] == "WAITING_FOR_HUMAN"
    assert "1_PM_COORDINATOR" in state["stages_data"]

def test_hitl_rejection_blocks_progression():
    controller = HITLSDLCController()
    state = controller.initialize_pipeline("Test Face Platform")
    
    # Reject PM stage
    state = controller.submit_human_decision(state, "REJECTED", feedback="Tolerances too loose")
    assert state["current_stage"] == "1_PM_COORDINATOR"
    assert state["stage_status"] == "REJECTED"
    # Stage 2 should not exist yet
    assert "2_SYSTEM_ARCHITECT" not in state["stages_data"]

def test_hitl_full_approval_cycle():
    controller = HITLSDLCController()
    state = controller.initialize_pipeline("Test Face Platform")
    
    # Approve Stage 1: PM
    state = controller.submit_human_decision(state, "APPROVED")
    assert state["current_stage"] == "2_SYSTEM_ARCHITECT"

    # Approve Stage 2: Architect
    state = controller.submit_human_decision(state, "APPROVED")
    assert state["current_stage"] == "3_TECH_LEAD"

    # Approve Stage 3: Tech Lead
    state = controller.submit_human_decision(state, "APPROVED")
    assert state["current_stage"] == "4_DEVELOPER_TASKS"
    assert state["current_task_idx"] == 1

    # Approve Tasks 1 through 5
    for task_id in range(1, 6):
        assert state["current_task_idx"] == task_id
        assert task_id in state["task_outputs"]
        assert task_id in state["task_qa_reports"]
        state = controller.submit_human_decision(state, "APPROVED")

    # Approve Stage 5: Reviewer
    assert state["current_stage"] == "5_CODE_REVIEWER"
    state = controller.submit_human_decision(state, "APPROVED")

    # Approve Stage 6: QA Regression
    assert state["current_stage"] == "6_QA_REGRESSION"
    state = controller.submit_human_decision(state, "APPROVED")

    # Approve Stage 7: Watchdog
    assert state["current_stage"] == "7_WATCHDOG_DEPLOY"
    state = controller.submit_human_decision(state, "APPROVED")

    # System Completed!
    assert state["current_stage"] == "COMPLETED"
    assert state["is_completed"] is True
    assert len(state["human_audit_trail"]) == 11 # 1+1+1+5+1+1+1
