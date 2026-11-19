# API HTTP SmartTasks com PostgreSQL e publicação de eventos.
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .db import initialize_schema
from .events import publish_task_created
from .models import Task, TaskCreate
from .store import TaskStore


@asynccontextmanager
async def lifespan(application: FastAPI):
    initialize_schema()
    yield


app = FastAPI(title="SmartTasks", version="1.0.0", lifespan=lifespan)
store = TaskStore()
LOGGER = logging.getLogger("uvicorn.error")


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
    task = store.create(data)
    LOGGER.info("[smarttasks] Tarefa %s guardada na PostgreSQL", task.id)
    published = publish_task_created(task)
    LOGGER.info(
        "[smarttasks] Publicação do evento da tarefa %s: %s",
        task.id,
        "OK" if published else "FALHOU",
    )
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