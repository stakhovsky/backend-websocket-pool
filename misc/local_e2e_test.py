import asyncio
import random

import orjson
import simple_dataclass_settings
import websockets

import libs.logger


@simple_dataclass_settings.settings
class _Log:
    name: str = "local-e2e-test"
    level: str = "INFO"
    root_level: str = "ERROR"


@simple_dataclass_settings.settings
class Settings:
    log: _Log


def _get_worker_registration_data() -> dict:
    return {
        "ip": "127.0.0.1",
        "address": "127.0.0.1",
        "hardware": "Test worker",
        "hardware_id": "test-worker",
        "caption": "E2E_TEST",
    }


def _get_job_input(
    proof_target: int = None,
    block_height: int = None,
) -> dict:
    if proof_target is None:
        proof_target = random.randint(1000, 10000)
    if block_height is None:
        block_height = random.randint(1, 100)

    return {
        "type": "job",
        "epoch_challenge": {
            "epoch_number": 123,
            "epoch_block_hash": "abc",
            "degree": 8191,
        },
        "proof_target": proof_target,
        "block_height": block_height,
    }


def _get_solution_input(
    task_id: str,
    solution_target: int = None,
    nonce: int = None,
) -> dict:
    if solution_target is None:
        solution_target = random.randint(1000, 10000)
    if nonce is None:
        nonce = random.randint(1, 100)

    return {
        "type": "solution",
        "task_id": task_id,
        "solution": {
            "partial_solution": {
                "address": "def",
                "nonce": nonce,
                "commitment": "ghi",
            },
            "proof.w": {
                "x": "123",
                "y": "456",
                "infinity": False,
            },
        },
        "solution_target": solution_target,
    }


async def main(
    cfg: Settings,
) -> None:
    logger = libs.logger.get(
        name=cfg.log.name,
        level=cfg.log.level,
    )

    try:
        logger.info("Starting tests")

        async with websockets.connect(f"ws://localhost:8001") as node:
            async with websockets.connect(f"ws://localhost:8002") as worker:
                logger.info("Registering worker and waiting for registration")
                await worker.send(orjson.dumps(_get_worker_registration_data()))
                await asyncio.sleep(1.5)
                logger.info("Message sent")

                logger.info("Sending message to node server")
                job_input = _get_job_input()
                await node.send(orjson.dumps(job_input))
                logger.info("Message sent")

                logger.info("Waiting message from worker server")
                worker_task = orjson.loads(await asyncio.wait_for(worker.recv(), 1.5))
                logger.info("Message received, checking content")
                assert len(worker_task.keys()) == 2
                assert "task_id" in worker_task
                assert worker_task["epoch_challenge"] == job_input["epoch_challenge"]
                logger.info("Message checked")

                logger.info("Sending solution to worker server")
                solution_input = _get_solution_input(
                    task_id=worker_task["task_id"],
                    solution_target=job_input["proof_target"],
                )
                await worker.send(orjson.dumps(solution_input))
                logger.info("Message sent")

                logger.info("Waiting message from node server")
                solution_output = orjson.loads(await asyncio.wait_for(node.recv(), 1.5))
                logger.info("Message received, checking content")
                assert solution_output == solution_input["solution"]
                logger.info("Message checked")
    except Exception:
        logger.info("Tests failed")
        raise
    else:
        logger.info("Tests done")


if __name__ == "__main__":
    simple_dataclass_settings.read_envfile('./.env.local_e2e_test')

    settings = simple_dataclass_settings.populate(Settings)
    libs.logger.configure(
        level=settings.log.root_level,
    )

    asyncio.run(main(
        cfg=settings,
    ))
