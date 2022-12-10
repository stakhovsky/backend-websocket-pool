import logging
import uuid

import definition.entity.job
import definition.storage.job_storage

import libs.database.storage.base
import libs.database.tables.job
import libs.json


class Storage(libs.database.storage.base.Storage, definition.storage.job_storage.Storage):
    table = libs.database.tables.job.job
    index_elements = ["block_height", ]
    bypass_column_name = "block_height"
    stored_entry_dedup_key = "task_id"
    dedup_prefix = "job_"
    exception_class = definition.storage.job_storage.Error

    def _prepare_database_values(
        self,
        entity: definition.entity.job.JobInput,
    ) -> dict:
        return {
            "block_height": entity.block_height,
            "epoch_challenge": libs.json.dumps(entity.epoch_challenge).decode(),
            "task_id": str(uuid.uuid4()),
        }

    def _prepare_result_entry(
        self,
        record,
    ) -> definition.entity.job.JobStorageMetadata:
        return definition.entity.job.JobStorageMetadata(
            task_id=record.task_id,
            block_height=record.block_height,
            created_at=record.created_at,
        )
