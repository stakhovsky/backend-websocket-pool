import simple_dataclass_settings


@simple_dataclass_settings.settings
class _Logger:
    name: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_LOG_NAME",
        default="process-solution",
    )
    level: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_LOG_LEVEL",
        default="INFO",
    )
    root_level: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_ROOT_LOG_LEVEL",
        default="ERROR",
    )


@simple_dataclass_settings.settings
class _SolutionConsumer:
    rabbitmq_address: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_RABBITMQ_ADDRESS",
        default="rabbitmq:5672",
    )
    rabbitmq_user: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_RABBITMQ_USER",
        default="rabbitmq",
    )
    rabbitmq_password: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_RABBITMQ_PASSWORD",
        default="rabbitmq_password",
    )
    rabbitmq_queue: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_RABBITMQ_QUEUE",
        default="solution.persist_and_broadcast",
    )


@simple_dataclass_settings.settings
class _SolutionStorage:
    postgresql_dsn: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_SOLUTION_POSTGRESQL_DSN",
        default="postgresql+asyncpg://postgres:postgres@db:5432/postgres",
    )
    redis_dsn: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_REDIS_DSN",
        default="redis://redis:6379/",
    )
    record_ttl_seconds: int = simple_dataclass_settings.field.int(
        var="PROCESS_SOLUTION_WORKER_RECORD_TTL_SECONDS",
        default=60 * 60,
    )


@simple_dataclass_settings.settings
class _JobReader:
    postgresql_dsn: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_JOB_POSTGRESQL_DSN",
        default="postgresql+asyncpg://postgres:postgres@db:5432/postgres",
    )


@simple_dataclass_settings.settings
class _SolutionProducer:
    kafka_servers: str = simple_dataclass_settings.field.list(
        var="PROCESS_SOLUTION_WORKER_KAFKA_SERVERS",
        default=("kafka:9093",),
    )
    kafka_user: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_KAFKA_USER",
        default="kafka",
    )
    kafka_password: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_KAFKA_PASSWORD",
        default="kafka_password",
    )
    kafka_topic: str = simple_dataclass_settings.field.str(
        var="PROCESS_SOLUTION_WORKER_KAFKA_TOPIC",
        default="solution",
    )


@simple_dataclass_settings.settings
class Settings:
    logger: _Logger
    solution_consumer: _SolutionConsumer
    solution_storage: _SolutionStorage
    job_reader: _JobReader
    solution_producer: _SolutionProducer
