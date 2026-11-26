"""API do SmartTasks: PostgreSQL, Transactional Outbox e anexos Blob."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .attachments import router as attachments_router, initialize_attachments_schema
from .db import initialize_schema
from .models import Task, TaskCreate
from .outbox import create_task_with_outbox, initialize_outbox_schema
from .store import TaskStore

LOGGER = logging.getLogger("uvicorn.error")
store = TaskStore()


@asynccontextmanager
async def lifespan(application: FastAPI):
    initialize_schema()               # Tarefas já existentes
    initialize_outbox_schema()        # Eventos pendentes do Notebook 23
    initialize_attachments_schema()   # NOVO: referências aos ficheiros Blob
    yield


app = FastAPI(title="SmartTasks", version="1.2.0", lifespan=lifespan)
app.include_router(attachments_router)  # NOVO: rotas de upload e download


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
    LOGGER.info("[outbox] Tarefa %s + evento PENDING guardados", task.id)
    return task


@app.patch("/api/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int) -> Task:
    task = store.set_status(task_id, "Concluída")
    if task is None:
        raise HTTPException(404, detail="Tarefa não encontrada.")
    return task


@app.patch("/api/tasks/{task_id}/reopen", response_model=Task)
def reopen_task(task_id: int) -> Task:
    task = store.set_status(task_id, "Aberta")
    if task is None:
        raise HTTPException(404, detail="Tarefa não encontrada.")
    return task