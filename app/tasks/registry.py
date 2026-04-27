from collections.abc import Callable

from app.models.schemas import TaskResult

type TaskHandler = Callable[[str, dict], TaskResult]

_REGISTRY: dict[str, TaskHandler] = {}


def register(name: str):
    def decorator(fn: TaskHandler) -> TaskHandler:
        _REGISTRY[name] = fn
        return fn

    return decorator


def resolve(task_name: str) -> TaskHandler:
    handler = _REGISTRY.get(task_name)
    if handler is None:
        raise ValueError(f"No handler registered for task '{task_name}'.")
    return handler
