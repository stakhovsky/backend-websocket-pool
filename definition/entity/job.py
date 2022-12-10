import datetime
import dataclasses


@dataclasses.dataclass(slots=True)
class JobInput:
    epoch_challenge: dict
    proof_target: int
    block_height: int


@dataclasses.dataclass(slots=True)
class JobStorageMetadata:
    task_id: str
    block_height: int
    created_at: datetime.datetime


@dataclasses.dataclass(slots=True)
class JobTransferMetadata:
    task_id: str
    epoch_challenge: dict
    block_height: int
    created_at: datetime.datetime


@dataclasses.dataclass(slots=True)
class JobOutput:
    task_id: str
    epoch_challenge: dict
