

class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestRunFlow:
    def test_successful_flow(self, client, sample_flow_payload):
        r = client.post("/flows/run", json=sample_flow_payload)
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "completed"
        assert body["flow_id"] == "flow123"
        assert len(body["executed_tasks"]) == 3

    def test_task_results_have_required_fields(self, client, sample_flow_payload):
        r = client.post("/flows/run", json=sample_flow_payload)
        for task in r.json()["executed_tasks"]:
            assert "task_name" in task
            assert "status" in task

    def test_data_flows_between_tasks(self, client, sample_flow_payload):
        r = client.post("/flows/run", json=sample_flow_payload)
        body = r.json()
        # task3 stores the ids processed by task2
        last_task = body["executed_tasks"][-1]
        assert last_task["data"]["count"] == 5

    def test_aborted_flow_on_failure(self, client):
        payload = {
            "flow": {
                "id": "fail_flow",
                "name": "Failing flow",
                "start_task": "task2",
                "tasks": [
                    {"name": "task2", "description": "Process data"},
                    {"name": "task3", "description": "Store data"},
                ],
                "conditions": [
                    {
                        "name": "cond",
                        "description": "",
                        "source_task": "task2",
                        "outcome": "success",
                        "target_task_success": "task3",
                        "target_task_failure": "end",
                    }
                ],
            }
        }
        r = client.post("/flows/run", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "aborted"
        assert body["stopped_at"] == "task2"

    def test_invalid_payload_returns_422(self, client):
        r = client.post("/flows/run", json={"flow": {}})
        assert r.status_code == 422

    def test_missing_body_returns_422(self, client):
        r = client.post("/flows/run")
        assert r.status_code == 422


class TestValidateFlow:
    def test_valid_flow_passes(self, client, sample_flow_payload):
        r = client.post("/flows/validate", json=sample_flow_payload)
        assert r.status_code == 200
        body = r.json()
        assert body["valid"] is True
        assert body["task_count"] == 3

    def test_invalid_start_task_rejected(self, client, sample_flow_payload):
        sample_flow_payload["flow"]["start_task"] = "nonexistent"
        r = client.post("/flows/validate", json=sample_flow_payload)
        assert r.status_code == 422
        errors = r.json()["detail"]
        assert any("start_task" in e for e in errors)

    def test_invalid_condition_target_rejected(self, client, sample_flow_payload):
        sample_flow_payload["flow"]["conditions"][0]["target_task_success"] = "ghost_task"
        r = client.post("/flows/validate", json=sample_flow_payload)
        assert r.status_code == 422

    def test_empty_conditions_passes(self, client):
        payload = {
            "flow": {
                "id": "f1",
                "name": "simple",
                "start_task": "task1",
                "tasks": [{"name": "task1", "description": "Fetch data"}],
                "conditions": [],
            }
        }
        r = client.post("/flows/validate", json=payload)
        assert r.status_code == 200
