import asyncio
import functools

import libs.database.storage.worker_storage
import libs.kafka.consumer
import libs.logger
import libs.rabbitmq.producer
import libs.server

import apps.worker_server.settings
import apps.worker_server.usecase


async def main(
    cfg: apps.worker_server.settings.Settings,
):
    logger = libs.logger.get(
        name=cfg.logger.name,
        level=cfg.logger.level,
    )

    worker_storage = libs.database.storage.worker_storage.Storage(
        db_dsn=cfg.worker_storage.postgresql_dsn,
    )
    await worker_storage.open()

    solution_producer = libs.rabbitmq.producer.Producer(
        address=cfg.solution_producer.rabbitmq_address,
        user=cfg.solution_producer.rabbitmq_user,
        password=cfg.solution_producer.rabbitmq_password,
        exchange=cfg.solution_producer.rabbitmq_exchange,
    )
    await solution_producer.open()

    server = libs.server.Server(
        port=cfg.server.port,
    )

    job_consumer_factory = libs.kafka.consumer.ConsumerFactory(
        servers=cfg.job_consumer.kafka_servers,
        user=cfg.job_consumer.kafka_user,
        password=cfg.job_consumer.kafka_password,
        topic=cfg.job_consumer.kafka_topic,
    )

    logger.debug(f"Starting server")
    try:
        await server.start(
            handler=functools.partial(
                apps.worker_server.usecase.handle_worker_connection,
                logger=logger,
                job_consumer_factory=job_consumer_factory,
                worker_storage=worker_storage,
                solution_producer=solution_producer,
            ),
        )
    except Exception as exc:
        logger.exception(exc)
        logger.debug(f"Server halt")
    finally:
        await solution_producer.close(
            logger=logger,
        )
        await worker_storage.close(
            logger=logger,
        )
        logger.debug(f"Server stopped")


if __name__ == "__main__":
    import simple_dataclass_settings

    simple_dataclass_settings.read_envfile()
    settings = simple_dataclass_settings.populate(apps.worker_server.settings.Settings)
    libs.logger.configure(
        level=settings.logger.root_level,
    )

    asyncio.run(main(
        cfg=settings,
    ))
