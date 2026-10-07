import sys
import os
import time
import argparse

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure local modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sdlc_engine.controller import HITLSDLCController
from sdlc_engine.state import TASKS

def print_banner(text: str, char: str = "="):
    print("\n" + char * 80)
    print(f" {text}")
    print(char * 80)

def main():
    parser = argparse.ArgumentParser(description="Interactive Human-In-The-Loop Multi-Agent SDLC Platform")
    parser.add_argument("--auto-approve", action="store_true", help="Automatically approves all gates (for automated testing)")
    args = parser.parse_args()

    controller = HITLSDLCController()
    state = controller.initialize_pipeline("Face Detection Multi-Agent Vision Platform")

    print_banner("INTERACTIVE HUMAN-IN-THE-LOOP SDLC PLATFORM: FACE DETECTION", "=")
    print("Welcome, Human Lead Approver! At each stage, the system will pause and present")
    print("the agent's output and test evidence for your explicit review and approval.\n")

    while not state.get("is_completed", False):
        view = controller.get_current_stage_view(state)
        stage_name = view["stage"]

        print_banner(f"📍 ACTIVE STAGE: {view['title']}")

        if stage_name in ["1_PM_COORDINATOR", "2_SYSTEM_ARCHITECT", "3_TECH_LEAD", "5_CODE_REVIEWER", "7_WATCHDOG_DEPLOY"]:
            data = view.get("data", {})
            for k, v in data.items():
                if isinstance(v, list):
                    print(f"\n🔹 {k.upper()}:")
                    for item in v:
                        print(f"   • {item}")
                elif isinstance(v, dict):
                    print(f"\n🔹 {k.upper()}:")
                    for sk, sv in v.items():
                        print(f"   • {sk}: {sv}")
                else:
                    print(f"• {k}: {v}")

        elif stage_name == "4_DEVELOPER_TASKS":
            dev = view.get("developer_output", {})
            qa = view.get("qa_report", {})
            task_id = view["task_id"]

            print(f"\n🛠️ DEVELOPER OUTPUT (Task {task_id}):")
            print(f"• Deliverable: {dev.get('title')}")
            print(f"• Functional Evidence: {dev.get('summary')}")
            if "metadata" in dev:
                print(f"• Details: {dev['metadata']}")
            if "detections_count" in dev:
                print(f"• Detections Found: {dev['detections_count']}")

            print("\n📋 QA ENGINEER TASK TEST REPORT:")
            print(qa.get("formatted_report", "No report available"))

        elif stage_name == "6_QA_REGRESSION":
            cert = view.get("data", {})
            print(f"\n🏆 MASTER QA CERTIFICATION:")
            print(f"• Total Test Cases: {cert.get('total_test_cases')} ({cert.get('total_passed')} Passed, {cert.get('total_failed')} Failed)")
            print(f"• Pass Rate: {cert.get('pass_rate_pct')}%")
            print(f"• Duration: {cert.get('execution_duration_sec')}s")
            print("\nTask-by-Task Breakdown:")
            for tb in cert.get("task_breakdown", []):
                print(f"   • Task {tb['task_id']}: {tb['task_name']:<45} Score: {tb['score']} [{tb['verdict']}]")

        print("-" * 80)
        print(f"❓ HUMAN APPROVAL GATE: {view.get('prompt')}")

        if args.auto_approve:
            choice = "a"
            print(">> [AUTO-APPROVE MODE] Decision: APPROVED")
            time.sleep(0.4)
        else:
            choice = input("\nEnter decision: [A] Approve & Proceed | [R] Reject with Notes | [Q] Quit: ").strip().lower()

        if choice == "a":
            state = controller.submit_human_decision(state, "APPROVED", feedback="Approved by Human Lead")
            print("\n✅ APPROVAL GRANTED! Unlocking next stage...")
            time.sleep(0.3)
        elif choice == "r":
            notes = input("Enter revision feedback for the Agent: ").strip()
            state = controller.submit_human_decision(state, "REJECTED", feedback=notes)
            print(f"\n⏸️ STAGE PAUSED. Feedback sent to agent: '{notes}'")
        elif choice == "q":
            print("\nExiting interactive session. State saved.")
            break
        else:
            print("Invalid input. Please choose A, R, or Q.")

    if state.get("is_completed", False):
        print_banner("MULTI-AGENT FACE PLATFORM FULLY CERTIFIED & DEPLOYED TO PRODUCTION!", "=")
        print("Audit Trail Summary:")
        for log in state.get("human_audit_trail", []):
            print(f"  • [{log['timestamp']}] {log['decision']} on {log['stage_or_task']} by {log['approver']}")

if __name__ == "__main__":
    main()
