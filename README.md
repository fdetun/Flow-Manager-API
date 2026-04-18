# Flow Manager

A small FastAPI service that runs a sequence of tasks, checking after each one
whether to keep going or stop. You define the tasks and the rules in a JSON
payload — the engine figures out the rest.

---

## The idea

The core concept is simple: you have tasks, and between them you have conditions.
A condition looks at whether the previous task succeeded or failed, then points
to either the next task or `"end"`. The engine follows that chain until there's
nowhere left to go.

```
task1 ──► did it succeed? ──► yes ──► task2
                          └──► no  ──► stop

task2 ──► did it succeed? ──► yes ──► task3
                          └──► no  ──► stop

task3 ──► (nothing after this) ──► done
```

Tasks don't know about each other at all. The wiring lives in the conditions,
which means you can define any flow you want in the request body without
touching the code.

---

## How it works

### Tasks

Each task is just a function that receives a `context` dictionary and returns
a `TaskResult` with a status of `success` or `failure`. The context is shared
across the whole run, so `task2` can read what `task1` wrote.

The built-in tasks simulate a data pipeline:

- **task1 / "fetch"** — generates some random records and puts them in context
- **task2 / "process"** — doubles the values from task1
- **task3 / "store"** — reads the processed records and returns the stored IDs

When you send a task name or description that isn't one of those three, the
engine tries to match it by keyword (`"fetch"`, `"process"`, `"store"`,
`"retrieve"`, `"transform"`, `"save"`, `"persist"`). If nothing matches at all,
it falls back to a generic handler that just returns success.

### Conditions

A condition says: *"after task X finishes, go to task Y if it succeeded, or
task Z if it failed."* If a task has no condition attached to it, the engine
treats it as the last step and wraps up the flow.

### Flow result

Every run returns a full picture of what happened:

- `status` — `completed` or `aborted`
- `executed_tasks` — everything that actually ran, in order, with their output
- `stopped_at` — set if the flow was cut short by a failure
- `message` — a plain-English summary

---

## Project layout

```
app/
├── api/routes.py           # HTTP endpoints — catches exceptions, maps to status codes
├── core/engine.py          # the loop that actually runs the flow
├── models/
│   ├── enums.py            # TaskStatus, FlowStatus, ConditionOutcome
│   └── schemas.py          # Pydantic models for the whole domain
├── services/
│   ├── flow_service.py     # validates inputs, then hands off to the engine
│   └── task_service.py     # entry point for task execution, delegates to the registry
└── tasks/
    ├── registry.py         # @register decorator + name/keyword lookup
    ├── fetch.py            # task1 — generates records, writes to context
    ├── process.py          # task2 — transforms records from context
    └── store.py            # task3 — persists processed records
```

### Adding a new task

Create a new file in `app/tasks/`, decorate the function with `@register`, then
add it to `app/tasks/__init__.py`. Nothing else needs to change.

```python
# app/tasks/notify.py
from app.tasks.registry import register

@register(name="task4")
def notify(task_name: str, context: dict):
    ...
```

If a flow references a task name with no registered handler, the engine aborts
immediately with a clear message — it won't silently succeed.

### Error handling

The service layer raises plain Python exceptions (`ValueError`). The routes catch
them and decide the HTTP status code — so the business logic stays framework-agnostic.

- Structural errors (bad task references) → `422`
- Unexpected crashes → `500`
- Flow aborts (task failed at runtime) → `200` with `status: aborted` in the body

---

## API

### `POST /flows/run`

Send a flow definition, get back a full execution report.

**Request**

```json
{
  "flow": {
    "id": "flow123",
    "name": "Data processing flow",
    "start_task": "task1",
    "tasks": [
      { "name": "task1", "description": "Fetch data" },
      { "name": "task2", "description": "Process data" },
      { "name": "task3", "description": "Store data" }
    ],
    "conditions": [
      {
        "name": "condition_task1_result",
        "description": "If task1 succeeded go to task2, otherwise stop",
        "source_task": "task1",
        "outcome": "success",
        "target_task_success": "task2",
        "target_task_failure": "end"
      },
      {
        "name": "condition_task2_result",
        "description": "If task2 succeeded go to task3, otherwise stop",
        "source_task": "task2",
        "outcome": "success",
        "target_task_success": "task3",
        "target_task_failure": "end"
      }
    ]
  }
}
```

**Everything went fine**

```json
{
  "flow_id": "flow123",
  "flow_name": "Data processing flow",
  "status": "completed",
  "executed_tasks": [
    { "task_name": "task1", "status": "success", "data": [...] },
    { "task_name": "task2", "status": "success", "data": [...] },
    { "task_name": "task3", "status": "success", "data": { "stored_ids": [1,2,3,4,5], "count": 5 } }
  ],
  "stopped_at": null,
  "message": "Flow completed successfully."
}
```

**Something failed along the way**

```json
{
  "flow_id": "flow123",
  "flow_name": "Data processing flow",
  "status": "aborted",
  "executed_tasks": [
    { "task_name": "task2", "status": "failure", "error": "No raw data to process" }
  ],
  "stopped_at": "task2",
  "message": "Flow ended after 'task2': task failure, condition directed to 'end'."
}
```

---

### `POST /flows/validate`

Check that a flow definition is internally consistent before running it — all
task references exist, start_task is defined, etc. Nothing is executed.

```json
{ "valid": true, "flow_id": "flow123", "task_count": 3 }
```

If there are problems you get a `422` with a list of what's wrong:

```json
{
  "detail": [
    "start_task 'nonexistent' is not defined in tasks.",
    "Condition 'cond1': target_task_success 'ghost_task' not defined."
  ]
}
```

---

### `GET /health`

```json
{ "status": "ok" }
```

---

## Running it

The `Makefile` has everything you need:

```bash
make install      # install dev dependencies
make run          # start with hot reload on :8000
make test         # run the test suite
make lint         # ruff check (E, F, W, I, UP)
make format       # ruff format
make build        # build production Docker image
make build-dev    # build dev Docker image
make up           # run production container
make dev          # run dev container with source mounted
```

Swagger UI is at http://localhost:8000/docs — the easiest way to try it out.

---

## Tests

```bash
make test
```

32 tests, 91% coverage. The suite covers the happy path, failure/abort scenarios,
edge cases in the engine (missing tasks, no conditions, single-task flows), and
the validation endpoint.
