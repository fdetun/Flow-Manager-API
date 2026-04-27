from app.models.enums import TaskStatus
from app.models.schemas import TaskResult
from app.tasks.registry import register


@register(name="task2")
async def process_data(task_name: str, context: dict) -> TaskResult:
    raw = context.get("raw_data")
    if not raw:
        return TaskResult(
            task_name=task_name, status=TaskStatus.FAILURE, error="No raw data to process"
        )
    try:
        processed = [{"id": r["id"], "value": r.get("value", r.get("price", 0)) * 2} for r in raw]
    except Exception:
        processed = raw
    context["processed_data"] = processed
    return TaskResult(task_name=task_name, status=TaskStatus.SUCCESS, data=processed)
