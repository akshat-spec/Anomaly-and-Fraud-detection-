"""Kafka consumer — reads `raw-transactions`, enriches, persists, and forwards.

Pipeline per message:
  1. Parse JSON from `raw-transactions`
  2. Run feature-engineering transforms
  3. Store computed features in Redis  (TTL 600 s)
  4. Persist the raw transaction in PostgreSQL
  5. Produce the enriched event to `enriched-transactions`

Malformed messages are routed to a `dead-letter-queue` topic.
"""

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from confluent_kafka import Consumer, KafkaError, KafkaException, Producer

from src.db.models import FraudAlert, RawTransaction
from src.db.session import get_session, init_db
from src.feature_store import redis_client
from src.features.engineer import engineer_features

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP", "fraud-consumer-group")
INPUT_TOPIC = "raw-transactions"
OUTPUT_TOPIC = "enriched-transactions"
DLQ_TOPIC = "dead-letter-queue"

# ─── Kafka helpers ─────────────────────────────────────────────


def build_consumer() -> Consumer:
    """Create a consumer with manual offset commits and rebalance logging."""
    conf = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "session.timeout.ms": 30000,
        "max.poll.interval.ms": 300000,
    }

    def on_assign(consumer, partitions):
        logger.info("Partitions assigned: %s", partitions)

    def on_revoke(consumer, partitions):
        logger.info("Partitions revoked: %s", partitions)
        consumer.commit(asynchronous=False)

    c = Consumer(conf)
    c.subscribe([INPUT_TOPIC], on_assign=on_assign, on_revoke=on_revoke)
    return c


def build_producer() -> Producer:
    """Lightweight producer for forwarding enriched events and DLQ."""
    return Producer({"bootstrap.servers": KAFKA_BOOTSTRAP, "client.id": "fraud-consumer-fwd"})


# ─── Processing logic ─────────────────────────────────────────


def parse_message(raw: bytes) -> Dict[str, Any]:
    """Deserialise and validate a raw-transaction JSON blob."""
    data = json.loads(raw)
    required = {"transaction_id", "timestamp", "amount", "user_id"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing fields: {missing}")
    return data


def transform_features(txn: Dict[str, Any]) -> pd.DataFrame:
    """Build a single-row DataFrame and run the feature-engineering pipeline."""
    v_cols = {f"V{i}": txn.get(f"v{i}", 0.0) for i in range(1, 29)}
    row = {"Time": txn["timestamp"], "Amount": txn["amount"], **v_cols}
    df = pd.DataFrame([row])
    # Add a dummy Class column (required by engineer_features) — will drop later
    df["Class"] = 0
    df = engineer_features(df)
    df = df.drop(columns=["Class"], errors="ignore")
    return df


async def persist_raw_transaction(txn: Dict[str, Any]) -> None:
    """Write the raw transaction to PostgreSQL."""
    v_data = {k: v for k, v in txn.items() if k.startswith("v")}
    record = RawTransaction(
        transaction_id=txn["transaction_id"],
        user_id=txn["user_id"],
        timestamp=datetime.fromtimestamp(txn["timestamp"], tz=timezone.utc),
        amount=txn["amount"],
        features_json=json.dumps(v_data),
    )
    async with get_session() as session:
        session.add(record)


async def process_message(
    txn: Dict[str, Any],
    fwd_producer: Producer,
) -> None:
    """Full pipeline for a single valid transaction."""
    user_id = txn["user_id"]

    # 1. Feature engineering
    features_df = transform_features(txn)
    features_dict = features_df.iloc[0].to_dict()
    # Convert numpy types to native Python for JSON serialisation
    features_dict = {k: float(v) if isinstance(v, (np.floating, float)) else v for k, v in features_dict.items()}

    # 2. Cache features in Redis
    await redis_client.set_user_features(user_id, features_dict, ttl=600)

    # 3. Persist raw transaction in Postgres
    await persist_raw_transaction(txn)

    # 4. Forward enriched event
    enriched = {**txn, "features": features_dict}
    fwd_producer.produce(
        OUTPUT_TOPIC,
        key=user_id,
        value=json.dumps(enriched, default=str),
    )
    fwd_producer.poll(0)

    logger.debug("Processed txn %s for user %s", txn["transaction_id"], user_id)


# ─── Main loop ─────────────────────────────────────────────────

_running = True


def _sig_handler(sig, frame):
    global _running
    logger.info("Shutdown signal received.")
    _running = False


async def consume_loop() -> None:
    """Continuously poll Kafka, process, and commit offsets."""
    global _running
    signal.signal(signal.SIGINT, _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)

    await init_db()

    consumer = build_consumer()
    fwd_producer = build_producer()
    dlq_producer = build_producer()

    logger.info("Consumer started — listening on '%s'.", INPUT_TOPIC)

    try:
        while _running:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug("End of partition reached %s [%d]", msg.topic(), msg.partition())
                else:
                    raise KafkaException(msg.error())
                continue

            try:
                txn = parse_message(msg.value())
                await process_message(txn, fwd_producer)
            except (json.JSONDecodeError, ValueError, KeyError) as exc:
                logger.warning("Malformed message → DLQ: %s", exc)
                dlq_producer.produce(
                    DLQ_TOPIC,
                    value=msg.value(),
                    headers=[("error", str(exc).encode())],
                )
                dlq_producer.poll(0)

            # Commit after each successfully-handled message
            consumer.commit(asynchronous=False)

    finally:
        consumer.close()
        fwd_producer.flush(timeout=10)
        dlq_producer.flush(timeout=10)
        await redis_client.close()
        logger.info("Consumer shut down cleanly.")


def main() -> None:
    asyncio.run(consume_loop())


if __name__ == "__main__":
    main()
