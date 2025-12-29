import os
import json
import base64
import asyncio
import shutil
import tempfile
from app.ai.client import client
from app.ai.prompt import SYSTEM_PROMPT
from app.ai.schema import ModerationResult
from app.video.extractor import extract_frames
from app.config import OPENAI_MODEL, TIMEOUT_SECONDS


async def moderate_video(video_path: str) -> dict:

    async def _run():
        temp_dir = tempfile.mkdtemp()
        try:
            frames = extract_frames(video_path, temp_dir)

            content = [{"type": "text", "text": "Analyze these video frames."}]
            for f in frames:
                with open(f, "rb") as img:
                    b64 = base64.b64encode(img.read()).decode()
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                })

            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                max_tokens=500
            )

            raw = response.choices[0].message.content
            data = json.loads(raw.strip().replace("```json", "").replace("```", ""))
            data["totalTokens"] = response.usage.total_tokens if response.usage else 0

            validated = ModerationResult.model_validate(data)
            return validated.model_dump()

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    try:
        return await asyncio.wait_for(_run(), timeout=TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        return {
            "moderationStatus": "failed",
            "reason": "Timeout",
            "explicitContent": None,
            "stemContent": None,
            "piiDetected": None,
            "copyrightRisk": None,
            "detectedObjects": [],
            "detectedKeywords": [],
            "totalTokens": 0
        }
