import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient

from app.models.schemas import Condition, Flow, Task
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_flow():
    return Flow(
        id="flow123",
        name="Data processing flow",
        start_task="task1",
        tasks=[
            Task(name="task1", description="Fetch data"),
            Task(name="task2", description="Process data"),
            Task(name="task3", description="Store data"),
        ],
        conditions=[
            Condition(
                name="condition_task1_result",
                description="Evaluate task1",
                source_task="task1",
                outcome="success",
                target_task_success="task2",
                target_task_failure="end",
            ),
            Condition(
                name="condition_task2_result",
                description="Evaluate task2",
                source_task="task2",
                outcome="success",
                target_task_success="task3",
                target_task_failure="end",
            ),
        ],
    )


@pytest.fixture
def sample_flow_payload():
    return {
        "flow": {
            "id": "flow123",
            "name": "Data processing flow",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "Fetch data"},
                {"name": "task2", "description": "Process data"},
                {"name": "task3", "description": "Store data"},
            ],
            "conditions": [
                {
                    "name": "condition_task1_result",
                    "description": "Evaluate task1",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "task2",
                    "target_task_failure": "end",
                },
                {
                    "name": "condition_task2_result",
                    "description": "Evaluate task2",
                    "source_task": "task2",
                    "outcome": "success",
                    "target_task_success": "task3",
                    "target_task_failure": "end",
                },
            ],
        }
    }
