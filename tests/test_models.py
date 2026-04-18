import pytest
from pydantic import ValidationError

from app.models.schemas import Condition, Flow, FlowRequest, FlowResult, Task, TaskResult


class TestTask:
    def test_valid_task(self):
        task = Task(name="task1", description="Fetch data")
        assert task.name == "task1"
        assert task.description == "Fetch data"

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            Task(description="Fetch data")

    def test_missing_description_raises(self):
        with pytest.raises(ValidationError):
            Task(name="task1")


class TestCondition:
    def test_valid_condition(self):
        c = Condition(
            name="cond1",
            description="desc",
            source_task="task1",
            outcome="success",
            target_task_success="task2",
            target_task_failure="end",
        )
        assert c.source_task == "task1"
        assert c.target_task_failure == "end"

    def test_missing_field_raises(self):
        with pytest.raises(ValidationError):
            Condition(name="cond1", description="desc", source_task="task1")


class TestFlow:
    def test_valid_flow(self, sample_flow):
        assert sample_flow.id == "flow123"
        assert len(sample_flow.tasks) == 3
        assert len(sample_flow.conditions) == 2

    def test_empty_tasks_allowed(self):
        flow = Flow(id="f1", name="empty", start_task="task1", tasks=[], conditions=[])
        assert flow.tasks == []

    def test_flow_request_wraps_flow(self, sample_flow):
        req = FlowRequest(flow=sample_flow)
        assert req.flow.id == "flow123"


class TestTaskResult:
    def test_success_result(self):
        r = TaskResult(task_name="task1", status="success", data={"key": "val"})
        assert r.status == "success"
        assert r.error is None

    def test_failure_result(self):
        r = TaskResult(task_name="task1", status="failure", error="something went wrong")
        assert r.status == "failure"
        assert r.data is None


class TestFlowResult:
    def test_completed_result(self):
        r = FlowResult(
            flow_id="f1",
            flow_name="test",
            status="completed",
            executed_tasks=[],
            message="done",
        )
        assert r.status == "completed"
        assert r.stopped_at is None
