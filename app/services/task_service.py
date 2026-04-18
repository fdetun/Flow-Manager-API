import app.tasks  # noqa: F401 — ensures all task modules are imported and self-registered
from app.models.schemas import TaskResult
from app.tasks.registry import resolve


def execute_task(task_name: str, context: dict) -> TaskResult:
    handler = resolve(task_name)
    return handler(task_name, context)
