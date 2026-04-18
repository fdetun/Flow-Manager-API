
from app.core.engine import run_flow
from app.models.schemas import Condition, Flow, Task


class TestRunFlowSuccess:
    def test_all_tasks_executed(self, sample_flow):
        result = run_flow(sample_flow)
        assert result.status == "completed"
        assert len(result.executed_tasks) == 3

    def test_task_order(self, sample_flow):
        result = run_flow(sample_flow)
        names = [t.task_name for t in result.executed_tasks]
        assert names == ["task1", "task2", "task3"]

    def test_all_tasks_succeed(self, sample_flow):
        result = run_flow(sample_flow)
        for task_result in result.executed_tasks:
            assert task_result.status == "success"

    def test_task3_stores_data(self, sample_flow):
        result = run_flow(sample_flow)
        last = result.executed_tasks[-1]
        assert last.task_name == "task3"
        assert "stored_ids" in last.data
        assert last.data["count"] == 5


class TestRunFlowFailure:
    def test_flow_aborts_when_task_fails(self):
        # Start at task2 with no context → process_data returns failure
        flow = Flow(
            id="f_fail",
            name="Failure flow",
            start_task="task2",
            tasks=[
                Task(name="task2", description="Process data"),
                Task(name="task3", description="Store data"),
            ],
            conditions=[
                Condition(
                    name="cond",
                    description="",
                    source_task="task2",
                    outcome="success",
                    target_task_success="task3",
                    target_task_failure="end",
                )
            ],
        )
        result = run_flow(flow)
        assert result.status == "aborted"
        assert result.stopped_at == "task2"
        assert len(result.executed_tasks) == 1
        assert result.executed_tasks[0].status == "failure"

    def test_only_failed_task_in_results(self):
        flow = Flow(
            id="f_fail2",
            name="Early fail",
            start_task="task2",
            tasks=[
                Task(name="task2", description="Process data"),
                Task(name="task3", description="Store data"),
            ],
            conditions=[
                Condition(
                    name="cond",
                    description="",
                    source_task="task2",
                    outcome="success",
                    target_task_success="task3",
                    target_task_failure="end",
                )
            ],
        )
        result = run_flow(flow)
        executed_names = [t.task_name for t in result.executed_tasks]
        assert "task3" not in executed_names


class TestRunFlowEdgeCases:
    def test_undefined_start_task_aborts(self, sample_flow):
        sample_flow.start_task = "nonexistent"
        result = run_flow(sample_flow)
        assert result.status == "aborted"
        assert "not found" in result.message

    def test_no_conditions_flow_runs_single_task(self):
        flow = Flow(
            id="f_single",
            name="Single task",
            start_task="task1",
            tasks=[Task(name="task1", description="Fetch data")],
            conditions=[],
        )
        result = run_flow(flow)
        assert result.status == "completed"
        assert len(result.executed_tasks) == 1

    def test_flow_result_contains_flow_metadata(self, sample_flow):
        result = run_flow(sample_flow)
        assert result.flow_id == sample_flow.id
        assert result.flow_name == sample_flow.name

    def test_two_task_flow_without_last_condition(self):
        flow = Flow(
            id="f_two",
            name="Two tasks",
            start_task="task1",
            tasks=[
                Task(name="task1", description="Fetch data"),
                Task(name="task2", description="Process data"),
            ],
            conditions=[
                Condition(
                    name="cond1",
                    description="",
                    source_task="task1",
                    outcome="success",
                    target_task_success="task2",
                    target_task_failure="end",
                )
            ],
        )
        result = run_flow(flow)
        assert result.status == "completed"
        assert len(result.executed_tasks) == 2
