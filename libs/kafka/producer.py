import asyncio
import logging
import typing

import aiokafka

import definition.producer

import libs.json
import libs.retry


class Error(Exception):
    ...


class Producer(definition.producer.Producer):
    _connect_retry_attempts: int = 5
    _retry_attempts: int = 3
    _stop_wait_time_seconds: int = 15

    __slots__ = (
        "_servers",
        "_user",
        "_password",
        "_topic",

        "_producer",
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

        self._producer: typing.Optional[aiokafka.AIOKafkaProducer] = None

    @libs.retry.retry(
        attempts=_connect_retry_attempts,
    )
    async def open(self) -> None:
        self._producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=self._servers,
            security_protocol="PLAINTEXT",
            sasl_mechanism="PLAIN",
            sasl_plain_username=self._user,
            sasl_plain_password=self._password,
        )
        try:
            await self._producer.start()
        except Exception:
            await self._producer.stop()
            raise

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        try:
            await asyncio.wait_for(self._producer.stop(), self._stop_wait_time_seconds)
        except Exception as exc:
            if isinstance(exc, asyncio.TimeoutError):
                return

            if logger is not None:
                logger.exception(exc)

    @libs.retry.retry(
        attempts=_retry_attempts,
    )
    async def produce(
        self,
        message: definition.producer.Message,
    ) -> None:
        if not isinstance(message, bytes):
            message = libs.json.dumps(message)

        await self._producer.send(
            topic=self._topic,
            value=message,
        )
