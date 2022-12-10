import dataclasses


@dataclasses.dataclass(slots=True)
class Worker:
    ip: str
    address: str
    hardware: str
    hardware_id: str
    caption: str


@dataclasses.dataclass(slots=True)
class WorkerConnection:
    id: int
