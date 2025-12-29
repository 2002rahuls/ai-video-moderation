import os
import shutil
import ffmpeg
from typing import List
from app.config import FRAME_INTERVAL, MAX_FRAMES


def extract_frames(video_path: str, output_dir: str, frame_rate: float) -> list[str]:
    """
    Extracts frames from a video file using ffmpeg-python.
    """
    #print(f"⏳ Starting frame extraction for {os.path.basename(video_path)}...")
    
    # Ensure ffmpeg binary is available on PATH before attempting extraction.
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg executable not found. Install ffmpeg and ensure the 'ffmpeg' binary is on your PATH. "
            "On Windows you can install via Chocolatey (`choco install ffmpeg`) or download a static build from https://ffmpeg.org/download.html."
        )

    output_pattern = os.path.join(output_dir, "frame-%04d.jpg")
    
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_pattern, r=frame_rate)
            .run(capture_stdout=True, capture_stderr=True, quiet=True)
        )
        #print(f"✅ Frame extraction finished for {os.path.basename(video_path)}.")
        files = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir)])
        return files
    except ffmpeg.Error as e:
        #print("❌ Error during frame extraction:")
        #print(e.stderr.decode())
        raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")


