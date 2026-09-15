from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

DASHBOARD_HTML = Path(__file__).resolve().parent.parent / "static" / "dashboard.html"


@router.get("/")
@router.get("/dashboard")
def servir_dashboard() -> FileResponse:
    return FileResponse(DASHBOARD_HTML)
