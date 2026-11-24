"""Transactional Outbox do SmartTasks: tarefa + evento na mesma transação.

Este módulo não contacta o Azure. A tabela de eventos é permanente.
"""
import json
from uuid import uuid4

from .db import connect
from .models import Task, TaskCreate


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS outbox_events (
    event_id UUID PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'SENT')),
    attempts INTEGER NOT NULL DEFAULT 0,
    next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    last_error TEXT
)
"""


def initialize_outbox_schema() -> None:
    """Cria a tabela sem concorrência entre API e worker; preserva os dados."""
    with connect() as connection:
        # Só um dos serviços pode inicializar a tabela de cada vez.
        # O bloqueio é libertado automaticamente no COMMIT/ROLLBACK.
        connection.execute("SELECT pg_advisory_xact_lock(230023)")
        connection.execute(CREATE_TABLE_SQL)
        connection.execute(
            """CREATE INDEX IF NOT EXISTS idx_outbox_pending
               ON outbox_events (next_attempt_at, created_at)
               WHERE status = 'PENDING'"""
        )


def create_task_with_outbox(data: TaskCreate) -> Task:
    """Uma transação: COMMIT das duas gravações ou ROLLBACK de ambas."""
    with connect() as connection:
        row = connection.execute(
            """INSERT INTO tasks (title, description, status)
               VALUES (%s, %s, 'Aberta')
               RETURNING id, title, description, status""",
            (data.title, data.description),
        ).fetchone()
        task = Task(**row)
        payload = {"event": "task.created", "id": task.id,
                   "title": task.title[:200]}
        connection.execute(
            """INSERT INTO outbox_events
                 (event_id, task_id, event_type, payload)
               VALUES (%s, %s, %s, %s::jsonb)""",
            (uuid4(), task.id, "task.created",
             json.dumps(payload, ensure_ascii=False)),
        )
    return task