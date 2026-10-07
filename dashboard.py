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
    .report-card {
        background: #111827;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #374151;
        font-family: monospace;
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
        st.info(f"**Pass Rate:** {cert.get('pass_rate_pct')}% ({cert.get('total_passed')}/{cert.get('total_test_cases')} Tests Passed) | **Duration:** {cert.get('execution_duration_sec')}s")
        st.write(cert.get("qa_signoff"))

    with col_b:
        if st.button("🔄 Reset & Re-Run Pipeline from Stage 1", type="primary", use_container_width=True):
            st.session_state.state = controller.initialize_pipeline("Face Detection Multi-Agent Vision Platform")
            st.rerun()

else:
    view = controller.get_current_stage_view(state)
    stage_name = view["stage"]

    st.markdown(f"### 📍 Active Stage: {view['title']}")

    # Ensure Stage 2 is refreshed with plain English text if running
    if stage_name == "2_SYSTEM_ARCHITECT" and "the_3_simple_steps" not in state["stages_data"].get("2_SYSTEM_ARCHITECT", {}):
        state["stages_data"]["2_SYSTEM_ARCHITECT"] = controller.architect_agent.run(state["stages_data"].get("1_PM_COORDINATOR", {}))
        view = controller.get_current_stage_view(state)

    # Display Stage Content
    if stage_name in ["1_PM_COORDINATOR", "2_SYSTEM_ARCHITECT", "3_TECH_LEAD", "5_CODE_REVIEWER", "7_WATCHDOG_DEPLOY"]:
        content_col, action_col = st.columns([3, 1])
        
        with content_col:
            data = view.get("data", {})
            st.markdown(f"#### 📄 Deliverables Summary: {data.get('title', stage_name)}")
            
            for k, v in data.items():
                if k in ["title", "status"]: continue
                if isinstance(v, list):
                    st.markdown(f"**{k.replace('_', ' ').title()}:**")
                    for item in v:
                        st.markdown(f"- {item}")
                elif isinstance(v, dict):
                    st.markdown(f"**{k.replace('_', ' ').title()}:**")
                    for sk, sv in v.items():
                        st.markdown(f"- **{sk}:** `{sv}`")
                else:
                    st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")

        with action_col:
            st.markdown("### 👤 Human Approval Gate")
            st.warning(f"**{view['prompt']}**")
            feedback = st.text_input("Reviewer Notes (Optional):", key=f"fb_{stage_name}")
            
            c_app, c_rej = st.columns(2)
            with c_app:
                if st.button("🟢 APPROVE", type="primary", use_container_width=True, key=f"btn_app_{stage_name}"):
                    st.session_state.state = controller.submit_human_decision(state, "APPROVED", feedback=feedback or "Approved by Human Lead")
                    st.rerun()
            with c_rej:
                if st.button("🔴 REJECT", use_container_width=True, key=f"btn_rej_{stage_name}"):
                    st.session_state.state = controller.submit_human_decision(state, "REJECTED", feedback=feedback or "Needs revision")
                    st.rerun()

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
        st.markdown("### 👤 Human Approval Gate for Task")
        g_c1, g_c2 = st.columns([3, 1])
        with g_c1:
            st.warning(f"**{view['prompt']}**")
            fb_task = st.text_input("Reviewer Notes for Task:", key=f"fb_task_{task_id}")
        with g_c2:
            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"🟢 APPROVE TASK {task_id}", type="primary", use_container_width=True, key=f"btn_app_task_{task_id}"):
                    st.session_state.state = controller.submit_human_decision(state, "APPROVED", feedback=fb_task or f"Approved Task {task_id}")
                    st.rerun()
            with b2:
                if st.button("🔴 REJECT", use_container_width=True, key=f"btn_rej_task_{task_id}"):
                    st.session_state.state = controller.submit_human_decision(state, "REJECTED", feedback=fb_task or "Needs fix")
                    st.rerun()

    elif stage_name == "6_QA_REGRESSION":
        cert = view.get("data", {})
        c_left, c_right = st.columns([3, 1])
        
        with c_left:
            st.markdown("#### 🏆 Master QA Regression Suite Results")
            st.success(f"**Status:** {cert.get('certification_status')} | **Duration:** {cert.get('execution_duration_sec')}s")
            
            for tb in cert.get("task_breakdown", []):
                st.markdown(f"- **Task {tb['task_id']} ({tb['task_name']}):** Score: `{tb['score']}` | Status: `{tb['verdict']}`")
            st.info(cert.get("qa_signoff"))

        with c_right:
            st.markdown("### 👤 Human Gate")
            st.warning(f"**{view['prompt']}**")
            fb_qa = st.text_input("Certification Notes:", key="fb_reg")
            if st.button("🟢 APPROVE QA CERTIFICATION", type="primary", use_container_width=True):
                st.session_state.state = controller.submit_human_decision(state, "APPROVED", feedback=fb_qa or "Approved QA Certification")
                st.rerun()

# Sidebar: Human Audit Trail & Execution Logs
with st.sidebar:
    st.markdown("### 📜 Human Audit Trail")
    trail = state.get("human_audit_trail", [])
    if not trail:
        st.info("No approval events recorded yet.")
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
        st.session_state.state = controller.initialize_pipeline("Face Detection Multi-Agent Vision Platform")
        st.rerun()
