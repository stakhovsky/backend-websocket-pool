import asyncio
import logging
import time
import typing
import uuid

import aiokafka

import definition.consumer
import libs.parsing
import libs.retry


class _Message(typing.Protocol):
    topic: str
    partition: str
    offset: int
    value: bytes


class Error(Exception):
    ...


class Consumer(definition.consumer.Consumer):
    _connect_retry_attempts: int = 5
    _retry_attempts: int = 3
    _stop_wait_time_seconds: int = 5

    __slots__ = (
        "_servers",
        "_user",
        "_password",
        "_topic",

        "_consumer",
    )

    def __init__(
        self,
        servers: typing.Sequence[str] = ("kafka:9093",),
        user: str = "kafka",
        password: str = "kafka_password",
        topic: str = "topic",
    ) -> None:
        self._servers = servers
        self._user = user
        self._password = password
        self._topic = topic

        self._consumer: typing.Optional[aiokafka.AIOKafkaConsumer] = None

    @libs.retry.retry(
        attempts=_connect_retry_attempts,
    )
    async def open(self) -> None:
        group_id = f"{str(uuid.uuid4())}-{str(time.time_ns())}"
        self._consumer = aiokafka.AIOKafkaConsumer(
            self._topic,
            group_id=group_id,
            auto_offset_reset="earliest",
            bootstrap_servers=self._servers,
            security_protocol="PLAINTEXT",
            sasl_mechanism="PLAIN",
            sasl_plain_username=self._user,
            sasl_plain_password=self._password,
            enable_auto_commit=False,
        )
        try:
            await self._consumer.start()
        except Exception:
            await self._consumer.stop()
            raise

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        try:
            await asyncio.wait_for(self._consumer.stop(), self._stop_wait_time_seconds)
        except Exception as exc:
            if isinstance(exc, asyncio.TimeoutError):
                return

            if logger is not None:
                logger.exception(exc)

    @libs.retry.retry(
        attempts=_retry_attempts,
        ignore_exceptions=(definition.consumer.DisconnectError, ),
    )
    async def _commit(
        self,
        message: _Message,
    ) -> None:
        try:
            tp = aiokafka.TopicPartition(
                topic=message.topic,
                partition=message.partition,
            )
            await self._consumer.commit({
                tp: message.offset + 1,
            })
        except aiokafka.errors.ConsumerStoppedError as exc:
            raise definition.consumer.DisconnectError from exc
        except Exception as exc:
            raise Error from exc

    @libs.retry.retry(
        attempts=_retry_attempts,
        ignore_exceptions=(definition.consumer.DisconnectError, ),
    )
    async def _get_message(self) -> _Message:
        try:
            return await self._consumer.getone()
        except aiokafka.errors.ConsumerStoppedError as exc:
            raise definition.consumer.DisconnectError from exc
        except Exception as exc:
            raise Error from exc

    async def consume(
        self,
        message_cls: typing.Type[definition.consumer.Data],
        handler: typing.Callable[[definition.consumer.Data], typing.Awaitable[None]],
        *,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        while True:
            message = await self._get_message()

            try:
                data = libs.parsing.parse(message_cls, message.value)
            except Exception as exc:
                if logger:
                    logger.exception(exc)
                await self._commit(message)
                continue

            try:
                await handler(data)
            except Exception as exc:
                if logger:
                    logger.exception(exc)
            else:
                await self._commit(message)


class ConsumerFactory:
    __slots__ = (
        "_servers",
        "_user",
        "_password",
        "_topic",
    )

    def __init__(
        self,
        servers: typing.Sequence[str] = ("kafka:9093",),
        user: str = "kafka",
        password: str = "kafka_password",
        topic: str = "topic",
    ) -> None:
        self._servers = servers
        self._user = user
        self._password = password
        self._topic = topic

    async def spawn(self) -> Consumer:
        result = Consumer(
            servers=self._servers,
            user=self._user,
            password=self._password,
            topic=self._topic,
        )
        await result.open()
        return result
