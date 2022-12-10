import asyncio
import functools

import definition.entity.solution

import libs.database.storage.job_reader
import libs.database.storage.solution_storage
import libs.kafka.producer
import libs.logger
import libs.rabbitmq.consumer

import apps.process_solution_worker.settings
import apps.process_solution_worker.usecase


async def main(
    cfg: apps.process_solution_worker.settings.Settings,
):
    logger = libs.logger.get(
        name=cfg.logger.name,
        level=cfg.logger.level,
    )

    solution_consumer = libs.rabbitmq.consumer.Consumer(
        address=cfg.solution_consumer.rabbitmq_address,
        user=cfg.solution_consumer.rabbitmq_user,
        password=cfg.solution_consumer.rabbitmq_password,
        queue=cfg.solution_consumer.rabbitmq_queue,
    )
    await solution_consumer.open()

    solution_storage = libs.database.storage.solution_storage.Storage(
        db_dsn=cfg.solution_storage.postgresql_dsn,
        redis_dsn=cfg.solution_storage.redis_dsn,
        record_ttl_seconds=cfg.solution_storage.record_ttl_seconds,
    )
    await solution_storage.open()

    job_reader = libs.database.storage.job_reader.Reader(
        db_dsn=cfg.job_reader.postgresql_dsn,
    )
    await job_reader.open()

    solution_producer = libs.kafka.producer.Producer(
        servers=cfg.solution_producer.kafka_servers,
        user=cfg.solution_producer.kafka_user,
        password=cfg.solution_producer.kafka_password,
        topic=cfg.solution_producer.kafka_topic,
    )
    await solution_producer.open()

    logger.debug(f"Starting worker")
    try:
        await solution_consumer.consume(
            message_cls=definition.entity.solution.SolutionInput,
            handler=functools.partial(
                apps.process_solution_worker.usecase.persist_and_broadcast_solution,
                logger=logger,
                solution_storage=solution_storage,
                job_reader=job_reader,
                solution_producer=solution_producer,
            ),
            logger=logger,
        )
    except Exception as exc:
        logger.exception(exc)
        logger.debug(f"Worker halt")
    finally:
        await solution_storage.close(
            logger=logger,
        )
        await solution_producer.close(
            logger=logger,
        )
        await solution_consumer.close(
            logger=logger,
        )
        await job_reader.close(
            logger=logger,
        )
        logger.debug(f"Worker stopped")


if __name__ == "__main__":
    import simple_dataclass_settings

    simple_dataclass_settings.read_envfile()
    settings = simple_dataclass_settings.populate(apps.process_solution_worker.settings.Settings)
    libs.logger.configure(
        level=settings.logger.root_level,
    )

    asyncio.run(main(
        cfg=settings,
    ))
