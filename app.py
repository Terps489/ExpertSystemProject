from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import main, cpu, memory, disk, network, services, web, results


app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


app.include_router(main.router)
app.include_router(cpu.router)
app.include_router(memory.router)
app.include_router(disk.router)
app.include_router(network.router)
app.include_router(services.router)
app.include_router(web.router)
app.include_router(results.router)