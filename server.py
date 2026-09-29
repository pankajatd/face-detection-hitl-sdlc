"""
Lightweight Web Server for Multi-Agent Face Detection
Provides an interactive web dashboard with real-time Photo Upload & Detection.
Runs the complete 4-agent LangGraph workflow on any uploaded gallery picture.
"""
import os
import io
import time
import json
import base64
import numpy as np
import cv2
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

from src.graph.workflow import MultiAgentFaceOrchestrator

orchestrator = MultiAgentFaceOrchestrator()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_PATH = os.path.join(SCRIPT_DIR, "output_multiframe", "side_by_side_dashboard.html")
UPLOAD_DIR = os.path.join(SCRIPT_DIR, "output_multiframe", "user_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FaceDetectionServerHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for file:// access
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        url_path = urllib.parse.urlparse(self.path).path
        if url_path in ["/", "/index.html", "/dashboard"]:
            if os.path.exists(DASHBOARD_PATH):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(DASHBOARD_PATH, "rb") as f:
                    self.wfile.write(f.read())
                return
        elif url_path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "running", "orchestrator": "ready"}).encode("utf-8"))
            return
        elif url_path == "/api/slides":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            manifest_file = os.path.join(UPLOAD_DIR, "manifest.json")
            saved_slides = []
            if os.path.exists(manifest_file):
                try:
                    with open(manifest_file, "r") as mf:
                        saved_slides = json.load(mf)
                except Exception:
                    saved_slides = []
            self.wfile.write(json.dumps({"status": "success", "slides": saved_slides}).encode("utf-8"))
            return

        # Fallback to normal file serving from project root
        return super().do_GET()

    def do_POST(self):
        url_path = urllib.parse.urlparse(self.path).path
        if url_path == "/api/delete_uploads":
            try:
                deleted_count = 0
                if os.path.exists(UPLOAD_DIR):
                    for fname in os.listdir(UPLOAD_DIR):
                        fpath = os.path.join(UPLOAD_DIR, fname)
                        if os.path.isfile(fpath):
                            try:
                                os.remove(fpath)
                                deleted_count += 1
                            except Exception:
                                pass
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "message": f"Deleted {deleted_count} files. Uploads wiped clean!"
                }).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif url_path == "/api/upload_detect":
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                post_body = self.rfile.read(content_len)
                data = json.loads(post_body.decode("utf-8"))

                # Base64 image payload
                img_b64 = data.get("image", "")
                if "," in img_b64:
                    img_b64 = img_b64.split(",")[1]

                img_bytes = base64.b64decode(img_b64)
                np_arr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if img is None:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to decode image"}).encode("utf-8"))
                    return

                # Resize if excessively large to maintain snappy interactive speed (max 1600px)
                h, w = img.shape[:2]
                max_dim = 1600
                if max(h, w) > max_dim:
                    scale = max_dim / float(max(h, w))
                    img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

                # Save raw input image
                timestamp = int(time.time() * 1000)
                in_filename = f"upload_{timestamp}_input.png"
                cv2.imwrite(os.path.join(UPLOAD_DIR, in_filename), img)

                # Run Multi-Agent Graph
                t0 = time.time()
                final_state = orchestrator.run(img, metadata={"filename": data.get("name", "upload")}, max_iterations=3)
                latency_ms = round((time.time() - t0) * 1000, 1)

                detections = final_state.get("detections", [])
                audit = final_state.get("audit_report", {})
                quality = final_state.get("quality_report", {})
                output_img = final_state.get("current_image", img).copy()

                # Draw high-visibility Bounding Boxes & Confidence Labels on the output image
                for det in detections:
                    bx, by, bw, bh = det["bbox"]
                    conf = det.get("confidence", 0.0)
                    method = det.get("detection_method", "")
                    
                    # Box
                    cv2.rectangle(output_img, (bx, by), (bx + bw, by + bh), (0, 255, 0), 3)
                    
                    # Label Banner
                    lbl = f"FACE {conf*100:.0f}%"
                    (tw, th), _ = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(output_img, (bx, max(0, by - 26)), (bx + tw + 10, max(26, by)), (0, 180, 0), -1)
                    cv2.putText(output_img, lbl, (bx + 5, max(18, by - 7)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                out_filename = f"upload_{timestamp}_output.png"
                cv2.imwrite(os.path.join(UPLOAD_DIR, out_filename), output_img)

                # Re-encode to base64
                _, in_encoded = cv2.imencode(".png", img)
                in_b64_full = "data:image/png;base64," + base64.b64encode(in_encoded.tobytes()).decode("utf-8")

                _, out_encoded = cv2.imencode(".png", output_img)
                out_b64_full = "data:image/png;base64," + base64.b64encode(out_encoded.tobytes()).decode("utf-8")

                response_data = {
                    "status": "success",
                    "name": data.get("name", "Uploaded Photo"),
                    "input_img": in_b64_full,
                    "output_img": out_b64_full,
                    "faces_count": len(detections),
                    "detections": detections,
                    "quality_score": audit.get("final_quality_score", quality.get("quality_score", 0.0)),
                    "verdict": audit.get("verdict", "PASSED" if detections else "NO_FACE_DETECTED"),
                    "retries": final_state.get("iteration_count", 1) - 1,
                    "enhancements": final_state.get("enhancement_history", []),
                    "latency_ms": latency_ms,
                    "degradation": quality.get("issues", ["none"])[0] if quality.get("issues") else "none"
                }

                # Save to persistent manifest for Auto-Play recovery
                manifest_file = os.path.join(UPLOAD_DIR, "manifest.json")
                manifest_list = []
                if os.path.exists(manifest_file):
                    try:
                        with open(manifest_file, "r") as mf:
                            manifest_list = json.load(mf)
                    except Exception:
                        manifest_list = []
                manifest_list.append(response_data)
                try:
                    with open(manifest_file, "w") as mf:
                        json.dump(manifest_list, mf)
                except Exception:
                    pass

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8050):
    import webbrowser
    server_address = ("", port)
    httpd = HTTPServer(server_address, FaceDetectionServerHandler)
    url = f"http://localhost:{port}"
    print("=" * 65)
    print(f"  [SERVER] Face Detection Server Active at: {url}")
    print(f"  [URL] Opening Dashboard in browser: {url}/")
    print(f"  [API] Upload API: {url}/api/upload_detect")
    print("=" * 65)
    # Auto-open browser
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")
        httpd.server_close()

if __name__ == "__main__":
    run_server(8050)
