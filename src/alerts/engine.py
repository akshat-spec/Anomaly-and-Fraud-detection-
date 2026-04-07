"""Async Alert Engine executing logical webhooks asynchronously listening selectively against Kafka signals."""

import asyncio
import json
import logging
import os
from typing import Dict, Any

import httpx
from confluent_kafka import Consumer, KafkaError, KafkaException

from src.db.models import FraudAlert
from src.db.session import get_session, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fraud_alert_engine")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
ALERTS_TOPIC = "fraud-alerts"
GROUP_ID = os.getenv("KAFKA_ALERTS_GROUP", "fraud-alerts-group")
WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "http://localhost:8080/alerts")

MAX_RETRIES = 3


def build_consumer() -> Consumer:
    """Mount generic properties required inside alerting Consumer definitions."""
    conf = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
    c = Consumer(conf)
    c.subscribe([ALERTS_TOPIC])
    return c


async def send_webhook_with_retry(payload: Dict[str, Any]) -> bool:
    """Implement graceful retry bounds sequentially escalating dynamically."""
    async with httpx.AsyncClient() as client:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Transmit logical webhook generically containing internal dict
                response = await client.post(WEBHOOK_URL, json=payload, timeout=5.0)
                if response.status_code in (200, 201, 202, 204):
                    logger.info("Webhook successfully dispatched for Transaction %s", payload.get("transaction_id"))
                    return True
                else:
                    logger.warning("Webhook explicitly answered dynamically code=%s", response.status_code)
            except httpx.RequestError as exc:
                logger.warning("Webhook communication sequentially halted: %s (Attempt %d/%d)", exc, attempt, MAX_RETRIES)
            
            # Context switch allowing asynchronous bounds (Exponential backoff)
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 ** attempt)
                
    logger.error("Failed to definitively route webhook after %d attempts", MAX_RETRIES)
    return False


async def run_alert_engine():
    """Continuously execute message extractions sequentially triggering alerts properly."""
    logger.info("Starting Async Alert Engine systematically focusing on %s...", ALERTS_TOPIC)
    await init_db()
    
    c = build_consumer()
    try:
        while True:
            # Poll async gracefully limiting execution blocks properly
            msg = await asyncio.to_thread(c.poll, 1.0)
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())

            try:
                payload = json.loads(msg.value())
                success = await send_webhook_with_retry(payload)
                if success:
                    # Validate DB logic or explicitly flag if required logically
                    pass
            except json.JSONDecodeError:
                logger.error("Alert structurally malformed securely ignoring seamlessly.")
            except Exception as e:
                logger.exception("Engine natively encountered exception parameters: %s", e)
                
            # Preserving systematic progression explicitly bounding delivery offset records
            c.commit(asynchronous=False)
            
    except KeyboardInterrupt:
        logger.info("Termination cleanly requested exiting explicitly...")
    finally:
        c.close()


if __name__ == "__main__":
    asyncio.run(run_alert_engine())
