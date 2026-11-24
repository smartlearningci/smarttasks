"""Publicador de eventos e Retry with Exponential Backoff.

SENT significa aceite pela Azure Storage Queue; nao significa email enviado.
A entrega é pelo menos uma vez: o consumidor deve tratar duplicados.
"""
import json
import logging
import os
import time

from azure.storage.queue import QueueClient, TextBase64EncodePolicy

from .db import connect, initialize_schema
from .outbox import initialize_outbox_schema

QUEUE_NAME = "smarttasks-events"
LOGGER = logging.getLogger("outbox-worker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def backoff_seconds(attempt: int) -> int:
    """1.ª, 2.ª, 3.ª tentativa falhada: 5, 10, 20, depois 30 s."""
    return min(5 * (2 ** min(attempt - 1, 4)), 30)


def publish_one() -> bool:
    """Publica um evento pendente, se existir algum já devido.

    FOR UPDATE SKIP LOCKED evita concorrência entre publicadores.
    A transação mantém o lock durante o envio: simples para o laboratório,
    mas em produção deve ser substituído por claims/leases e timeouts.
    """
    with connect() as connection:
        row = connection.execute(
            """SELECT event_id, task_id, payload, attempts
               FROM outbox_events
               WHERE status = 'PENDING' AND next_attempt_at <= NOW()
               ORDER BY created_at
               FOR UPDATE SKIP LOCKED
               LIMIT 1"""
        ).fetchone()
        if row is None:
            return False

        event_id = row["event_id"]
        task_id = row["task_id"]
        attempt = row["attempts"] + 1
        try:
            if os.getenv("OUTBOX_SIMULATE_AZURE_FAILURE", "0") == "1":
                raise ConnectionError("Falha simulada: envio Azure indisponível")
            queue = QueueClient.from_connection_string(
                conn_str=os.environ["AZURE_STORAGE_CONNECTION_STRING"],
                queue_name=QUEUE_NAME,
                message_encode_policy=TextBase64EncodePolicy(),
            )
            # Compatível com o payload dos Notebooks 17–22.
            queue.send_message(json.dumps(row["payload"], ensure_ascii=False))
        except Exception as exc:
            wait = backoff_seconds(attempt)
            connection.execute(
                """UPDATE outbox_events
                   SET attempts = %s,
                       next_attempt_at = NOW() + (%s * INTERVAL '1 second'),
                       last_error = %s
                   WHERE event_id = %s""",
                (attempt, wait, str(exc)[:300], event_id),
            )
            LOGGER.warning(
                "[retry] Falha tarefa=%s | tentativa=%s | próxima em %ss | %s",
                task_id, attempt, wait, exc,
            )
        else:
            connection.execute(
                """UPDATE outbox_events
                   SET status = 'SENT', attempts = %s,
                       sent_at = NOW(), last_error = NULL
                   WHERE event_id = %s""",
                (attempt, event_id),
            )
            LOGGER.info(
                "[outbox] PUBLICADO na fila Azure | tarefa=%s | tentativa=%s",
                task_id, attempt,
            )
    return True


def main() -> None:
    # Garante a existência das tabelas mesmo no arranque inicial.
    initialize_schema()
    initialize_outbox_schema()
    LOGGER.info("[outbox] Worker iniciado; a escutar eventos pendentes")
    while True:
        try:
            if not publish_one():
                time.sleep(2)
        except Exception:
            LOGGER.exception("[outbox] Erro inesperado; nova tentativa em 5s")
            time.sleep(5)


if __name__ == "__main__":
    main()