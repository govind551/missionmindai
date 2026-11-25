from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.voice import TranscriptionResponse, SynthesizeRequest, SynthesizeResponse
from app.services.speech_service import SpeechService

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty audio payload received")
    
    result = await SpeechService.transcribe_audio(content, file.filename or "audio.wav")
    return TranscriptionResponse(
        text=result.get("text", ""),
        confidence=result.get("confidence", 1.0)
    )

@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(req: SynthesizeRequest):
    result = await SpeechService.synthesize_speech(req.text, req.voice or "alloy")
    return SynthesizeResponse(
        audio_base64=result.get("audio_base64"),
        format=result.get("format", "mp3"),
        message=result.get("message")
    )
