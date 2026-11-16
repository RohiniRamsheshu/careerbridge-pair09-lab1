from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.app import agent, main
from backend.app.auth import get_authenticated_user


class MemoryRepoFake:
    def __init__(self):
        self.docs = []
        self.calls = []

    def save_explicit_memory(self, student_id, memory_key, value, kind="fact"):
        self.calls.append((student_id, memory_key, value, kind))
        existing = next((item for item in self.docs if item["student_user_id"] == student_id and item["memory_key"] == memory_key and item["active"]), None)
        if existing:
            existing.update(value=value, kind=kind)
            return existing
        document = {"student_user_id": student_id, "memory_key": memory_key, "value": value, "kind": kind, "active": True}
        self.docs.append(document)
        return document

    def memory_summary(self, student_id):
        return [item for item in self.docs if item["student_user_id"] == student_id and item["active"]]

    def get_conversation(self, *_args):
        return None

    def save_conversation(self, *_args):
        return None


def with_student(user_id=12):
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": user_id, "role": "student"}


def test_authenticated_memory_endpoint_uses_authenticated_id_and_memory_command_retrieves(monkeypatch):
    repository = MemoryRepoFake()
    monkeypatch.setattr(main, "get_memory_repository", lambda: repository)
    with_student(12)
    client = TestClient(main.app)
    try:
        stored = client.post("/assistant/memory", json={
            "memory_key": "preferred_project_name",
            "value": "CareerBridge Demo",
            "kind": "preference",
            "student_user_id": 999,
        })
        retrieved = client.post("/assistant/chat", json={"message": "/memory"})
    finally:
        main.app.dependency_overrides.clear()

    assert stored.status_code == 201
    assert repository.calls == [(12, "preferred_project_name", "CareerBridge Demo", "preference")]
    assert retrieved.status_code == 200
    assert "CareerBridge Demo" in retrieved.json()["answer"]


def test_memory_endpoint_rejects_company_and_malformed_input(monkeypatch):
    repository = MemoryRepoFake()
    monkeypatch.setattr(main, "get_memory_repository", lambda: repository)
    client = TestClient(main.app)

    with_student(7)
    try:
        malformed = client.post("/assistant/memory", json={"memory_key": "Bad Key", "value": ""})
    finally:
        main.app.dependency_overrides.clear()
    assert malformed.status_code == 422

    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 8, "role": "company"}
    try:
        company = client.post("/assistant/memory", json={"memory_key": "company_note", "value": "private"})
    finally:
        main.app.dependency_overrides.clear()
    assert company.status_code == 403
    assert repository.calls == []


def test_explicit_chat_memory_intent_writes_and_ordinary_text_does_not(monkeypatch):
    repository = MemoryRepoFake()
    monkeypatch.setattr(agent, "FAST_RETRIEVAL_SUMMARY", True)
    user = {"id": 12, "role": "student"}

    answer = agent.run_assistant(
        "Remember this for future conversations: My preferred project name is CareerBridge Demo.",
        [], user, lambda *args, **kwargs: None, memory_repo=repository,
    )
    assert "CareerBridge Demo" in answer
    assert len(repository.calls) == 1

    class ScriptedModel:
        def complete(self, messages, tools=None):
            return {"content": "I can help with career searches."}

    agent.run_assistant(
        "My preferred project name is Another Name.",
        [], user, lambda *args, **kwargs: None, model=ScriptedModel(), memory_repo=repository,
    )
    assert len(repository.calls) == 1


def test_memory_isolation_in_chat_command(monkeypatch):
    repository = MemoryRepoFake()
    repository.save_explicit_memory(12, "preferred_project_name", "CareerBridge Demo", "preference")
    monkeypatch.setattr(main, "get_memory_repository", lambda: repository)
    with_student(13)
    client = TestClient(main.app)
    try:
        response = client.post("/assistant/chat", json={"message": "/memory"})
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "No stored memory" in response.json()["answer"]
