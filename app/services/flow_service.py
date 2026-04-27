"""
Sits between the API and the engine. Validates the flow definition first
(all task references exist, start_task is defined), then hands it off to run.
"""

from app.core.engine import run_flow
from app.models.enums import FLOW_END
from app.models.schemas import Flow, FlowResult

_VALID_TARGETS = {FLOW_END}


def validate_flow(flow: Flow) -> dict:
    task_names = {t.name for t in flow.tasks} | _VALID_TARGETS
    errors = []

    if flow.start_task not in task_names:
        errors.append(f"start_task '{flow.start_task}' is not defined in tasks.")

    for cond in flow.conditions:
        if cond.source_task not in task_names:
            errors.append(f"Condition '{cond.name}': source_task '{cond.source_task}' not defined.")
        if cond.target_task_success not in task_names:
            errors.append(
                f"Condition '{cond.name}': target_task_success "
                f"'{cond.target_task_success}' not defined."
            )
        if cond.target_task_failure not in task_names:
            errors.append(
                f"Condition '{cond.name}': target_task_failure "
                f"'{cond.target_task_failure}' not defined."
            )

    if errors:
        raise ValueError(errors)

    return {"valid": True, "flow_id": flow.id, "task_count": len(flow.tasks)}


async def execute_flow(flow: Flow) -> FlowResult:
    return await run_flow(flow)
