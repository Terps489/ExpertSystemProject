from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from models import Diagnosis
from inference_engine import load_rules, run_expert_system
from routers.app_state import system_state, update_diagnoses


router = APIRouter()

templates = Jinja2Templates(directory="templates")

memory_rules = load_rules("knowledge_base/memory.json")

@router.get("/memory")
def memory_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="memory.html",
        context={
            **system_state["memory"],
            "results": system_state["diagnoses"]
        }
    )

@router.post("/memory/analyze")
def memory_analyze(request: Request,
    ram_usage: int = Form(0),
    swap_usage: int = Form(0),
    process_memory_usage: int = Form(0),
    process_count: int = Form(0),

    swap_active: str | None = Form(None),
    oom_log_found: str | None = Form(None),
    process_memory_growth: str | None = Form(None),
    performance_degraded: str | None = Form(None),
    free_memory_low: str | None = Form(None),
    cache_usage_high: str | None = Form(None),
    system_working: str | None = Form(None)):

    facts = {
        "ram_usage": ram_usage,
        "swap_usage": swap_usage,
        "process_memory_usage": process_memory_usage,
        "process_count": process_count,

        "swap_active": swap_active is not None,
        "oom_log_found": oom_log_found is not None,
        "process_memory_growth": process_memory_growth is not None,
        "performance_degraded": performance_degraded is not None,
        "free_memory_low": free_memory_low is not None,
        "cache_usage_high": cache_usage_high is not None,
        "system_working": system_working is not None
    }
    system_state["memory"] = facts
    
    results = run_expert_system(facts, memory_rules)
    update_diagnoses("Оперативная память",results)

    
    if not results:
        results = [ Diagnosis("Оперативная память", "0", "Проблем не обнаружено","Нет выявленных проблем",
                    ["Состояние оперативной памяти соответствует заданным параметрам",
                        "Всё хорошо или вы ввели недостаточно данных"])]


    return templates.TemplateResponse(
        request=request,
        name="memory.html",
        context={"results": system_state["diagnoses"] if system_state["diagnoses"] else results,

            "ram_usage": ram_usage,
            "swap_usage": swap_usage,
            "process_memory_usage": process_memory_usage,
            "process_count": process_count,

            "swap_active": swap_active,
            "oom_log_found": oom_log_found,
            "process_memory_growth": process_memory_growth,
            "performance_degraded": performance_degraded,
            "free_memory_low": free_memory_low,
            "cache_usage_high": cache_usage_high,
            "system_working": system_working
        }
    )