import json

from app import events
from app.models import Task


def sample_task():
    return Task(id=7, title="Preparar apresentação", description="", status="Aberta")


def test_event_disabled_without_azure_connection(monkeypatch):
    monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)
    assert events.publish_task_created(sample_task()) is False


def test_event_sent_to_queue(monkeypatch):
    captured = {}

    class FakeQueueClient:
        @classmethod
        def from_connection_string(cls, **kwargs):
            captured.update(kwargs)
            return cls()

        def send_message(self, content):
            captured["message"] = json.loads(content)

    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "ligacao-de-teste")
    monkeypatch.setattr(events, "QueueClient", FakeQueueClient)

    assert events.publish_task_created(sample_task()) is True
    assert captured["queue_name"] == "smarttasks-events"
    assert captured["message"] == {
        "event": "task.created",
        "id": 7,
        "title": "Preparar apresentação",
    }