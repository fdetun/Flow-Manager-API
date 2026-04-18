from typing import Any

from pydantic import BaseModel

from app.models.enums import ConditionOutcome, FlowStatus, TaskStatus


class Task(BaseModel):
    name: str
    description: str


class Condition(BaseModel):
    name: str
    description: str
    source_task: str
    outcome: ConditionOutcome
    target_task_success: str
    target_task_failure: str


class Flow(BaseModel):
    id: str
    name: str
    start_task: str
    tasks: list[Task]
    conditions: list[Condition]


class FlowRequest(BaseModel):
    flow: Flow


class TaskResult(BaseModel):
    task_name: str
    status: TaskStatus
    data: Any | None = None
    error: str | None = None


class FlowResult(BaseModel):
    flow_id: str
    flow_name: str
    status: FlowStatus
    executed_tasks: list[TaskResult]
    stopped_at: str | None = None
    message: str
