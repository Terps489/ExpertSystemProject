from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from models import Diagnosis
from inference_engine import load_rules, run_expert_system
from routers.app_state import system_state, update_diagnoses


router = APIRouter()

templates = Jinja2Templates(directory="templates")

cpu_rules = load_rules("knowledge_base/cpu.json")


@router.get("/cpu")
def cpu_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cpu.html",
        context={
            **system_state["cpu"],
            "results": system_state["diagnoses"]
        }
    )


@router.post("/cpu/analyze")
def cpu_analyze(request: Request,
    cpu_usage: int = Form(0),
    process_cpu_usage: int = Form(0),
    io_wait: int = Form(0),
    process_count: int = Form(0),

    load_high: str | None = Form(None),
    resource_wait: str | None = Form(None),
    performance_degraded: str | None = Form(None),
    service_cpu_source: str | None = Form(None),
    system_cpu_high: str | None = Form(None)):
    
    facts = {
    "cpu_usage": cpu_usage,
    "process_cpu_usage": process_cpu_usage,
    "io_wait": io_wait,
    "process_count": process_count,

    "load_high": load_high is not None,
    "resource_wait": resource_wait is not None,
    "performance_degraded": performance_degraded is not None,
    "service_cpu_source": service_cpu_source is not None,
    "system_cpu_high": system_cpu_high is not None
    }
    system_state["cpu"] = facts

    results = run_expert_system(facts, cpu_rules)
    update_diagnoses("Процессор и системная нагрузка",results)

    if not results:
        results = [ Diagnosis("Процессор и системная нагрузка", "0", "Проблем не обнаружено","Нет выявленных проблем",
                    ["Состояние процессора соответствует заданным параметрам",
                        "Всё хорошо или вы ввели недостаточно данных"])]
    return templates.TemplateResponse(
        request=request,
        name="cpu.html",
        context={"results": system_state["diagnoses"] if system_state["diagnoses"] else results,
            "cpu_usage": cpu_usage,
            "process_cpu_usage": process_cpu_usage,
            "io_wait": io_wait,
            "process_count": process_count,

            "load_high": load_high,
            "resource_wait": resource_wait,
            "performance_degraded": performance_degraded,
            "service_cpu_source": service_cpu_source,
            "system_cpu_high": system_cpu_high
        }
    )