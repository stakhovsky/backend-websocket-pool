import asyncio
import functools

import definition.entity.job

import libs.database.storage.job_storage
import libs.kafka.producer
import libs.logger
import libs.rabbitmq.consumer

import apps.process_job_worker.settings
import apps.process_job_worker.usecase


async def main(
    cfg: apps.process_job_worker.settings.Settings,
):
    logger = libs.logger.get(
        name=cfg.logger.name,
        level=cfg.logger.level,
    )

    job_consumer = libs.rabbitmq.consumer.Consumer(
        address=cfg.job_consumer.rabbitmq_address,
        user=cfg.job_consumer.rabbitmq_user,
        password=cfg.job_consumer.rabbitmq_password,
        queue=cfg.job_consumer.rabbitmq_queue,
    )
    await job_consumer.open()

    job_storage = libs.database.storage.job_storage.Storage(
        db_dsn=cfg.job_storage.postgresql_dsn,
        redis_dsn=cfg.job_storage.redis_dsn,
        record_ttl_seconds=cfg.job_storage.record_ttl_seconds,
    )
    await job_storage.open()

    job_producer = libs.kafka.producer.Producer(
        servers=cfg.job_producer.kafka_servers,
        user=cfg.job_producer.kafka_user,
        password=cfg.job_producer.kafka_password,
        topic=cfg.job_producer.kafka_topic,
    )
    await job_producer.open()

    logger.debug(f"Starting worker")
    try:
        await job_consumer.consume(
            message_cls=definition.entity.job.JobInput,
            handler=functools.partial(
                apps.process_job_worker.usecase.persist_and_broadcast_job,
                logger=logger,
                job_storage=job_storage,
                job_producer=job_producer,
            ),
            logger=logger,
        )
    except Exception as exc:
        logger.exception(exc)
        logger.debug(f"Worker halt")
    finally:
        await job_storage.close(
            logger=logger,
        )
        await job_producer.close(
            logger=logger,
        )
        await job_consumer.close(
            logger=logger,
        )
        logger.debug(f"Worker stopped")


if __name__ == "__main__":
    import simple_dataclass_settings

    simple_dataclass_settings.read_envfile()
    settings = simple_dataclass_settings.populate(apps.process_job_worker.settings.Settings)
    libs.logger.configure(
        level=settings.logger.root_level,
    )

    asyncio.run(main(
        cfg=settings,
    ))
