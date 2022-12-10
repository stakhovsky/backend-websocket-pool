import typing

import orjson


_Data = typing.TypeVar('_Data')


def dumps(
    data: _Data,
    option=orjson.OPT_UTC_Z | orjson.OPT_NAIVE_UTC | orjson.OPT_NON_STR_KEYS | orjson.OPT_SORT_KEYS,
) -> bytes:
    return orjson.dumps(data, option=option)
