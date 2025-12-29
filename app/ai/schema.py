from pydantic import BaseModel
from typing import List, Optional


class ModerationResult(BaseModel):
    moderationStatus: str
    reason: str
    explicitContent: Optional[bool]
    stemContent: Optional[bool]
    piiDetected: Optional[bool]
    copyrightRisk: Optional[bool]
    detectedObjects: List[str]
    detectedKeywords: List[str]
    totalTokens: int
