import argparse
import asyncio
import json
import os
from app.pipeline import moderate_video

def main():
    parser = argparse.ArgumentParser(description="Run AI video moderation on a single video")
    parser.add_argument("--video", required=True, help="Path to local video file")
    parser.add_argument("--output", help="Optional output JSON file")
    args = parser.parse_args()

    video_path = args.video

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    result = asyncio.run(moderate_video(video_path))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
