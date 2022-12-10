import typing

import simple_dataclass_settings


@simple_dataclass_settings.settings
class _Logger:
    name: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_LOG_NAME",
        default="worker-server",
    )
    level: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_LOG_LEVEL",
        default="DEBUG",
    )
    root_level: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_ROOT_LOG_LEVEL",
        default="ERROR",
    )


@simple_dataclass_settings.settings
class _JobConsumer:
    kafka_servers: typing.Sequence[str] = simple_dataclass_settings.field.list(
        var="WORKER_SERVER_KAFKA_SERVERS",
        default=("kafka:9093",),
    )
    kafka_user: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_KAFKA_USER",
        default="kafka",
    )
    kafka_password: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_KAFKA_PASSWORD",
        default="kafka_password",
    )
    kafka_topic: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_KAFKA_TOPIC",
        default="job",
    )


@simple_dataclass_settings.settings
class _SolutionProducer:
    rabbitmq_address: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_RABBITMQ_ADDRESS",
        default="rabbitmq:5672",
    )
    rabbitmq_user: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_RABBITMQ_USER",
        default="rabbitmq",
    )
    rabbitmq_password: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_RABBITMQ_PASSWORD",
        default="rabbitmq_password",
    )
    rabbitmq_exchange: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_RABBITMQ_EXCHANGE",
        default="solution",
    )


@simple_dataclass_settings.settings
class _WorkerStorage:
    postgresql_dsn: str = simple_dataclass_settings.field.str(
        var="WORKER_SERVER_POSTGRESQL_DSN",
        default="postgresql+asyncpg://postgres:postgres@db:5432/postgres",
    )


@simple_dataclass_settings.settings
class _Server:
    port: int = simple_dataclass_settings.field.int(
        var="WORKER_SERVER_SERVER_PORT",
        default=8002,
    )


@simple_dataclass_settings.settings
class Settings:
    logger: _Logger
    job_consumer: _JobConsumer
    solution_producer: _SolutionProducer
    worker_storage: _WorkerStorage
    server: _Server
