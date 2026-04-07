"""Kafka producer — replays the Kaggle credit-card dataset to `raw-transactions`.

Usage:
    python -m src.streaming.producer --tps 100
"""

import argparse
import json
import logging
import os
import time
import uuid
from pathlib import Path

import pandas as pd
from confluent_kafka import Producer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "creditcard.csv"

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = "raw-transactions"


def delivery_report(err, msg) -> None:
    """Callback invoked once per message to indicate delivery result."""
    if err is not None:
        logger.error("Message delivery failed: %s", err)
    else:
        logger.debug("Delivered to %s [%d] @ offset %d", msg.topic(), msg.partition(), msg.offset())


def build_producer() -> Producer:
    """Create a confluent-kafka Producer with sensible defaults."""
    conf = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "client.id": "fraud-producer",
        "acks": "all",
        "retries": 3,
        "linger.ms": 5,
        "batch.num.messages": 500,
    }
    return Producer(conf)


def run(tps: int = 100) -> None:
    """Read the CSV row by row and produce JSON messages at *tps* transactions/sec."""
    if not RAW_CSV.exists():
        raise FileNotFoundError(
            f"Dataset not found at {RAW_CSV}. Run `python -m src.data.loader` first."
        )

    producer = build_producer()
    df = pd.read_csv(RAW_CSV)
    logger.info("Loaded %d rows. Producing at %d TPS to topic '%s'.", len(df), tps, TOPIC)

    interval = 1.0 / tps
    v_cols = [c for c in df.columns if c.startswith("V")]

    for idx, row in df.iterrows():
        txn = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "amount": float(row["Amount"]),
            "user_id": f"user_{int(row['Time']) % 1000:04d}",  # synthetic user id
        }
        # attach V1–V28
        for vc in v_cols:
            txn[vc.lower()] = float(row[vc])

        producer.produce(
            TOPIC,
            key=txn["user_id"],
            value=json.dumps(txn),
            callback=delivery_report,
        )

        # keep the in-memory buffer moving
        if idx % 1000 == 0:
            producer.poll(0)
            logger.info("Produced %d / %d messages", idx, len(df))

        time.sleep(interval)

    producer.flush(timeout=30)
    logger.info("All %d messages produced.", len(df))


def main() -> None:
    parser = argparse.ArgumentParser(description="Fraud-detection Kafka producer")
    parser.add_argument("--tps", type=int, default=100, help="Transactions per second")
    args = parser.parse_args()
    run(tps=args.tps)


if __name__ == "__main__":
    main()
