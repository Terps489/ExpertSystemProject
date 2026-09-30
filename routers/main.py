from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from routers.app_state import system_state


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
def index(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "results": system_state["diagnoses"]
        }
    )