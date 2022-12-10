import typing


_T = typing.TypeVar("_T")


def get_value(
    item: _T,
    key: str,
) -> typing.Any:
    try:
        return getattr(item, key)
    except AttributeError:
        return item[key]
