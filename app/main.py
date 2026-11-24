"""API SmartTasks integrada com o padrão Transactional Outbox."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .db import initialize_schema
from .models import Task, TaskCreate
from .outbox import create_task_with_outbox, initialize_outbox_schema
from .store import TaskStore

LOGGER = logging.getLogger("uvicorn.error")
store = TaskStore()


@asynccontextmanager
async def lifespan(application: FastAPI):
    initialize_schema()          # Tabela tasks existente: mantém os dados
    initialize_outbox_schema()   # Acrescenta a tabela permanente outbox_events
    yield


app = FastAPI(title="SmartTasks", version="1.1.0", lifespan=lifespan)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    return store.list_tasks()


@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(data: TaskCreate) -> Task:
    task = create_task_with_outbox(data)
    LOGGER.info("[outbox] Tarefa %s + evento PENDING gravados no PostgreSQL", task.id)
    return task


@app.patch("/api/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int) -> Task:
    task = store.set_status(task_id, "Concluída")
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return task


@app.patch("/api/tasks/{task_id}/reopen", response_model=Task)
def reopen_task(task_id: int) -> Task:
    task = store.set_status(task_id, "Aberta")
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return task