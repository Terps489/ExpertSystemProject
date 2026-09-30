
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from models import Diagnosis
from inference_engine import load_rules, run_expert_system
from routers.app_state import system_state, update_diagnoses


router = APIRouter()

templates = Jinja2Templates(directory="templates")

web_rules = load_rules("knowledge_base/web.json")


@router.get("/web")
def web_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="web.html",
        context={
            **system_state["web"],
            "results": system_state["diagnoses"]
        }
    )


@router.post("/web/analyze")
def web_analyze(request: Request,
    http_status: int = Form(0),
    backend_response_time: int = Form(0),
    http_5xx_count: int = Form(0),
    http_404_count: int = Form(0),
    http_403_count: int = Form(0),
    response_size: int = Form(0),
    active_connections: int = Form(0),
    http_response_time: int = Form(0),

    backend_unavailable: str | None = Form(None),
    database_unavailable: str | None = Form(None),
    http_port_unavailable: str | None = Form(None)):


    facts = {
    "http_status": http_status,
    "backend_response_time": backend_response_time,
    "http_5xx_count": http_5xx_count,
    "http_404_count": http_404_count,
    "http_403_count": http_403_count,
    "response_size": response_size,
    "active_connections": active_connections,
    "http_response_time": http_response_time,

    "backend_unavailable": backend_unavailable is not None,
    "database_unavailable": database_unavailable is not None,
    "http_port_unavailable": http_port_unavailable is not None
    }


    system_state["web"] = facts

    results = run_expert_system(facts, web_rules)

    update_diagnoses("Веб-службы и приложения", results)


    if not results:
        results = [
            Diagnosis(
                "Веб-службы и приложения",
                "0",
                "Проблем не обнаружено",
                "Нет выявленных проблем",
                [
                    "Состояние веб-служб соответствует заданным параметрам",
                    "Всё хорошо или вы ввели недостаточно данных"
                ]
            )
        ]


    return templates.TemplateResponse(
        request=request,
        name="web.html",
        context={
            "results": system_state["diagnoses"] if system_state["diagnoses"] else results,

            "http_status": http_status,
            "backend_response_time": backend_response_time,
            "http_5xx_count": http_5xx_count,
            "http_404_count": http_404_count,
            "http_403_count": http_403_count,
            "response_size": response_size,
            "active_connections": active_connections,
            "http_response_time": http_response_time,

            "backend_unavailable": backend_unavailable,
            "database_unavailable": database_unavailable,
            "http_port_unavailable": http_port_unavailable
        }
    )