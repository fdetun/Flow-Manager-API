import random
import httpx

from app.models.enums import TaskStatus
from app.models.schemas import TaskResult
from app.tasks.registry import register


# @register(name="task1")
# async def fetch_data(task_name: str, context: dict) -> TaskResult:
#     records = [{"id": i, "value": random.randint(1, 100)} for i in range(1, 6)]
#     context["raw_data"] = records
#     return TaskResult(task_name=task_name, status=TaskStatus.SUCCESS, data=records)


@register(name="task1")
async def fetch_data(task_name: str, context: dict) -> TaskResult:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://fakestoreapi.com/products/1")
        response.raise_for_status()
        records = response.json()

    records = records if isinstance(records, list) else [records]
    context["raw_data"] = records
    return TaskResult(task_name=task_name, status=TaskStatus.SUCCESS, data=records)
