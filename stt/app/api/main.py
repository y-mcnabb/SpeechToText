from fastapi import APIRouter

from app.api.routes import audio, report, root, transcript

api_router = APIRouter()
api_router.include_router(root.router, prefix="", tags=["swagger_ui"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(transcript.router, prefix="/transcript", tags=["transcript"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
