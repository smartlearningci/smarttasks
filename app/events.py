# Publicação de eventos da criação de tarefas na Azure Storage Queue.
import json
import logging
import os

from azure.storage.queue import QueueClient, TextBase64EncodePolicy

from .models import Task


QUEUE_NAME = "smarttasks-events"
LOGGER = logging.getLogger("uvicorn.error")


def publish_task_created(task: Task) -> bool:
    # O logger do Uvicorn escreve diretamente no Log stream do container.
    LOGGER.info("[eventos] Recebida tarefa %s para publicação", task.id)
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        LOGGER.warning(
            "[eventos] NÃO PUBLICADO: variável AZURE_STORAGE_CONNECTION_STRING em falta"
        )
        return False

    message = json.dumps(
        {"event": "task.created", "id": task.id, "title": task.title[:200]},
        ensure_ascii=False,
    )

    try:
        LOGGER.info("[eventos] A enviar task.created | tarefa=%s | fila=%s", task.id, QUEUE_NAME)
        queue = QueueClient.from_connection_string(
            conn_str=connection_string,
            queue_name=QUEUE_NAME,
            message_encode_policy=TextBase64EncodePolicy(),
        )
        queue.send_message(message)
        LOGGER.info("[eventos] PUBLICADO na fila | tarefa=%s", task.id)
        return True
    except Exception:
        LOGGER.exception("[eventos] ERRO ao publicar na fila | tarefa=%s", task.id)
        return False