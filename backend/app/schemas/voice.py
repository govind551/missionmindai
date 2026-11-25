from typing import Optional
from pydantic import BaseModel

class TranscriptionResponse(BaseModel):
    text: str
    confidence: Optional[float] = 1.0
    language: Optional[str] = "en"

class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"
    speed: Optional[float] = 1.0

class SynthesizeResponse(BaseModel):
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    format: str = "mp3"
    message: Optional[str] = "Audio generated successfully"
