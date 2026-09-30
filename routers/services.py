from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from models import Diagnosis
from inference_engine import load_rules, run_expert_system
from routers.app_state import system_state, update_diagnoses


router = APIRouter()

templates = Jinja2Templates(directory="templates")

services_rules = load_rules("knowledge_base/services.json")


@router.get("/services")
def services_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="services.html",
        context={
            **system_state["services"],
            "results": system_state["diagnoses"]
        }
    )


@router.post("/services/analyze")
def services_analyze(request: Request,
    restart_count: int = Form(0),

    service_inactive: str | None = Form(None),
    service_failed: str | None = Form(None),
    service_port_missing: str | None = Form(None),
    port_conflict: str | None = Form(None),
    service_local_only: str | None = Form(None),
    remote_port_unavailable: str | None = Form(None),
    dependency_failed: str | None = Form(None)):


    facts = {
    "restart_count": restart_count,

    "service_inactive": service_inactive is not None,
    "service_failed": service_failed is not None,
    "service_port_missing": service_port_missing is not None,
    "port_conflict": port_conflict is not None,
    "service_local_only": service_local_only is not None,
    "remote_port_unavailable": remote_port_unavailable is not None,
    "dependency_failed": dependency_failed is not None
    }


    system_state["services"] = facts

    results = run_expert_system(facts, services_rules)

    update_diagnoses("Сетевые порты и службы", results)


    if not results:
        results = [
            Diagnosis(
                "Сетевые порты и службы",
                "0",
                "Проблем не обнаружено",
                "Нет выявленных проблем",
                [
                    "Состояние сетевых портов и служб соответствует заданным параметрам",
                    "Всё хорошо или вы ввели недостаточно данных"
                ]
            )
        ]


    return templates.TemplateResponse(
        request=request,
        name="services.html",
        context={
            "results": system_state["diagnoses"] if system_state["diagnoses"] else results,

            "restart_count": restart_count,

            "service_inactive": service_inactive,
            "service_failed": service_failed,
            "service_port_missing": service_port_missing,
            "port_conflict": port_conflict,
            "service_local_only": service_local_only,
            "remote_port_unavailable": remote_port_unavailable,
            "dependency_failed": dependency_failed
        }
    )