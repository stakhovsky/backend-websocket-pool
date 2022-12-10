import typing

import kafka.admin
import kafka.errors


def ensure_topic(
    servers: typing.Sequence[str] = ("localhost:9093", ),
    user: str = "kafka",
    password: str = "kafka_password",
    topic_name: str = "topic",
    num_partitions: int = 1,
    replication_factor: int = 1,
    topic_retention_milliseconds: int = 60 * 60 * 1000,
):
    admin_client = kafka.admin.KafkaAdminClient(
        bootstrap_servers=servers,
        security_protocol="PLAINTEXT",
        sasl_mechanism="PLAIN",
        sasl_plain_username=user,
        sasl_plain_password=password,
    )

    try:
        admin_client.create_topics(
            new_topics=[
                kafka.admin.NewTopic(
                    name=topic_name,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor,
                    topic_configs={
                        "retention.ms": topic_retention_milliseconds,
                    },
                ),
            ],
            validate_only=False,
        )
    except kafka.errors.TopicAlreadyExistsError:
        print(f"[Kafka] Topic \"{topic_name}\" already exists.")
    else:
        print(f"[Kafka] Topic \"{topic_name}\" created.")
