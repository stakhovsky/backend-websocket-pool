import typing

import simple_dataclass_settings


@simple_dataclass_settings.settings
class _Logger:
    name: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_LOG_NAME",
        default="node-server",
    )
    level: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_LOG_LEVEL",
        default="DEBUG",
    )
    root_level: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_ROOT_LOG_LEVEL",
        default="ERROR",
    )


@simple_dataclass_settings.settings
class _SolutionConsumer:
    kafka_servers: typing.Sequence[str] = simple_dataclass_settings.field.list(
        var="NODE_SERVER_KAFKA_SERVERS",
        default=("kafka:9093",),
    )
    kafka_user: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_KAFKA_USER",
        default="kafka",
    )
    kafka_password: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_KAFKA_PASSWORD",
        default="kafka_password",
    )
    kafka_topic: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_KAFKA_TOPIC",
        default="solution",
    )


@simple_dataclass_settings.settings
class _SolutionBroadcaster:
    wait_time_seconds: int = simple_dataclass_settings.field.int(
        var="NODE_SERVER_SOLUTION_WAIT_TIME_SECONDS",
        default=20 * 60,
    )


@simple_dataclass_settings.settings
class _JobProducer:
    rabbitmq_address: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_RABBITMQ_ADDRESS",
        default="rabbitmq:5672",
    )
    rabbitmq_user: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_RABBITMQ_USER",
        default="rabbitmq",
    )
    rabbitmq_password: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_RABBITMQ_PASSWORD",
        default="rabbitmq_password",
    )
    rabbitmq_exchange: str = simple_dataclass_settings.field.str(
        var="NODE_SERVER_RABBITMQ_EXCHANGE",
        default="job",
    )


@simple_dataclass_settings.settings
class _Server:
    port: int = simple_dataclass_settings.field.int(
        var="NODE_SERVER_SERVER_PORT",
        default=8001,
    )


@simple_dataclass_settings.settings
class Settings:
    logger: _Logger
    solution_consumer: _SolutionConsumer
    solution_broadcaster: _SolutionBroadcaster
    job_producer: _JobProducer
    server: _Server
