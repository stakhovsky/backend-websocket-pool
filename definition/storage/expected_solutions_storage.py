import typing


Height = typing.TypeVar('Height', bound=int)
Target = typing.TypeVar('Target', bound=int)


class Storage(typing.Protocol):
    def open(self) -> None:
        ...

    def wait(
        self,
        height: Height,
        target: Target,
    ) -> None:
        ...

    def is_waits(
        self,
        height: Height,
        target: Target,
    ) -> bool:
        ...

    def close(self) -> None:
        ...
