import asyncio
import typing

import aiormq


def create_exchange_and_queues(
    address: str = "rabbitmq:5672",
    user: str = "rabbitmq",
    password: str = "rabbitmq_password",
    exchange: str = "",
    queues: typing.Sequence[str] = ("queue", ),
):
    async def _run():
        connection = await aiormq.connect(
            f"amqp://{user}:{password}@{address}//",
        )
        channel = await connection.channel()

        await channel.exchange_declare(
            exchange=exchange,
            exchange_type="fanout",
            durable=True,
        )
        print(f"[RabbitMQ] Exchange declared \"{exchange}\"")

        for queue in queues:
            await channel.queue_declare(
                queue=queue,
                durable=True,
            )
            await channel.queue_bind(
                queue=queue,
                exchange=exchange,
            )
            print(f"[RabbitMQ] Queue declared \"{queue}\"")

    asyncio.run(_run())

