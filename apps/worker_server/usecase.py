import asyncio
import functools
import logging
import typing

import definition.entity.job
import definition.entity.solution
import definition.entity.worker
import definition.consumer
import definition.producer
import definition.job_priority_shield
import definition.storage.worker_storage
import definition.server

import libs.in_memory.job_priority_shield
import libs.json
import libs.parsing


async def _handle_job(
    job: definition.entity.job.JobTransferMetadata,
    logger: logging.Logger,
    priority_shield: definition.job_priority_shield.Shield,
    connection: definition.server.Connection,
) -> None:
    log_prefix = (
        f"[Connection {id(connection)}][Task {job.task_id}]"
        f"[Height {job.block_height}]"
    )
    logger.debug(f"{log_prefix} Got job data")

    async with priority_shield.ensure_priority(job.block_height) as should_process:
        if not should_process:
            logger.debug(f"{log_prefix} Already processing more prior job")
            return

        try:
            message = libs.json.dumps(definition.entity.job.JobOutput(
                task_id=job.task_id,
                epoch_challenge=job.epoch_challenge,
            ))
        except Exception as exc:
            logger.debug(f"{log_prefix} Can not create job message")
            logger.exception(exc)
            return

        try:
            await connection.send(message)
        except Exception as exc:
            logger.debug(f"{log_prefix} Can not send job to connection")
            logger.exception(exc)
        else:
            logger.debug(f"{log_prefix} Job sent")
            priority_shield.store_priority(job.block_height)


async def _consume_jobs(
    connection: definition.server.Connection,
    job_consumer: definition.consumer.Consumer,
    priority_shield: definition.job_priority_shield.Shield,
    logger: logging.Logger,
) -> None:
    try:
        await job_consumer.consume(
            message_cls=definition.entity.job.JobTransferMetadata,
            handler=functools.partial(
                _handle_job,
                logger=logger,
                priority_shield=priority_shield,
                connection=connection,
            ),
            logger=logger,
        )
    except Exception as exc:
        if not isinstance(exc, definition.consumer.DisconnectError):
            logger.exception(exc)
    finally:
        if connection.open:
            try:
                await connection.close(1011)
            except Exception as exc:
                logger.exception(exc)


async def _create_connection_consumer(
    connection: definition.server.Connection,
    job_consumer_factory: definition.consumer.ConsumerFactory,
    priority_shield: definition.job_priority_shield.Shield,
    logger: logging.Logger,
) -> typing.Tuple[definition.consumer.Consumer, asyncio.Task]:
    job_consumer = await job_consumer_factory.spawn()
    consume_task = asyncio.get_event_loop().create_task(_consume_jobs(
        connection=connection,
        job_consumer=job_consumer,
        priority_shield=priority_shield,
        logger=logger,
    ))
    return job_consumer, consume_task


async def _try_register_worker(
    data: bytes,
    connection: definition.server.Connection,
    logger: logging.Logger,
    job_consumer_factory: definition.consumer.ConsumerFactory,
    worker_storage: definition.storage.worker_storage.Storage,
) -> typing.Tuple[
    bool,
    typing.Optional[definition.entity.worker.Worker],
    typing.Optional[definition.entity.worker.WorkerConnection],
    typing.Optional[definition.consumer.Consumer],
    typing.Optional[asyncio.Task],
]:
    log_prefix = f"[Connection {id(connection)}]"

    try:
        worker = libs.parsing.parse(definition.entity.worker.Worker, data)
    except Exception as exc:
        logger.exception(exc)
        logger.debug(f"{log_prefix} Got unknown worker handshake")
        await connection.close(3000)
        return False, None, None, None, None

    try:
        worker_connection = await worker_storage.store_connect(worker)
    except Exception as exc:
        logger.exception(exc)
        logger.debug(f"{log_prefix} Got error while saving worker connection")
        await connection.close(1011)
        return False, worker, None, None, None

    priority_shield = libs.in_memory.job_priority_shield.Shield()
    try:
        job_consumer, consume_task = await _create_connection_consumer(
            connection=connection,
            job_consumer_factory=job_consumer_factory,
            priority_shield=priority_shield,
            logger=logger,
        )
    except Exception as exc:
        logger.exception(exc)
        logger.debug(f"{log_prefix} Could not start consumer")
        await connection.close(1011)
        return False, worker, worker_connection, None, None

    logger.debug(f"{log_prefix} Worker registered")
    return True, worker, worker_connection, job_consumer, consume_task


async def handle_worker_connection(
    connection: definition.server.Connection,
    logger: logging.Logger,
    job_consumer_factory: definition.consumer.ConsumerFactory,
    worker_storage: definition.storage.worker_storage.Storage,
    solution_producer: definition.producer.Producer,
) -> None:
    worker: typing.Optional[definition.entity.worker.Worker] = None
    worker_connection: typing.Optional[definition.entity.worker.WorkerConnection] = None
    job_consumer: typing.Optional[definition.consumer.Consumer] = None
    consume_task: typing.Optional[asyncio.Task] = None

    log_prefix = f"[Connection {id(connection)}]"
    logger.debug(f"{log_prefix} Connection started")

    try:
        async for data in connection:
            if worker is None:
                is_success, worker, worker_connection, job_consumer, consume_task = await _try_register_worker(
                    data=data,
                    connection=connection,
                    logger=logger,
                    job_consumer_factory=job_consumer_factory,
                    worker_storage=worker_storage,
                )
                if not is_success:
                    break
                continue

            try:
                raw_solution = libs.parsing.parse(definition.entity.solution.RawSolutionInput, data)
                solution = definition.entity.solution.SolutionInput(
                    hardware_id=worker.hardware_id,
                    caption=worker.caption,
                    task_id=raw_solution.task_id,
                    solution=raw_solution.solution,
                    solution_target=raw_solution.solution_target,
                )
            except Exception as exc:
                logger.exception(exc)
                logger.debug(f"{log_prefix} Got unknown solution")
                continue

            try:
                logger.debug(f"{log_prefix}[Task ID: {solution.task_id}] Processing solution")
                await solution_producer.produce(
                    message=solution,
                )
            except Exception as exc:
                logger.debug(f"{log_prefix}[Task ID: {solution.task_id}] Error while processing solution")
                logger.exception(exc)
                await connection.close(1011)
                break
    except Exception as exc:
        logger.debug(f"{log_prefix} Critical error during connection")
        logger.exception(exc)
    finally:
        if worker_connection is not None:
            try:
                await worker_storage.store_disconnect(worker_connection)
            except Exception as exc:
                logger.exception(exc)
                logger.debug(f"{log_prefix} Got error while saving worker disconnection")

        if consume_task is not None:
            if not consume_task.done():
                consume_task.cancel()

        if job_consumer is not None:
            await job_consumer.close(
                logger=logger,
            )

        logger.debug(f"{log_prefix} Connection closed")
