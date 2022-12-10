import logging
import sys
import typing


_FORMAT = "[{asctime}][{name}][{levelname}][{module}] {message}"


def configure(
    level: typing.Union[str, int] = logging.INFO,
    name: str = None,
) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    common_handler = logging.StreamHandler(
        stream=sys.stdout,
    )
    common_handler.setLevel(logging.DEBUG)

    error_handler = logging.StreamHandler(
        stream=sys.stderr,
    )
    error_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        fmt=_FORMAT,
        style='{',
    )
    common_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    logger.addHandler(common_handler)
    logger.addHandler(error_handler)


def get(
    level: typing.Union[str, int] = logging.INFO,
    name: str = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
