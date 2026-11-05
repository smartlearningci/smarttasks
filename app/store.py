"""Camada de armazenamento em memória (RNF-04, RNF-05).

Não depende de HTTP ou de base de dados. Reiniciar o processo perde os dados.
"""
from .models import Task, TaskCreate


class TaskStore:
    """Dicionário de tarefas, com identificadores sequenciais."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def list_tasks(self) -> list[Task]:
        """US-01/US-05; RF-01: listar tarefas pela ordem de criação."""
        return list(self._tasks.values())

    def create(self, data: TaskCreate) -> Task:
        """US-02; RF-02: criar tarefa inicialmente Aberta."""
        task = Task(
            id=self._next_id,
            title=data.title,
            description=data.description,
            status="Aberta",
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def set_status(self, task_id: int, status: str) -> Task | None:
        """US-03/US-04; RF-03/RF-04: alterar estado, ou None se não existir."""
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.status = status
        return task
