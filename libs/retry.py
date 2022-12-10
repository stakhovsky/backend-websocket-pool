import asyncio
import logging
import typing

import backoff


_T = typing.TypeVar("_T")


def retry(
    fn: typing.Optional[_T] = None,
    *,
    ignore_exceptions: typing.Sequence[typing.Type[Exception]] = (),
    attempts: int = 1,
) -> typing.Union[_T, typing.Callable[[_T], _T]]:
    def wrapper(
        fn_: _T,
    ) -> _T:
        return backoff.on_exception(
            backoff.expo,
            Exception,
            giveup=lambda exc: isinstance(exc, (asyncio.CancelledError, *ignore_exceptions)),
            giveup_log_level=logging.DEBUG,
            max_tries=attempts,
        )(fn_)

    if fn:
        return wrapper(fn)

    return wrapper
