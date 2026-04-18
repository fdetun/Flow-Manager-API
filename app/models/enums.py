from enum import StrEnum


class TaskStatus(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"


class FlowStatus(StrEnum):
    COMPLETED = "completed"
    ABORTED = "aborted"


class ConditionOutcome(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"


FLOW_END = "end"
