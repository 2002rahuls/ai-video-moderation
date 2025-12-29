import os
import sys
import tempfile
import shutil

# Ensure the repository root is on sys.path so we can import the package when
# running this script from within app/video/ (useful for quick local testing).
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
	sys.path.insert(0, ROOT)

from app.video.extractor import extract_frames

video = r"C:\Users\Rahul\Downloads\5538137-hd_1920_1080_25fps.mp4"  # small local video
tmp = tempfile.mkdtemp()

# pass a frame_rate (fps) to match the extractor signature
frames = extract_frames(video, tmp, frame_rate=1.0)
print(f"Extracted {len(frames)} frames")

shutil.rmtree(tmp)
