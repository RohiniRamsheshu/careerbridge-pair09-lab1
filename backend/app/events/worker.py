"""Independently runnable Kafka workers for the local Lab 2 stack."""

import argparse
import logging
import os
import time

from backend.app.events.consumer import run_kafka_consumer
from backend.app.events.contracts import LOGICAL_TOPICS, topic_name
from backend.app.events.outbox import publish_pending_once, record_processed_event
from backend.app.events.producer import KafkaEventProducer, publish_event
from backend.app import config
from backend.app.memory_consolidation import consolidate_student
from backend.app.mongo_repository import MongoRepository

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("careerbridge.worker")


def run_outbox_worker(interval=1.0):
    while True:
        publish_pending_once()
        time.sleep(interval)


def run_event_worker(topics, group_id):
    producer = KafkaEventProducer()
    repository = MongoRepository() if config.MONGO_URI else None

    def handle(envelope):
        if not record_processed_event(envelope):
            return
        if envelope.topic == topic_name("memory.updated"):
            publish_event("memory.consolidate", envelope.aggregate_id, "student_memory", {"student_user_id": envelope.aggregate_id})
        elif envelope.topic == topic_name("memory.consolidate") and repository is not None:
            consolidate_student(repository, envelope.aggregate_id)

    run_kafka_consumer(
        [topic_name(topic) for topic in topics],
        group_id,
        handle,
        lambda envelope, error: producer.publish_dlq(envelope, error),
        raw_dlq_publisher=lambda topic, raw, error: producer.publish_raw_dlq(topic, raw, error),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("outbox", "consumer"), default="consumer")
    parser.add_argument("--group", default="p09-careerbridge-workers")
    args = parser.parse_args()
    if args.mode == "outbox":
        run_outbox_worker()
    else:
        run_event_worker(LOGICAL_TOPICS, args.group)


if __name__ == "__main__":
    main()
