import logging

import definition.entity.solution
import definition.storage.solution_storage

import libs.database.storage.base
import libs.database.tables.solution
import libs.json


class Storage(libs.database.storage.base.Storage, definition.storage.solution_storage.Storage):
    table = libs.database.tables.solution.solution
    index_elements = ["unique_key", ]
    bypass_column_name = "unique_key"
    stored_entry_dedup_key = "unique_key"
    dedup_prefix = "solution_"
    exception_class = definition.storage.solution_storage.Error

    def _prepare_database_values(
        self,
        entity: definition.entity.solution.SolutionInput,
    ) -> dict:
        return {
            "hardware_id": entity.hardware_id,
            "caption": entity.caption,
            "task_id": entity.task_id,
            "unique_key": str(entity.solution["partial_solution"]["nonce"]),  # TODO: re-check
            "solution": libs.json.dumps(entity.solution).decode(),
        }

    def _prepare_result_entry(
        self,
        record,
    ) -> definition.entity.solution.SolutionStorageData:
        return definition.entity.solution.SolutionStorageData(
            unique_key=record.unique_key,
            created_at=record.created_at,
        )
