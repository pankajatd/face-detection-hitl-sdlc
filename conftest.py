import os
import sys

# Ensure root directory is in sys.path for test discovery across all pytest versions
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
