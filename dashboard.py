import os
import sys
import time
import cv2
import numpy as np
from PIL import Image
import streamlit as st

# Configure wide layout
st.set_page_config(
    page_title="Human-In-The-Loop Multi-Agent SDLC: Face Detection",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Industrial Dark Styling
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    .main-header {
        background: linear-gradient(135deg, #111827 0%, #1e1b4b 100%);
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 16px;
    }
    .stage-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 8px;
    }
    .badge-status {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        font-family: monospace;
    }
    .badge-green { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
    .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }
    .badge-yellow { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid #eab308; }
    .badge-purple { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #a855f7; }
    .badge-red { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    .report-card {
        background: #111827;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #374151;
        font-family: monospace;
    }

    /* ALL BUTTONS BASE: Amber Text, Amber Border, Dark Background */
    button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-primary"],
    div[data-testid="stButton"] > button {
        background-color: #111827 !important;
        border: 2px solid #f59e0b !important;
        color: #fbbf24 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 8px 6px !important;
        white-space: nowrap !important;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.2) !important;
        transition: all 0.2s ease-in-out !important;
    }

    button[data-testid="baseButton-secondary"] p,
    button[data-testid="baseButton-primary"] p,
    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span,
    div[data-testid="stButton"] > button div {
        color: #fbbf24 !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        white-space: nowrap !important;
    }

    /* Approve Column (Col 1) Hover & Active: GREEN */
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] > button:hover,
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] > button:active {
        background-color: rgba(34, 197, 94, 0.2) !important;
        border-color: #22c55e !important;
        color: #4ade80 !important;
        box-shadow: 0 0 16px rgba(34, 197, 94, 0.5) !important;
    }
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] > button:hover p,
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] > button:active p {
        color: #4ade80 !important;
    }

    /* Reject Column (Col 2) Hover & Active: RED */
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] > button:hover,
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] > button:active {
        background-color: rgba(239, 68, 68, 0.2) !important;
        border-color: #ef4444 !important;
        color: #f87171 !important;
        box-shadow: 0 0 16px rgba(239, 68, 68, 0.5) !important;
    }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] > button:hover p,
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] > button:active p {
        color: #f87171 !important;
    }

    /* High contrast text inputs */
    div[data-testid="stTextInput"] input {
        background-color: #111827 !important;
        color: #f3f4f6 !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #f59e0b !important;
        box-shadow: 0 0 8px rgba(245, 158, 11, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

from sdlc_engine.controller import HITLSDLCController
from sdlc_engine.state import STAGES, TASKS

# Helper to convert cv2 image to PIL RGB
def cv_to_pil(img_bgr):
    if img_bgr is None:
        return None
    return Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

# Initialize controller and state in streamlit session
if "controller" not in st.session_state:
    st.session_state.controller = HITLSDLCController()
if "state" not in st.session_state:
    st.session_state.state = st.session_state.controller.initialize_pipeline("Face Detection Multi-Agent Vision Platform")

controller = st.session_state.controller
state = st.session_state.state

def reset_pipeline():
    """
    Completely purges all session approvals, notes, and states,
    ensuring a 100% clean reset to Stage 1.
    """
    for key in list(st.session_state.keys()):
        if key != "controller":
            del st.session_state[key]
    st.session_state.state = controller.initialize_pipeline("Face Detection Multi-Agent Vision Platform")

def render_human_approval_gate(controller, state, stage_or_task_name, prompt_text, key_prefix):
    """
    Renders standardized Human-in-the-Loop Approval Gate:
    - Default state: Both Approve & Reject buttons have crisp AMBER text and border.
    - Active stage is always ready for human approval (no stuck old approved banners).
    - If rejected: displays red status and styles reject button in red.
    - Buttons are properly sized to prevent text truncation (APP... / REJE...).
    """
    st.markdown("### 👤 Human Approval Gate")
    
    current_status = state.get("stage_status", "WAITING_FOR_HUMAN")
    is_rejected = (current_status == "REJECTED")
    
    if is_rejected:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.15); border: 1.5px solid #ef4444; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;">
            <div style="color: #f87171; font-weight: 700; font-size: 13px;">🔴 STATUS: REJECTED (CHANGES REQUESTED)</div>
            <div style="color: #fca5a5; font-size: 12px; margin-top: 4px;">Stage held in paused state. Update reviewer notes or click APPROVE when ready to proceed.</div>
        </div>
        """, unsafe_allow_html=True)
        # Injected dynamic CSS when in rejected state
        st.markdown("""
        <style>
        div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] > button {
            background-color: rgba(239, 68, 68, 0.25) !important;
            border-color: #ef4444 !important;
            color: #f87171 !important;
        }
        div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] > button p {
            color: #f87171 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Prompt Card with high-contrast Amber styling (No blue/dark contrast issues)
    st.markdown(f"""
    <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid #f59e0b; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 12px 14px; margin-bottom: 12px;">
        <div style="color: #fbbf24; font-weight: 700; font-size: 12px; margin-bottom: 4px; letter-spacing: 0.5px;">⚠️ HUMAN REVIEW REQUIRED</div>
        <div style="color: #fef3c7; font-size: 13px; line-height: 1.4;">{prompt_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    feedback = st.text_input("Reviewer Notes (Optional):", key=f"fb_{key_prefix}")
    
    c_app, c_rej = st.columns(2, gap="small")
    with c_app:
        if st.button("🟡 APPROVE", use_container_width=True, key=f"btn_app_{key_prefix}"):
            st.session_state.state = controller.submit_human_decision(state, "APPROVED", feedback=feedback or f"Approved {stage_or_task_name}")
            st.rerun()
    with c_rej:
        rej_label = "🔴 REJECTED" if is_rejected else "🟡 REJECT"
        if st.button(rej_label, use_container_width=True, key=f"btn_rej_{key_prefix}"):
            st.session_state.state = controller.submit_human_decision(state, "REJECTED", feedback=feedback or "Needs revision")
            st.rerun()

# Header
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 22px; color: #ffffff;">👤 Human-In-The-Loop Multi-Agent SDLC Platform</h1>
            <p style="margin: 4px 0 0 0; font-size: 13px; color: #9ca3af;">
                Interactive Stage-by-Stage Approvals: <b>7 SDLC Agents</b> + <b>5 Algorithmic Tasks</b> with Task QA Reports
            </p>
        </div>
        <div style="margin-top: 8px;">
            <span class="badge-status badge-purple">● HITL MODE ACTIVE</span>
            <span class="badge-status badge-blue">YUNET DEEP LEARNING</span>
            <span class="badge-status badge-green">TASK-LEVEL QA GATES</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 7 SDLC Stages Top Bar
st.markdown("<h4 style='font-size: 13px; color: #9ca3af; margin-bottom: 8px;'>🛡️ 7 SDLC GOVERNANCE STAGES & ACTIVE HUMAN GATE</h4>", unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

current_stg = state.get("current_stage")
cur_task = state.get("current_task_idx", 1)

stages_cols = [c1, c2, c3, c4, c5, c6, c7]
stage_labels = [
    ("1. PM Spec", "1_PM_COORDINATOR"),
    ("2. Architect", "2_SYSTEM_ARCHITECT"),
    ("3. Tech Lead", "3_TECH_LEAD"),
    (f"4. Dev (T{cur_task}/5)", "4_DEVELOPER_TASKS"),
    ("5. Reviewer", "5_CODE_REVIEWER"),
    ("6. QA Full", "6_QA_REGRESSION"),
    ("7. Watchdog", "7_WATCHDOG_DEPLOY")
]

for idx, (label, stg_key) in enumerate(stage_labels):
    with stages_cols[idx]:
        if state.get("is_completed"):
            badge_class = "badge-green"
            status_text = "APPROVED"
        elif current_stg == stg_key:
            badge_class = "badge-yellow"
            status_text = "WAITING YOU"
        elif idx < state.get("current_stage_idx", 0):
            badge_class = "badge-green"
            status_text = "APPROVED"
        else:
            badge_class = "badge-blue"
            status_text = "LOCKED"

        st.markdown(f"""
        <div class="stage-card">
            <div style="font-size: 11px; font-weight: bold;">{label}</div>
            <span class="badge-status {badge_class}">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='border: 0.5px solid #1f2937; margin: 10px 0 16px 0;'>", unsafe_allow_html=True)

# Main Stage Review Area
if state.get("is_completed"):
    st.balloons()
    st.success("🎉 **SYSTEM FULLY CERTIFIED & DEPLOYED TO PRODUCTION!** All 7 SDLC Stages and 5 Algorithmic Tasks approved by Human Lead.")
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("### 🏆 Master QA Regression Certificate")
        cert = state["stages_data"].get("6_QA_REGRESSION", {})
        st.markdown(f"""
        <div style="background: rgba(31, 41, 55, 0.7); border: 1px solid #374151; border-left: 4px solid #10b981; border-radius: 8px; padding: 12px 16px; margin-bottom: 12px;">
            <div style="color: #34d399; font-weight: 700; font-size: 14px;">PASSED ALL REGRESSION SUITES</div>
            <div style="color: #f3f4f6; font-size: 13px; margin-top: 4px;">
                Pass Rate: <b>{cert.get('pass_rate_pct')}%</b> ({cert.get('total_passed')}/{cert.get('total_test_cases')} Tests Passed) | Duration: {cert.get('execution_duration_sec')}s
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write(cert.get("qa_signoff"))

    with col_b:
        if st.button("🔄 Reset & Re-Run Pipeline from Stage 1", use_container_width=True):
            reset_pipeline()
            st.rerun()

else:
    view = controller.get_current_stage_view(state)
    stage_name = view["stage"]

    st.markdown(f"### 📍 Active Stage: {view['title']}")

    # Force refresh Stage 2 if old keys exist in memory
    if stage_name == "2_SYSTEM_ARCHITECT":
        if "tier_1_governance" in state["stages_data"].get("2_SYSTEM_ARCHITECT", {}) or "system_components" not in state["stages_data"].get("2_SYSTEM_ARCHITECT", {}):
            state["stages_data"]["2_SYSTEM_ARCHITECT"] = controller.architect_agent.run(state["stages_data"].get("1_PM_COORDINATOR", {}))
            view = controller.get_current_stage_view(state)

        content_col, action_col = st.columns([2.0, 1.2])
        with content_col:
            st.markdown("#### 🏗️ Stage 2: System Architect Agent")
            st.markdown("##### 📄 System Architecture Blueprint for Face Detection")
            
            # High-contrast card (NO unreadable dark-blue text)
            st.markdown("""
            <div style="background: rgba(31, 41, 55, 0.7); border: 1px solid #374151; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 14px 18px; margin: 12px 0 16px 0;">
                <div style="color: #fbbf24; font-weight: 700; font-size: 13px; margin-bottom: 4px; letter-spacing: 0.5px;">
                    🏛️ ARCHITECTURAL BLUEPRINT OVERVIEW
                </div>
                <div style="color: #f3f4f6; font-size: 14px; line-height: 1.5;">
                    The System Architect Agent designs the 4 core components that process photos from ingestion to face detection:
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🧩 The 4 System Components:")
            st.markdown("""
            * **1. 📸 Image Ingestion Module:**
              Opens digital photos (JPG, PNG, WebP) and verifies color buffers.
            * **2. 💡 Image Enhancement Module:**
              Pre-processes low-light or blurry photos using adaptive contrast (CLAHE).
            * **3. 🧠 AI Detection Core:**
              Executes OpenCV YuNet Deep Neural Network to locate faces and 5 facial points.
            * **4. 🎯 Quality & Output Module:**
              Draws green bounding boxes, measures clarity, and outputs confidence scores.
            """)
            
            st.markdown("### 🔄 Data Flow Pipeline:")
            st.code("Input Photo  -->  Image Enhancement  -->  YuNet AI Detector  -->  Annotated Face Output", language="text")
            
            st.markdown("### 🎯 Technical Specifications:")
            st.markdown("""
            * **AI Detection Model:** OpenCV YuNet Deep Neural Network (ONNX)
            * **Target Speed:** Under 150 milliseconds per photo
            * **Target Accuracy:** Greater than 95% precision
            * **Output:** Green bounding box coordinates [x, y, width, height], confidence score, and 5 facial points
            """)

        with action_col:
            render_human_approval_gate(
                controller,
                state,
                "System Architect Blueprint",
                "Do you approve the System Architect Agent's 4-component design and data flow for the Face Detection engine?",
                stage_name
            )

    # Stage 3: Dedicated Tech Lead 5-Task Roadmap Display
    elif stage_name == "3_TECH_LEAD":
        content_col, action_col = st.columns([2.0, 1.2])
        data = view.get("data", {})
        
        with content_col:
            st.markdown("#### 🛠️ Stage 3: Tech Lead Agent")
            st.markdown("##### 📋 5-Task Algorithmic Development Roadmap")
            
            st.markdown("""
            <div style="background: rgba(31, 41, 55, 0.7); border: 1px solid #374151; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 14px 18px; margin: 12px 0 16px 0;">
                <div style="color: #fbbf24; font-weight: 700; font-size: 13px; margin-bottom: 4px; letter-spacing: 0.5px;">
                    🎯 TECH LEAD DEVELOPMENT ROADMAP
                </div>
                <div style="color: #f3f4f6; font-size: 14px; line-height: 1.5;">
                    The Tech Lead breaks down the architecture blueprint into <b>5 concrete tasks for developers</b>. 
                    Each task defines the exact worker file being developed, its deliverables, and the rigorous test acceptance criteria.
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### ⚙️ Calibration Standards & Thresholds:")
            c_cal1, c_cal2, c_cal3, c_cal4 = st.columns(4)
            with c_cal1:
                st.markdown("""
                <div style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 12px 8px; text-align: center;">
                    <div style="color: #9ca3af; font-size: 11px; font-weight: bold;">SHARPNESS CUTOFF</div>
                    <div style="color: #fbbf24; font-size: 18px; font-weight: bold; margin: 4px 0;">50.0</div>
                    <div style="color: #6b7280; font-size: 10px;">Laplacian blur score</div>
                </div>
                """, unsafe_allow_html=True)
            with c_cal2:
                st.markdown("""
                <div style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 12px 8px; text-align: center;">
                    <div style="color: #9ca3af; font-size: 11px; font-weight: bold;">AI CONFIDENCE</div>
                    <div style="color: #34d399; font-size: 18px; font-weight: bold; margin: 4px 0;">55%</div>
                    <div style="color: #6b7280; font-size: 10px;">Min YuNet threshold</div>
                </div>
                """, unsafe_allow_html=True)
            with c_cal3:
                st.markdown("""
                <div style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 12px 8px; text-align: center;">
                    <div style="color: #9ca3af; font-size: 11px; font-weight: bold;">CONTRAST BOOST</div>
                    <div style="color: #60a5fa; font-size: 18px; font-weight: bold; margin: 4px 0;">3.5x</div>
                    <div style="color: #6b7280; font-size: 10px;">CLAHE clip limit</div>
                </div>
                """, unsafe_allow_html=True)
            with c_cal4:
                st.markdown("""
                <div style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 12px 8px; text-align: center;">
                    <div style="color: #9ca3af; font-size: 11px; font-weight: bold;">SPEED BUDGET</div>
                    <div style="color: #c084fc; font-size: 18px; font-weight: bold; margin: 4px 0;">150 ms</div>
                    <div style="color: #6b7280; font-size: 10px;">Max latency / photo</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>### 📝 The 5 Algorithmic Tasks for Developers:", unsafe_allow_html=True)
            
            task_icons = {1: "📸", 2: "💡", 3: "🧠", 4: "📐", 5: "🔄"}
            for t in data.get("tasks", []):
                t_id = t.get("task_id", 0)
                icon = task_icons.get(t_id, "📌")
                st.markdown(f"""
                <div style="background: #111827; border: 1px solid #374151; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap;">
                        <span style="color: #fbbf24; font-weight: bold; font-size: 15px;">{icon} {t.get('title')}</span>
                        <span style="background: #1f2937; color: #60a5fa; padding: 2px 8px; border-radius: 4px; font-family: monospace; font-size: 11px; border: 1px solid #374151;">📁 {t.get('target_worker')}</span>
                    </div>
                    <div style="margin-top: 6px; font-size: 13px; color: #f3f4f6; line-height: 1.4;">
                        <b style="color: #fbbf24;">📦 Deliverable:</b> {t.get('deliverables')}
                    </div>
                    <div style="margin-top: 6px; font-size: 13px; color: #a7f3d0; line-height: 1.4;">
                        <b style="color: #34d399;">✅ Acceptance Criteria:</b> {t.get('acceptance_criteria')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with action_col:
            render_human_approval_gate(
                controller,
                state,
                "5-Task Development Roadmap",
                view["prompt"],
                stage_name
            )

    # Display Stage Content for other stages (1_PM_COORDINATOR, 5_CODE_REVIEWER, 7_WATCHDOG_DEPLOY)
    elif stage_name in ["1_PM_COORDINATOR", "5_CODE_REVIEWER", "7_WATCHDOG_DEPLOY"]:
        content_col, action_col = st.columns([2.0, 1.2])
        
        with content_col:
            data = view.get("data", {})
            st.markdown(f"#### 📄 Deliverables Summary: {data.get('title', stage_name)}")
            
            for k, v in data.items():
                if k in ["title", "status"]: continue
                if isinstance(v, list):
                    st.markdown(f"**{k.replace('_', ' ').title()}:**")
                    for item in v:
                        if isinstance(item, dict):
                            st.markdown(f"- **{item.get('title', 'Item')}:** {item.get('deliverables', str(item))}")
                        else:
                            st.markdown(f"- {item}")
                elif isinstance(v, dict):
                    st.markdown(f"**{k.replace('_', ' ').title()}:**")
                    for sk, sv in v.items():
                        st.markdown(f"- **{sk}:** `{sv}`")
                else:
                    st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")

        with action_col:
            render_human_approval_gate(
                controller,
                state,
                view["title"],
                view["prompt"],
                stage_name
            )

    elif stage_name == "4_DEVELOPER_TASKS":
        task_id = view["task_id"]
        dev_out = view.get("developer_output", {})
        qa_rep = view.get("qa_report", {})
        task_def = view.get("task_def", {})

        st.markdown(f"**Active Task:** `{task_def.get('name')}`")
        
        dev_col, qa_col = st.columns([1, 1])

        with dev_col:
            st.markdown("#### 🛠️ Developer Output & Visual Evidence")
            st.success(f"**Deliverable:** {dev_out.get('title')}\n\n{dev_out.get('summary')}")
            
            # Show visual images based on task
            test_dir = os.path.join(os.path.dirname(__file__), "test_images")
            if task_id in [1, 2, 3, 5]:
                from algorithmic_agents.worker_1_streamer import FaceStreamerWorker
                streamer = FaceStreamerWorker()
                
                if task_id == 1:
                    p = os.path.join(test_dir, "Img3.jpg")
                    img = cv2.imread(p) if os.path.exists(p) else streamer.generate_synthetic_frame()[0]
                    st.image(cv_to_pil(img), caption="Ingested Frame Buffer (Verified 3 Channels)", use_container_width=True)
                
                elif task_id == 2:
                    from algorithmic_agents.worker_2_enhancer import ImageEnhancerWorker
                    enhancer = ImageEnhancerWorker()
                    dark_img, _ = streamer.generate_synthetic_frame("dark")
                    enh_img, act = enhancer.enhance_image(dark_img, "dark")
                    
                    sub1, sub2 = st.columns(2)
                    with sub1:
                        st.image(cv_to_pil(dark_img), caption="Input Dark Frame", use_container_width=True)
                    with sub2:
                        st.image(cv_to_pil(enh_img), caption=f"Enhanced ({act})", use_container_width=True)

                elif task_id == 3:
                    from algorithmic_agents.worker_3_detector import FaceDetectorWorker
                    detector = FaceDetectorWorker()
                    p = os.path.join(test_dir, "Img4.jpg")
                    img = cv2.imread(p) if os.path.exists(p) else streamer.generate_synthetic_frame()[0]
                    dets = detector.detect_faces(img)
                    vis = detector.draw_detections(img, dets)
                    st.image(cv_to_pil(vis), caption=f"Face Detections ({len(dets)} Found with Bounding Boxes & Landmarks)", use_container_width=True)

                elif task_id == 5:
                    from algorithmic_agents.worker_5_orchestrator import MultiAgentFacePipeline
                    pipeline = MultiAgentFacePipeline()
                    p = os.path.join(test_dir, "Img3.jpg")
                    res = pipeline.run_pipeline(p if os.path.exists(p) else None)
                    st.image(cv_to_pil(res["annotated_image"]), caption=f"End-to-End Pipeline Output (Latency: {res['latency_ms']}ms)", use_container_width=True)

        with qa_col:
            st.markdown("#### 📋 QA Engineer Task Test Report")
            rate = qa_rep.get("pass_rate_pct", 100.0)
            st.markdown(f"**QA Verdict:** `{qa_rep.get('verdict')}` | **Pass Rate:** `{rate}%` ({qa_rep.get('tests_passed')}/{qa_rep.get('tests_total')} Tests)")
            
            for tc in qa_rep.get("test_cases", []):
                badge = "badge-green" if tc["result"] == "PASSED" else "badge-red"
                st.markdown(f"""
                <div style="background: #1f2937; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; border: 1px solid #374151;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold; font-size: 12px;">[{tc['id']}] {tc['name']}</span>
                        <span class="badge-status {badge}">{tc['result']} ({tc['duration_ms']}ms)</span>
                    </div>
                    <div style="font-size: 11px; color: #9ca3af; margin-top: 4px;">{tc['notes']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr style='border: 0.5px solid #1f2937; margin: 12px 0;'>", unsafe_allow_html=True)
        
        # Human Action Gate for Task
        render_human_approval_gate(
            controller,
            state,
            f"Developer Task {task_id}: {task_def.get('name')}",
            view["prompt"],
            f"task_{task_id}"
        )

    elif stage_name == "6_QA_REGRESSION":
        cert = view.get("data", {})
        c_left, c_right = st.columns([3, 1])
        
        with c_left:
            st.markdown("#### 🏆 Master QA Regression Suite Results")
            st.success(f"**Status:** {cert.get('certification_status')} | **Duration:** {cert.get('execution_duration_sec')}s")
            
            for tb in cert.get("task_breakdown", []):
                st.markdown(f"- **Task {tb['task_id']} ({tb['task_name']}):** Score: `{tb['score']}` | Status: `{tb['verdict']}`")
            
            st.markdown(f"""
            <div style="background: rgba(31, 41, 55, 0.7); border: 1px solid #374151; border-left: 4px solid #10b981; border-radius: 8px; padding: 12px 16px; margin-top: 12px;">
                <span style="color: #34d399; font-weight: 700;">QA Lead Sign-Off:</span> <span style="color: #f3f4f6;">{cert.get('qa_signoff')}</span>
            </div>
            """, unsafe_allow_html=True)

        with c_right:
            render_human_approval_gate(
                controller,
                state,
                "Master QA Regression Certification",
                view["prompt"],
                "stage_6_qa"
            )

# Sidebar: Human Audit Trail & Execution Logs
with st.sidebar:
    st.markdown("### 📜 Human Audit Trail")
    trail = state.get("human_audit_trail", [])
    if not trail:
        st.markdown("<div style='color: #9ca3af; font-size: 13px; font-style: italic;'>No approval events recorded yet.</div>", unsafe_allow_html=True)
    else:
        for t in reversed(trail):
            color = "badge-green" if t["decision"] == "APPROVED" else "badge-red"
            st.markdown(f"""
            <div style="background: #111827; padding: 8px 10px; border-radius: 6px; margin-bottom: 6px; border: 1px solid #374151;">
                <div style="font-size: 11px; color: #9ca3af;">{t['timestamp']}</div>
                <div style="font-size: 12px; font-weight: bold; margin: 2px 0;">{t['stage_or_task']}</div>
                <span class="badge-status {color}">{t['decision']}</span>
                <div style="font-size: 10px; color: #d1d5db; margin-top: 4px;">Notes: {t['feedback']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🛠️ Controls")
    if st.button("🔄 Reset to Stage 1 (Fresh Start)", use_container_width=True):
        reset_pipeline()
        st.rerun()
