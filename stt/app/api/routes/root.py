import os

from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_swagger_ui_html

router = APIRouter()


@router.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Techniek Chat Assistant Workorders",
    )
