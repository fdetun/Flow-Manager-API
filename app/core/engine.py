"""
The actual execution loop. No HTTP, no framework — just the flow logic.

Starts at start_task, runs each task, checks the condition, moves to the
next one or stops. Returns a full result regardless of how it ends.
"""

from app.models.enums import FLOW_END, FlowStatus, TaskStatus
from app.models.schemas import Flow, FlowResult, TaskResult
from app.services.task_service import execute_task


def _find_condition(flow: Flow, task_name: str):
    for condition in flow.conditions:
        if condition.source_task == task_name:
            return condition
    return None


def _find_task(flow: Flow, task_name: str):
    for task in flow.tasks:
        if task.name == task_name:
            return task
    return None


def run_flow(flow: Flow) -> FlowResult:
    context: dict = {}
    executed: list[TaskResult] = []
    current_task_name = flow.start_task

    while current_task_name and current_task_name != FLOW_END:
        task = _find_task(flow, current_task_name)
        if task is None:
            return FlowResult(
                flow_id=flow.id,
                flow_name=flow.name,
                status=FlowStatus.ABORTED,
                executed_tasks=executed,
                stopped_at=current_task_name,
                message=f"Task '{current_task_name}' not found in flow definition.",
            )

        try:
            result = execute_task(task.name, context)
        except ValueError as e:
            return FlowResult(
                flow_id=flow.id,
                flow_name=flow.name,
                status=FlowStatus.ABORTED,
                executed_tasks=executed,
                stopped_at=current_task_name,
                message=str(e),
            )
        executed.append(result)

        condition = _find_condition(flow, current_task_name)
        if condition is None:
            break  # terminal task — no further routing

        succeeded = result.status == TaskStatus.SUCCESS
        next_task = condition.target_task_success if succeeded else condition.target_task_failure

        if next_task == FLOW_END:
            return FlowResult(
                flow_id=flow.id,
                flow_name=flow.name,
                status=FlowStatus.COMPLETED if succeeded else FlowStatus.ABORTED,
                executed_tasks=executed,
                stopped_at=current_task_name,
                message=(
                    f"Flow ended after '{current_task_name}': "
                    f"task {result.status}, condition directed to '{FLOW_END}'."
                ),
            )

        current_task_name = next_task

    return FlowResult(
        flow_id=flow.id,
        flow_name=flow.name,
        status=FlowStatus.COMPLETED,
        executed_tasks=executed,
        message="Flow completed successfully.",
    )
