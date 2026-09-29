import os
import cv2
import json
import base64

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(SCRIPT_DIR, "output_multiframe", "user_uploads")
MANIFEST_FILE = os.path.join(UPLOAD_DIR, "manifest.json")

def sync_manifest():
    if not os.path.exists(UPLOAD_DIR):
        print("Upload dir does not exist.")
        return

    # Check existing manifest
    manifest_data = []
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, "r") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = []

    print(f"Current manifest contains {len(manifest_data)} entries.")

if __name__ == "__main__":
    sync_manifest()
