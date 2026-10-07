# 👤 Human-In-The-Loop Multi-Agent SDLC Platform: Face Detection (`face_detection_hitl_sdlc`)

> **An enterprise AI platform where Human Approval is an explicit code guard at every single lifecycle stage and development task, featuring 7 SDLC Governance Agents and 5 Algorithmic Face Detection Workers with per-task QA certification.**

[![Tests](https://img.shields.io/badge/Pytest-9%2F9%20Suites%20Passed%20(100%25)-22c55e?style=for-the-badge&logo=pytest&logoColor=white)](#-automated-testing--verification)
[![SDLC](https://img.shields.io/badge/Architecture-7%20SDLC%20%2B%205%20Workers-6366f1?style=for-the-badge)](#-two-tier-system-architecture)
[![HITL](https://img.shields.io/badge/Governance-Human--In--The--Loop%20Gates-f59e0b?style=for-the-badge)](#-how-human-approval-works-in-the-code)
[![Deep Learning](https://img.shields.io/badge/AI%20Model-OpenCV%20YuNet%20DNN-10b981?style=for-the-badge)](#-the-5-algorithmic-face-detection-workers)

---

## ⚡ Quick Start: How to Run in 30 Seconds

```powershell
# 1. Navigate to the project directory:
cd C:\Users\panka\.gemini\antigravity\scratch\face_detection_hitl_sdlc

# 2. Launch the Interactive Web Dashboard:
.\run_dashboard.bat
# (Opens in your browser at http://localhost:8509)

# 3. Or run the Interactive Terminal CLI:
.\run_cli.bat

# 4. Or execute the full automated test suite:
.\run_all.bat
```

---

## 💡 What Is This Project? (In Plain English)

Traditional software development faces two major risks:
1. **Black Box AI:** If AI agents run completely autonomously without human supervision, they can build the wrong features or pass subtle bugs into production.
2. **Delayed Quality Testing:** In traditional teams, testing only happens at the very end. Finding bugs late costs massive time and money.

### Our Solution:
This project enforces a **Human-In-The-Loop (HITL) Software Development Lifecycle (SDLC)**:
* 🔒 **The Code Literally Pauses at Every Stage:** The system halts at every single state and awaits explicit human authorization. The next agent or task **cannot execute** until you click **`[Approve]`**.
* 🛠️ **Developer + QA Micro-Loop:** When a Developer builds a task, the QA Engineer immediately runs tests on that specific task and generates an official **QA Test Report Card**. You inspect both the Developer's output and the QA Report before advancing to the next task.

---

## 🏛️ Two-Tier System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TIER 1: 7 SDLC GOVERNANCE AGENTS                                │
│                                                                                        │
│   [1. PM Agent] ──────► 👤 HUMAN GATE 1: Approve Requirements?                         │
│         │                                                                              │
│         ▼                                                                              │
│   [2. Architect] ─────► 👤 HUMAN GATE 2: Approve Architecture Blueprint?               │
│         │                                                                              │
│         ▼                                                                              │
│   [3. Tech Lead] ─────► 👤 HUMAN GATE 3: Approve 5-Task Roadmap?                       │
│         │                                                                              │
│         ▼                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────────────┐     │
│   │               4. DEVELOPER + QA TASK-BY-TASK APPROVAL CYCLE                  │     │
│   │                                                                              │     │
│   │   • Task 1: Streamer   ──► QA Test Report 1 (3/3 Pass) ──► 👤 HUMAN GATE 4.1 │     │
│   │   • Task 2: Enhancer   ──► QA Test Report 2 (3/3 Pass) ──► 👤 HUMAN GATE 4.2 │     │
│   │   • Task 3: Detector   ──► QA Test Report 3 (4/4 Pass) ──► 👤 HUMAN GATE 4.3 │     │
│   │   • Task 4: Inspector  ──► QA Test Report 4 (3/3 Pass) ──► 👤 HUMAN GATE 4.4 │     │
│   │   • Task 5: Pipeline   ──► QA Test Report 5 (3/3 Pass) ──► 👤 HUMAN GATE 4.5 │     │
│   └──────────────────────────────────────┬───────────────────────────────────────┘     │
│                                          │ (All tasks approved)                        │
│                                          ▼                                             │
│   [5. Reviewer] ──────► 👤 HUMAN GATE 5: Approve Security & Code Audit?                │
│         │                                                                              │
│         ▼                                                                              │
│   [6. QA Full Suite] ─► 👤 HUMAN GATE 6: Approve Master QA Certification (100% Pass)?  │
│         │                                                                              │
│         ▼                                                                              │
│   [7. Watchdog] ──────► 👤 FINAL HUMAN GATE: Launch Production System!                 │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔒 How Human Approval Works in the Code

Human Approval is not just a UI design; **it is an active code guard in Python**:

```python
def submit_human_decision(state, decision, feedback=""):
    if decision != "APPROVED":
        # System halts execution and records feedback
        state["stage_status"] = "REJECTED"
        return state
        
    # Strictly unlocks the next stage only upon 'APPROVED'
    record_approval(state, current_stage, "APPROVED")
    unlock_next_agent_or_task(state)
```

1. **State 1 (PM Coordinator):** Generates functional specs ➔ **Pauses for Human Approval**.
2. **State 2 (System Architect):** Designs folder structure & models ➔ **Pauses for Human Approval**.
3. **State 3 (Tech Lead):** Creates 5-task roadmap ➔ **Pauses for Human Approval**.
4. **State 4 (Developer Tasks 1..5):** 
   - Developer builds Task $N$ ➔
   - QA runs unit & edge case tests ➔
   - Displays Developer evidence & QA Test Report ➔
   - **Pauses for Human Approval** before Task $N+1$ can begin!
5. **State 5 (Code Reviewer):** Audits memory & exceptions ➔ **Pauses for Human Approval**.
6. **State 6 (QA Regression):** Runs master regression test suite ➔ **Pauses for Human Approval**.
7. **State 7 (Watchdog):** Production packaging & memory checks ➔ **Pauses for Final Deployment Sign-Off**.

---

## ⚙️ The 5 Algorithmic Face Detection Workers

Built and verified task-by-task during Stage 4:

1. **Worker 1: Face Streamer (`worker_1_streamer.py`):**
   * Ingests 1080p images or generates synthetic test frames with verified 3-channel buffers.
2. **Worker 2: Adaptive Enhancer (`worker_2_enhancer.py`):**
   * Uses Lab-space CLAHE, gamma correction, and unsharp masking to salvage dark or blurry face images.
3. **Worker 3: Deep Learning Detector (`worker_3_detector.py`):**
   * Uses OpenCV's **YuNet ONNX deep neural network** to detect faces, output bounding boxes, and compute 5 facial landmarks (eyes, nose, mouth) with Haar cascade fallback.
4. **Worker 4: Quality & Pose Inspector (`worker_4_inspector.py`):**
   * Measures sharpness (Laplacian variance), illumination, contrast, and facial angle (frontal vs. profile).
5. **Worker 5: Multi-Agent Pipeline (`worker_5_orchestrator.py`):**
   * Connects all workers in an autonomous closed loop with self-healing latency `< 150ms`.

---

## 🧪 Automated Testing & Verification

Run the verification suite:
```powershell
.\run_all.bat
```

```text
============================= test session starts =============================
collected 9 items

tests/test_algorithmic_workers.py::test_worker_1_streamer PASSED         [ 11%]
tests/test_algorithmic_workers.py::test_worker_2_enhancer PASSED         [ 22%]
tests/test_algorithmic_workers.py::test_worker_3_detector PASSED         [ 33%]
tests/test_algorithmic_workers.py::test_worker_4_inspector PASSED        [ 44%]
tests/test_algorithmic_workers.py::test_worker_5_orchestrator PASSED     [ 55%]
tests/test_per_task_qa.py::test_qa_evaluator_all_tasks PASSED            [ 66%]
tests/test_sdlc_hitl.py::test_hitl_initialization PASSED                 [ 77%]
tests/test_sdlc_hitl.py::test_hitl_rejection_blocks_progression PASSED   [ 88%]
tests/test_sdlc_hitl.py::test_hitl_full_approval_cycle PASSED            [100%]

============================== 9 passed in 2.67s ==============================
```

---

## 📂 Project Directory Structure

```
face_detection_hitl_sdlc/
├── dashboard.py                   # Full interactive Streamlit Web Approval Dashboard
├── run_interactive_sdlc.py        # Interactive CLI Approval Runner
├── run_dashboard.bat              # 1-Click launcher for web dashboard
├── run_cli.bat                    # 1-Click launcher for terminal CLI
├── run_all.bat                    # 1-Click test suite runner
│
├── sdlc_engine/                   # Core HITL State Machine & Quality Engines
│   ├── state.py                   # State schema, stage constants & audit trail
│   ├── controller.py              # Strict Human Approval gatekeeper & transition guard
│   └── qa_evaluator.py            # Automated per-task QA Test Report generator
│
├── sdlc_agents/                   # Tier 1: 7 SDLC Governance Agents
│   ├── pm_agent.py                # Stage 1: PM Coordinator (Requirements Spec)
│   ├── architect_agent.py         # Stage 2: System Architect (Architecture Blueprint)
│   ├── tech_lead_agent.py         # Stage 3: Tech Lead (Task Breakdown Roadmap)
│   ├── developer_agent.py         # Stage 4: Developer Agent (Executes Task 1..5)
│   ├── qa_agent.py                # Stage 4: QA Engineer (Task-Level Test Reports)
│   ├── reviewer_agent.py          # Stage 5: Code Reviewer & Safety Auditor
│   ├── qa_system_agent.py         # Stage 6: Master QA Regression Suite
│   └── watchdog_agent.py          # Stage 7: Production Watchdog & Final Sign-Off
│
├── algorithmic_agents/            # Tier 2: 5 Algorithmic Face Detection Workers
│   ├── worker_1_streamer.py       # Task 1: Ingestion & Buffer Streamer
│   ├── worker_2_enhancer.py       # Task 2: Adaptive Lighting & Blur Enhancer
│   ├── worker_3_detector.py       # Task 3: YuNet Deep Learning Face Detector
│   ├── worker_4_inspector.py      # Task 4: Quality & 5-Point Pose Inspector
│   └── worker_5_orchestrator.py   # Task 5: End-to-End Multi-Agent Pipeline
│
├── models/
│   └── face_detection_yunet.onnx  # YuNet Deep Neural Network ONNX weight
│
├── test_images/                   # Sample facial test images (Img1 to Img6)
└── tests/                         # Automated pytest test suites
```
