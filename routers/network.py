from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from models import Diagnosis
from inference_engine import load_rules, run_expert_system
from routers.app_state import system_state, update_diagnoses


router = APIRouter()

templates = Jinja2Templates(directory="templates")

network_rules = load_rules("knowledge_base/network.json")


@router.get("/network")
def network_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="network.html",
        context={
            **system_state["network"],
            "results": system_state["diagnoses"]
        }
    )


@router.post("/network/analyze")
def network_analyze(request: Request,
    packet_loss: int = Form(0),

    interface_down: str | None = Form(None),
    interface_no_ip: str | None = Form(None),
    default_route_missing: str | None = Form(None),
    gateway_unavailable: str | None = Form(None),
    external_ip_unavailable: str | None = Form(None),
    dns_failed: str | None = Form(None),
    dns_server_unavailable: str | None = Form(None),
    domain_resolution_failed: str | None = Form(None),
    large_packets_failed: str | None = Form(None),
    ip_conflict: str | None = Form(None)):


    facts = {
    "packet_loss": packet_loss,

    "interface_down": interface_down is not None,
    "interface_no_ip": interface_no_ip is not None,
    "default_route_missing": default_route_missing is not None,
    "gateway_unavailable": gateway_unavailable is not None,
    "external_ip_unavailable": external_ip_unavailable is not None,
    "dns_failed": dns_failed is not None,
    "dns_server_unavailable": dns_server_unavailable is not None,
    "domain_resolution_failed": domain_resolution_failed is not None,
    "large_packets_failed": large_packets_failed is not None,
    "ip_conflict": ip_conflict is not None
    }


    system_state["network"] = facts

    results = run_expert_system(facts, network_rules)

    update_diagnoses("Сетевое подключение", results)


    if not results:
        results = [
            Diagnosis(
                "Сетевое подключение",
                "0",
                "Проблем не обнаружено",
                "Нет выявленных проблем",
                [
                    "Состояние сетевого подключения соответствует заданным параметрам",
                    "Всё хорошо или вы ввели недостаточно данных"
                ]
            )
        ]


    return templates.TemplateResponse(
        request=request,
        name="network.html",
        context={
            "results": system_state["diagnoses"] if system_state["diagnoses"] else results,

            "packet_loss": packet_loss,

            "interface_down": interface_down,
            "interface_no_ip": interface_no_ip,
            "default_route_missing": default_route_missing,
            "gateway_unavailable": gateway_unavailable,
            "external_ip_unavailable": external_ip_unavailable,
            "dns_failed": dns_failed,
            "dns_server_unavailable": dns_server_unavailable,
            "domain_resolution_failed": domain_resolution_failed,
            "large_packets_failed": large_packets_failed,
            "ip_conflict": ip_conflict
        }
    )