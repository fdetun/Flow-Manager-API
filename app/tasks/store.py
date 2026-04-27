from app.models.enums import TaskStatus
from app.models.schemas import TaskResult
from app.tasks.registry import register


@register(name="task3")
async def store_data(task_name: str, context: dict) -> TaskResult:
    processed = context.get("processed_data")
    if not processed:
        return TaskResult(
            task_name=task_name, status=TaskStatus.FAILURE, error="No processed data to store"
        )
    stored_ids = [r["id"] for r in processed]
    return TaskResult(
        task_name=task_name,
        status=TaskStatus.SUCCESS,
        data={"stored_ids": stored_ids, "count": len(stored_ids)},
    )
