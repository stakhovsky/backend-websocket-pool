import asyncio
import functools
import logging

import definition.entity.job
import definition.entity.solution
import definition.consumer
import definition.producer
import definition.storage.expected_solutions_storage
import definition.server

import libs.in_memory.expected_solutions_storage
import libs.json
import libs.parsing


async def _handle_solution(
    solution_data: definition.entity.solution.SolutionTransferData,
    logger: logging.Logger,
    expected_solution_storage: definition.storage.expected_solutions_storage.Storage,
    connection: definition.server.Connection,
) -> None:
    log_prefix = (
        f"[Connection {id(connection)}][Task ID {solution_data.task_id}]"
        f"[Height {solution_data.solution_height}][Target {solution_data.solution_target}]"
    )
    logger.debug(f"{log_prefix} Got solution data")

    if not expected_solution_storage.is_waits(
        height=solution_data.solution_height,
        target=solution_data.solution_target,
    ):
        logger.debug(f"{log_prefix} Solution is not eligible")
        return

    try:
        message = libs.json.dumps(
            definition.entity.solution.SolutionOutput(**solution_data.solution)
        )
    except Exception as exc:
        logger.debug(f"{log_prefix} Can not create solution message")
        logger.exception(exc)
        return

    try:
        await connection.send(message)
        logger.debug(f"{log_prefix} Solution sent")
    except Exception as exc:
        logger.debug(f"{log_prefix} Can not send solution to connection")
        logger.exception(exc)

    logger.debug(f"{log_prefix} Solution processing done")


async def _consume_solutions(
    connection: definition.server.Connection,
    solution_consumer: definition.consumer.Consumer,
    expected_solution_storage: definition.storage.expected_solutions_storage.Storage,
    logger: logging.Logger,
) -> None:
    try:
        await solution_consumer.consume(
            message_cls=definition.entity.solution.SolutionTransferData,
            handler=functools.partial(
                _handle_solution,
                logger=logger,
                expected_solution_storage=expected_solution_storage,
                connection=connection,
            ),
            logger=logger,
        )
    finally:
        if connection.open:
            try:
                await connection.close(1011)
            except Exception as exc:
                logger.exception(exc)


async def _create_connection_consumer(
    connection: definition.server.Connection,
    solution_consumer_factory: definition.consumer.ConsumerFactory,
    expected_solution_storage: definition.storage.expected_solutions_storage.Storage,
    logger: logging.Logger,
) -> definition.consumer.Consumer:
    solution_consumer = await solution_consumer_factory.spawn()
    asyncio.get_event_loop().create_task(_consume_solutions(
        connection=connection,
        solution_consumer=solution_consumer,
        expected_solution_storage=expected_solution_storage,
        logger=logger,
    ))
    return solution_consumer


async def handle_node_connection(
    connection: definition.server.Connection,
    logger: logging.Logger,
    solution_consumer_factory: definition.consumer.ConsumerFactory,
    job_producer: definition.producer.Producer,
) -> None:
    log_prefix = f"[Connection {id(connection)}]"
    logger.debug(f"{log_prefix} Connection started")

    expected_solution_storage = libs.in_memory.expected_solutions_storage.Storage(
        logger=logger,
    )

    try:
        solution_consumer = await _create_connection_consumer(
            connection=connection,
            solution_consumer_factory=solution_consumer_factory,
            expected_solution_storage=expected_solution_storage,
            logger=logger,
        )
    except Exception as exc:
        logger.exception(exc)
        logger.debug(f"{log_prefix} Could not start consumer")
        await connection.close(1011)
        return

    try:
        async for data in connection:
            try:
                job = libs.parsing.parse(definition.entity.job.JobInput, data)
            except Exception as exc:
                logger.debug(f"{log_prefix} Got unknown job")
                logger.exception(exc)
                continue

            try:
                await job_producer.produce(
                    message=job,
                )
            except Exception as exc:
                logger.debug(f"{log_prefix}[Height: {job.block_height}] Error while processing job")
                logger.exception(exc)
                await connection.close(1011)
                break
            else:
                expected_solution_storage.wait(
                    height=job.block_height,
                    target=job.proof_target,
                )
    except Exception as exc:
        logger.debug(f"{log_prefix} Critical error during connection")
        logger.exception(exc)
    finally:
        await solution_consumer.close(
            logger=logger,
        )
        expected_solution_storage.close()
        logger.debug(f"{log_prefix} Connection closed")
