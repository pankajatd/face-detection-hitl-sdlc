import numpy as np
import pytest

from algorithmic_agents.worker_1_streamer import FaceStreamerWorker
from algorithmic_agents.worker_2_enhancer import ImageEnhancerWorker
from algorithmic_agents.worker_3_detector import FaceDetectorWorker
from algorithmic_agents.worker_4_inspector import QualityInspectorWorker
from algorithmic_agents.worker_5_orchestrator import MultiAgentFacePipeline

def test_worker_1_streamer():
    worker = FaceStreamerWorker()
    img, meta = worker.generate_synthetic_frame()
    assert img.shape == (512, 512, 3)
    assert meta["status"] == "VALID_INGESTION"

def test_worker_2_enhancer():
    streamer = FaceStreamerWorker()
    enhancer = ImageEnhancerWorker()
    dark_img, _ = streamer.generate_synthetic_frame("dark")
    enhanced, action = enhancer.enhance_image(dark_img, "dark")
    assert np.mean(enhanced) > np.mean(dark_img)
    assert "CLAHE" in action

def test_worker_3_detector():
    streamer = FaceStreamerWorker()
    detector = FaceDetectorWorker()
    synth, _ = streamer.generate_synthetic_frame()
    dets = detector.detect_faces(synth)
    assert isinstance(dets, list)

def test_worker_4_inspector():
    streamer = FaceStreamerWorker()
    inspector = QualityInspectorWorker()
    synth, _ = streamer.generate_synthetic_frame()
    dets = [{"bbox": [100, 100, 200, 200], "confidence": 0.95, "landmarks": []}]
    q = inspector.inspect(synth, dets)
    assert q["status"] in ["HIGH_QUALITY", "ACCEPTABLE"]
    assert q["sharpness_score"] > 0

def test_worker_5_orchestrator():
    pipeline = MultiAgentFacePipeline()
    res = pipeline.run_pipeline(None)
    assert res["status"] == "SUCCESS"
    assert "annotated_image" in res
    assert res["latency_ms"] < 250
