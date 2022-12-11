import asyncio
import functools
import logging
import typing

import aiormq
import aiormq.types
import backoff

import definition.consumer

import libs.asyncio
import libs.parsing
import libs.retry


class Error(Exception):
    ...


class Consumer(definition.consumer.Consumer):
    _connect_retry_attempts: int = 5
    _retry_attempts: int = 3
    _stop_wait_time_seconds: int = 15

    __slots__ = (
        "_address",
        "_user",
        "_password",
        "_queue",

        "_connection",
    )

    def __init__(
        self,
        address: str = "rabbitmq:5672",
        user: str = "rabbitmq",
        password: str = "rabbitmq_password",
        queue: str = "queue",
    ) -> None:
        self._address = address
        self._user = user
        self._password = password
        self._queue = queue

        self._connection: typing.Optional[aiormq.Connection] = None

    @libs.retry.retry(
        attempts=_connect_retry_attempts,
    )
    async def open(self) -> None:
        self._connection = await aiormq.connect(
            f"amqp://{self._user}:{self._password}@{self._address}//",
        )

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        try:
            await self._connection.close(timeout=self._stop_wait_time_seconds)
        except Exception as exc:
            if isinstance(exc, asyncio.TimeoutError):
                return

            if logger is not None:
                logger.exception(exc)

    @libs.retry.retry(
        attempts=_retry_attempts,
    )
    async def _commit(
        self,
        message: aiormq.types.DeliveredMessage,
    ) -> None:
        await message.channel.basic_ack(
            message.delivery.delivery_tag,
        )

    async def _consume_message(
        self,
        message: aiormq.types.DeliveredMessage,
        message_cls: typing.Type[definition.consumer.Data],
        handler: typing.Callable[[definition.consumer.Data], typing.Awaitable[None]],
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        logger.debug(f"[Message ID {id(message)}] Processing message")
        try:
            data = libs.parsing.parse(message_cls, message.body)
        except Exception as exc:
            logger.debug(f"[Message ID {id(message)}] Unknown message format, skipping")
            if logger:
                logger.exception(exc)
            await self._commit(message)
            return

        try:
            await handler(data)
        except Exception as exc:
            logger.debug(f"[Message ID {id(message)}] Message processing failed")
            if logger:
                logger.exception(exc)
        else:
            await self._commit(message)
            logger.debug(f"[Message ID {id(message)}] Message processing done")

    async def consume(
        self,
        message_cls: typing.Type[definition.consumer.Data],
        handler: typing.Callable[[definition.consumer.Data], typing.Awaitable[None]],
        *_,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        channel = await self._connection.channel()
        await channel.basic_qos(
            prefetch_count=1,
        )

        try:
            await channel.basic_consume(
                queue=self._queue,
                consumer_callback=functools.partial(
                    self._consume_message,
                    message_cls=message_cls,
                    handler=handler,
                    logger=logger,
                ),
                no_ack=False,
            )
            while True:
                await libs.asyncio.stop_marker()
        finally:
            try:
                await channel.close()
            except Exception as exc:
                logger.exception(exc)
