import dataclasses
import datetime
import typing

import dacite
import dateutil.parser
import orjson


_T = typing.TypeVar("_T")


def _parse_dt(val: str) -> datetime.datetime:
    result = dateutil.parser.parse(val)
    return result.replace(tzinfo=None)


def parse(
    cls_: typing.Type[_T],
    data: typing.Union[str, bytes, typing.Mapping],
) -> _T:
    if isinstance(data, (str, bytes)):
        data = orjson.loads(data)

    if dataclasses.is_dataclass(cls_):
        return dacite.from_dict(
            data_class=cls_,
            data=data,
            config=dacite.Config({
                datetime.datetime: _parse_dt,
            }),
        )

    return cls_(data)
