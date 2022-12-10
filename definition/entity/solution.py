import dataclasses
import datetime
import typing


@dataclasses.dataclass(slots=True)
class RawSolutionInput:
    task_id: str
    solution: dict
    solution_target: int


@dataclasses.dataclass(slots=True)
class SolutionInput:
    hardware_id: str
    caption: str
    task_id: str
    solution: dict
    solution_target: int


@dataclasses.dataclass(slots=True)
class SolutionStorageData:
    unique_key: str
    created_at: datetime.datetime


@dataclasses.dataclass(slots=True)
class SolutionTransferData:
    task_id: str
    solution_target: int
    solution: dict
    solution_height: int


SolutionOutput = typing.TypedDict(
    "SolutionOutput",
    {
        "solution": dict,
        "proof.w": dict,
    },
)
