from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from .errors import ConflictError, StateTransitionError, ValidationError
from .utils import digest, require_aware

class TaskState(str, Enum):
    READY = "READY"
    LEASED = "LEASED"
    COMPLETED = "COMPLETED"
    DEAD_LETTER = "DEAD_LETTER"

@dataclass(slots=True)
class OperationalTask:
    key: str
    payload_digest: str
    priority: int
    state: TaskState = TaskState.READY
    attempts: int = 0
    lease_owner: str | None = None
    lease_until: datetime | None = None
    result: object | None = None

class OperationalQueue:
    def __init__(self, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValidationError("max_attempts inválido")
        self.max_attempts = max_attempts
        self._tasks: dict[str, OperationalTask] = {}

    def submit(self, key: str, payload: object, priority: int = 100) -> OperationalTask:
        if not key.strip():
            raise ValidationError("chave obrigatória")
        fingerprint = digest(payload)
        current = self._tasks.get(key)
        if current:
            if current.payload_digest != fingerprint:
                raise ConflictError("tarefa duplicada com payload divergente")
            return current
        task = OperationalTask(key, fingerprint, priority)
        self._tasks[key] = task
        return task

    def claim(self, worker_id: str, now: datetime, lease_seconds: int = 60) -> OperationalTask | None:
        require_aware(now, "now")
        if not worker_id.strip() or lease_seconds <= 0:
            raise ValidationError("lease inválido")
        candidates=[]
        for task in self._tasks.values():
            expired = task.state == TaskState.LEASED and task.lease_until and task.lease_until <= now
            if task.state == TaskState.READY or expired:
                candidates.append(task)
        if not candidates:
            return None
        task=sorted(candidates, key=lambda item:(item.priority,item.key))[0]
        task.state=TaskState.LEASED
        task.lease_owner=worker_id
        task.lease_until=now+timedelta(seconds=lease_seconds)
        task.attempts += 1
        return task

    def complete(self, key: str, worker_id: str, result: object) -> OperationalTask:
        task=self._require(key)
        self._assert_lease(task, worker_id)
        task.state=TaskState.COMPLETED
        task.result=result
        task.lease_owner=None
        task.lease_until=None
        return task

    def fail(self, key: str, worker_id: str) -> OperationalTask:
        task=self._require(key)
        self._assert_lease(task, worker_id)
        task.lease_owner=None
        task.lease_until=None
        task.state=TaskState.DEAD_LETTER if task.attempts >= self.max_attempts else TaskState.READY
        return task

    def _assert_lease(self, task: OperationalTask, worker_id: str) -> None:
        if task.state != TaskState.LEASED or task.lease_owner != worker_id:
            raise StateTransitionError("lease inválido")

    def _require(self, key: str) -> OperationalTask:
        if key not in self._tasks:
            raise ValidationError("tarefa ausente")
        return self._tasks[key]
