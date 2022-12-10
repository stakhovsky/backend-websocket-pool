import typing

import simple_dataclass_settings

import misc.managmenet.kafka
import misc.managmenet.rabbitmq
import misc.managmenet.database.migration

import libs.database.tables.job
import libs.database.tables.migration.job

import libs.database.tables.solution
import libs.database.tables.migration.solution

import libs.database.tables.worker
import libs.database.tables.migration.worker


@simple_dataclass_settings.settings
class _Kafka:
    servers: typing.Sequence[str] = simple_dataclass_settings.field.list(
        var="KAFKA_SERVERS",
        default=("kafka:9093",),
    )
    user: str = simple_dataclass_settings.field.str(
        var="KAFKA_USER",
        default="kafka",
    )
    password: str = simple_dataclass_settings.field.str(
        var="KAFKA_PASSWORD",
        default="kafka_password",
    )

    solution_topic: str = simple_dataclass_settings.field.str(
        var="KAFKA_SOLUTION_TOPIC",
        default="solution",
    )
    solution_topic_retention_milliseconds: int = simple_dataclass_settings.field.int(
        var="KAFKA_SOLUTION_TOPIC_RETENTION_MILLISECONDS",
        default=25 * 60 * 1000,
    )

    job_topic: str = simple_dataclass_settings.field.str(
        var="KAFKA_JOB_TOPIC",
        default="job",
    )
    job_topic_retention_milliseconds: int = simple_dataclass_settings.field.int(
        var="KAFKA_JOB_TOPIC_RETENTION_MILLISECONDS",
        default=25 * 60 * 1000,
    )


@simple_dataclass_settings.settings
class _Rabbitmq:
    address: str = simple_dataclass_settings.field.str(
        var="RABBITMQ_ADDRESS",
        default="rabbitmq:5672",
    )
    user: str = simple_dataclass_settings.field.str(
        var="RABBITMQ_USER",
        default="rabbitmq",
    )
    password: str = simple_dataclass_settings.field.str(
        var="RABBITMQ_PASSWORD",
        default="rabbitmq_password",
    )

    job_exchange: str = simple_dataclass_settings.field.str(
        var="RABBITMQ_JOB_EXCHANGE",
        default="job",
    )
    job_persist_queue: str = simple_dataclass_settings.field.str(
        var="RABBITMQ_JOB_PERSIST_QUEUE",
        default="job.persist_and_broadcast",
    )

    solution_exchange: str = simple_dataclass_settings.field.str(
        var="RABBITMQ_SOLUTION_EXCHANGE",
        default="solution",
    )
    solution_persist_queue: str = simple_dataclass_settings.field.str(
        var="RABBITMQ_SOLUTION_PERSIST_QUEUE",
        default="solution.persist_and_broadcast",
    )


@simple_dataclass_settings.settings
class _Postgresql:
    dsn: str = simple_dataclass_settings.field.str(
        var="POSTGRESQL_DSN",
        default="postgresql://postgres:postgres@db:5432/postgres",
    )


@simple_dataclass_settings.settings
class Settings:
    kafka: _Kafka
    rabbitmq: _Rabbitmq
    postgresql: _Postgresql


def setup(
    cfg: Settings,
):
    misc.managmenet.kafka.ensure_topic(
        servers=cfg.kafka.servers,
        user=cfg.kafka.user,
        password=cfg.kafka.password,
        topic_name=cfg.kafka.solution_topic,
        topic_retention_milliseconds=cfg.kafka.solution_topic_retention_milliseconds,
    )
    misc.managmenet.kafka.ensure_topic(
        servers=cfg.kafka.servers,
        user=cfg.kafka.user,
        password=cfg.kafka.password,
        topic_name=cfg.kafka.job_topic,
        topic_retention_milliseconds=cfg.kafka.job_topic_retention_milliseconds,
    )

    misc.managmenet.rabbitmq.create_exchange_and_queues(
        address=cfg.rabbitmq.address,
        user=cfg.rabbitmq.user,
        password=cfg.rabbitmq.password,
        exchange=cfg.rabbitmq.job_exchange,
        queues=(cfg.rabbitmq.job_persist_queue, ),
    )
    misc.managmenet.rabbitmq.create_exchange_and_queues(
        address=cfg.rabbitmq.address,
        user=cfg.rabbitmq.user,
        password=cfg.rabbitmq.password,
        exchange=cfg.rabbitmq.solution_exchange,
        queues=(cfg.rabbitmq.solution_persist_queue, ),
    )

    misc.managmenet.database.migration.migrate(
        db_dsn=cfg.postgresql.dsn,
        metadata=libs.database.tables.job.metadata,
        migrations_dir=libs.database.tables.migration.job,
        version_table=libs.database.tables.migration.job.__versions_table__,
    )
    misc.managmenet.database.migration.migrate(
        db_dsn=cfg.postgresql.dsn,
        metadata=libs.database.tables.solution.metadata,
        migrations_dir=libs.database.tables.migration.solution,
        version_table=libs.database.tables.migration.solution.__versions_table__,
    )
    misc.managmenet.database.migration.migrate(
        db_dsn=cfg.postgresql.dsn,
        metadata=libs.database.tables.worker.metadata,
        migrations_dir=libs.database.tables.migration.worker,
        version_table=libs.database.tables.migration.worker.__versions_table__,
    )


if __name__ == '__main__':
    simple_dataclass_settings.read_envfile('./.env.setup_local_environment')

    settings = simple_dataclass_settings.populate(Settings)

    setup(
        cfg=settings,
    )
