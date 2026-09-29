import pytest
import numpy as np

from src.generator.face_streamer import SyntheticFaceStreamer
from src.detection.face_detector import FaceDetectorAgent
from src.quality.quality_inspector import QualityInspectorAgent
from src.enhancement.image_enhancer import ImageEnhancerAgent
from src.audit.test_auditor import TestAuditorAgent
from src.graph.workflow import MultiAgentFaceOrchestrator

@pytest.fixture
def streamer():
    return SyntheticFaceStreamer(img_size=(256, 256))

@pytest.fixture
def orchestrator():
    return MultiAgentFaceOrchestrator()

def test_face_streamer(streamer):
    img, meta = streamer.generate_face_image(degradation_type="none")
    assert img.shape == (256, 256, 3)
    assert meta["degradation"] == "none"
    assert "ground_truth_bbox" in meta

def test_detector_agent(streamer):
    detector = FaceDetectorAgent()
    img, meta = streamer.generate_face_image(degradation_type="none")
    detections = detector.detect_faces(img)
    assert len(detections) > 0
    assert "bbox" in detections[0]
    assert "confidence" in detections[0]

def test_quality_inspector_agent(streamer):
    inspector = QualityInspectorAgent()
    detector = FaceDetectorAgent()
    
    # Standard image
    img, _ = streamer.generate_face_image(degradation_type="none")
    detections = detector.detect_faces(img)
    report = inspector.inspect_quality(img, detections)
    assert "quality_score" in report
    assert "status" in report
    assert report["quality_score"] > 50.0

def test_enhancer_agent(streamer):
    enhancer = ImageEnhancerAgent()
    dark_img, _ = streamer.generate_face_image(degradation_type="under_exposed", severity=0.8)
    enhanced, action = enhancer.enhance_image(dark_img, {"issues": ["UNDER_EXPOSED"]})
    assert action == "CLAHE_BRIGHTNESS_BOOST"
    assert np.mean(enhanced) > np.mean(dark_img)

def test_multi_agent_workflow(orchestrator, streamer):
    dark_img, meta = streamer.generate_face_image(degradation_type="under_exposed", severity=0.8)
    final_state = orchestrator.run(dark_img, metadata=meta, max_iterations=3)
    
    audit = final_state["audit_report"]
    assert audit["verdict"] in ["PASSED_FIRST_TRY", "PASSED_AFTER_SELF_HEALING", "FAILED_QUALITY_GATE"]
    assert final_state["iteration_count"] > 1 or audit["verdict"] == "PASSED_FIRST_TRY"
    assert len(final_state["enhancement_history"]) > 0 or audit["verdict"] == "PASSED_FIRST_TRY"
