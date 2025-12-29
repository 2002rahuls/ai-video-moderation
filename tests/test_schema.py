import sys
# print(sys.executable)
# print(sys.path)

from app.ai.schema import ModerationResult

dummy = {
    "moderationStatus": "approved",
    "reason": "Educational STEM content",
    "explicitContent": False,
    "stemContent": True,
    "piiDetected": False,
    "copyrightRisk": False,
    "detectedObjects": ["whiteboard"],
    "detectedKeywords": ["physics"],
    "totalTokens": 123
}

ModerationResult.model_validate(dummy)
print("Schema OK")
