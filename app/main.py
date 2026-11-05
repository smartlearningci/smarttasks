"""Camada HTTP SmartTasks (RF-01 a RF-06).

Recebe pedidos e delega as operações na camada de armazenamento.
Separar responsabilidades facilita a compreensão e evolução (RNF-04).
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .models import Task, TaskCreate
from .store import TaskStore

app = FastAPI(title="SmartTasks", version="1.0.0")
# Os dados vivem apenas durante a execução deste processo.
store = TaskStore()


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """US-01/US-02; RNF-01/RNF-03: servir a interface HTML."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    """US-06; RF-06: indicar que o serviço responde."""
    return {"status": "ok"}


@app.get("/api/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    """US-01/US-05; RF-01/RF-05: devolver tarefas existentes."""
    return store.list_tasks()


@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(data: TaskCreate) -> Task:
    """US-02; RF-02/RF-05: criar tarefa com entrada validada."""
    return store.create(data)


@app.patch("/api/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int) -> Task:
    """US-03; RF-03/RF-05: concluir tarefa ou responder 404."""
    task = store.set_status(task_id, "Concluída")
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return task


@app.patch("/api/tasks/{task_id}/reopen", response_model=Task)
def reopen_task(task_id: int) -> Task:
    """US-04; RF-04/RF-05: reabrir tarefa ou responder 404."""
    task = store.set_status(task_id, "Aberta")
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return task
