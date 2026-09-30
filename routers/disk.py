from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from models import Diagnosis
from inference_engine import load_rules, run_expert_system
from routers.app_state import system_state, update_diagnoses


router = APIRouter()

templates = Jinja2Templates(directory="templates")

disk_rules = load_rules("knowledge_base/disk.json")


@router.get("/disk")
def disk_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="disk.html",
        context={
            **system_state["disk"],
            "results": system_state["diagnoses"]
        }
    )


@router.post("/disk/analyze")
def disk_analyze(request: Request,
    filesystem_usage: int = Form(0),
    var_usage: int = Form(0),
    inode_usage: int = Form(0),
    io_wait: int = Form(0),
    disk_response_time: int = Form(0),

    free_space_available: str | None = Form(None),
    filesystem_read_only: str | None = Form(None),
    mount_point_missing: str | None = Form(None),
    mount_failed: str | None = Form(None),
    io_error_found: str | None = Form(None)):


    facts = {
    "filesystem_usage": filesystem_usage,
    "var_usage": var_usage,
    "inode_usage": inode_usage,
    "io_wait": io_wait,
    "disk_response_time": disk_response_time,

    "free_space_available": free_space_available is not None,
    "filesystem_read_only": filesystem_read_only is not None,
    "mount_point_missing": mount_point_missing is not None,
    "mount_failed": mount_failed is not None,
    "io_error_found": io_error_found is not None
    }


    system_state["disk"] = facts

    results = run_expert_system(facts, disk_rules)

    update_diagnoses("Дисковая подсистема", results)


    if not results:
        results = [
            Diagnosis(
                "Дисковая подсистема",
                "0",
                "Проблем не обнаружено",
                "Нет выявленных проблем",
                [
                    "Состояние дисковой подсистемы соответствует заданным параметрам",
                    "Всё хорошо или вы ввели недостаточно данных"
                ]
            )
        ]


    return templates.TemplateResponse(
        request=request,
        name="disk.html",
        context={
            "results": system_state["diagnoses"] if system_state["diagnoses"] else results,

            "filesystem_usage": filesystem_usage,
            "var_usage": var_usage,
            "inode_usage": inode_usage,
            "io_wait": io_wait,
            "disk_response_time": disk_response_time,

            "free_space_available": free_space_available,
            "filesystem_read_only": filesystem_read_only,
            "mount_point_missing": mount_point_missing,
            "mount_failed": mount_failed,
            "io_error_found": io_error_found
        }
    )