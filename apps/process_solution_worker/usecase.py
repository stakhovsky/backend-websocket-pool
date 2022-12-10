import logging

import definition.entity.solution
import definition.producer
import definition.storage.job_reader
import definition.storage.solution_storage


async def persist_and_broadcast_solution(
    solution: definition.entity.solution.SolutionInput,
    logger: logging.Logger,
    solution_storage: definition.storage.solution_storage.Storage,
    job_reader: definition.storage.job_reader.Reader,
    solution_producer: definition.producer.Producer,
) -> None:
    log_prefix = (
        f"[Task ID: {solution.task_id}]"
        f"[Hardware ID: {solution.hardware_id}]"
        f"[Caption: {solution.caption}]"
    )

    logger.debug(f"{log_prefix} Processing solution")
    is_newly_stored, solution_storage_metadata = await solution_storage.store(solution)
    if not is_newly_stored:
        logger.info(
            f"{log_prefix}[Solution: {solution_storage_metadata.unique_key}] "
            f"Duplicate solution"
        )
        return

    job_storage_metadata = await job_reader.get(
        task_id=solution.task_id,
    )
    if not job_storage_metadata:
        logger.info(
            f"{log_prefix}[Solution: {solution_storage_metadata.unique_key}] "
            f"Got unknown solution"
        )
        return
    solution_transfer_metadata = definition.entity.solution.SolutionTransferData(
        task_id=solution.task_id,
        solution_target=solution.solution_target,
        solution=solution.solution,
        solution_height=job_storage_metadata.block_height,
    )

    logger.debug(f"{log_prefix} Sending solution to broadcast")
    await solution_producer.produce(solution_transfer_metadata)
    marked_as_stored = await solution_storage.mark_stored(solution_storage_metadata)
    if marked_as_stored is False:
        logger.debug(
            f"{log_prefix} "
            f"Could not be marked as stored - "
            f"solution was already processed by other worker"
        )
    logger.debug(f"{log_prefix} Solution done")
