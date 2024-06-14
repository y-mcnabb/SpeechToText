from fastapi import APIRouter

from app.api.routes import audio, report, transcript

api_router = APIRouter()
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
api_router.include_router(transcript.router, prefix="/transcript", tags=["transcript"])
