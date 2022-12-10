import typing


Height = typing.TypeVar('Height', bound=int)


class Shield(typing.Protocol):
    async def ensure_priority(
        self,
        height: Height,
    ) -> typing.AsyncContextManager[bool]:
        ...

    def store_priority(
        self,
        height: Height,
    ) -> None:
        ...
