import asyncio
import functools

import libs.kafka.consumer
import libs.logger
import libs.rabbitmq.producer
import libs.server

import apps.node_server.settings
import apps.node_server.usecase


async def main(
    cfg: apps.node_server.settings.Settings,
) -> None:
    logger = libs.logger.get(
        name=cfg.logger.name,
        level=cfg.logger.level,
    )

    job_producer = libs.rabbitmq.producer.Producer(
        address=cfg.job_producer.rabbitmq_address,
        user=cfg.job_producer.rabbitmq_user,
        password=cfg.job_producer.rabbitmq_password,
        exchange=cfg.job_producer.rabbitmq_exchange,
    )
    await job_producer.open()

    solution_consumer_factory = libs.kafka.consumer.ConsumerFactory(
        servers=cfg.solution_consumer.kafka_servers,
        user=cfg.solution_consumer.kafka_user,
        password=cfg.solution_consumer.kafka_password,
        topic=cfg.solution_consumer.kafka_topic,
    )

    server = libs.server.Server(
        port=cfg.server.port,
    )

    logger.debug(f"Starting server")
    try:
        await server.start(
            handler=functools.partial(
                apps.node_server.usecase.handle_node_connection,
                logger=logger,
                solution_consumer_factory=solution_consumer_factory,
                job_producer=job_producer,
            ),
        )
    except Exception as exc:
        logger.exception(exc)
        logger.debug(f"Server halt")
    finally:
        await job_producer.close(
            logger=logger,
        )
        logger.debug(f"Server stopped")


if __name__ == "__main__":
    import simple_dataclass_settings

    simple_dataclass_settings.read_envfile()
    settings = simple_dataclass_settings.populate(apps.node_server.settings.Settings)
    libs.logger.configure(
        level=settings.logger.root_level,
    )

    asyncio.run(main(
        cfg=settings,
    ))
