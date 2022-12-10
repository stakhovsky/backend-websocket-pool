import logging

import definition.entity.job
import definition.producer
import definition.storage.job_storage


async def persist_and_broadcast_job(
    job: definition.entity.job.JobInput,
    logger: logging.Logger,
    job_storage: definition.storage.job_storage.Storage,
    job_producer: definition.producer.Producer,
) -> None:
    logger.debug(f"[Height: {job.block_height}] Processing task")
    is_newly_stored, job_storage_metadata = await job_storage.store(job)
    if not is_newly_stored:
        logger.debug(f"[Height: {job.block_height}][Task: {job_storage_metadata.task_id}] Task already processed, skipping")
        return

    job_transfer_metadata = definition.entity.job.JobTransferMetadata(
        task_id=job_storage_metadata.task_id,
        epoch_challenge=job.epoch_challenge,
        block_height=job.block_height,
        created_at=job_storage_metadata.created_at
    )

    logger.debug(f"[Height: {job.block_height}][Task: {job_storage_metadata.task_id}] Sending task to broadcast")
    await job_producer.produce(job_transfer_metadata)
    marked_as_stored = await job_storage.mark_stored(job_storage_metadata)
    if marked_as_stored is False:
        logger.info(
            f"[Height: {job.block_height}][Task: {job_storage_metadata.task_id}] "
            f"Could not be marked as stored - "
            f"task was already processed by other worker"
        )
    logger.debug(f"[Height: {job.block_height}][Task: {job_storage_metadata.task_id}] Task done")
