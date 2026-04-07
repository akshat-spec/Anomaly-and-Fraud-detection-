"""Demo Generator aggressively pushing synthetic anomalies into streaming inference interfaces securely capturing states directly."""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seed_demo")

API_URL = "http://localhost:8000/api/v1/predict"
TOTAL_TRANSACTIONS = 1000
FRAUD_COUNT = 50


def generate_transaction(is_fraud: bool) -> dict:
    """Mock organic vectors strictly mapping dimensional constraints."""
    base_txn = {
        "transaction_id": f"tx_{int(time.time() * 1000)}_{random.randint(100, 999)}",
        "user_id": f"usr_{random.randint(1, 200)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "amount": random.uniform(5.0, 150.0) if not is_fraud else random.uniform(5000.0, 25000.0),
    }

    # Injecting synthetic standard dimensions organically generating random mapping values securely
    for i in range(1, 29):
        val = random.uniform(-2.0, 2.0)
        
        if is_fraud:
            # Extreme mappings intentionally breaking patterns cleanly triggering Isolation Forest explicitly  
            if i in (4, 11, 14, 18):
                val += random.uniform(5.0, 10.0) 
            if i in (3, 10, 12, 16):
                val -= random.uniform(5.0, 10.0) 
                
        base_txn[f"v{i}"] = round(val, 4)

    return base_txn


async def seed_dashboard():
    """Concurrently pushes loads efficiently mimicking web traffic smoothly natively."""
    logger.info("Initializing synthetic loads orchestrating successfully over REST payloads.")
    
    transactions = [generate_transaction(is_fraud=False) for _ in range(TOTAL_TRANSACTIONS - FRAUD_COUNT)]
    fraud_transactions = [generate_transaction(is_fraud=True) for _ in range(FRAUD_COUNT)]
    
    all_transactions = transactions + fraud_transactions
    random.shuffle(all_transactions)
    
    async with httpx.AsyncClient() as client:
        for idx, txn in enumerate(all_transactions):
            try:
                res = await client.post(API_URL, json=txn)
                if res.status_code == 200:
                    status = "🚨 FRAUD" if res.json().get("fraud") else "✅ NORMAL"
                    logger.info("[%d/%d] ID: %s | Result: %s", idx + 1, TOTAL_TRANSACTIONS, txn["transaction_id"], status)
                else:
                    logger.warning("Unexpected Server Code strictly breaking logic bounds natively: %s", res.status_code)
            except Exception as e:
                logger.error("Connection effectively blocked seamlessly triggering logic halts: %s", e)
                
            # Simulate real-world intervals spacing uniformly aggressively ensuring clean graph processing
            await asyncio.sleep(random.uniform(0.1, 0.4))
            
    logger.info("Database strictly flooded seamlessly testing logic arrays completed natively.")


if __name__ == "__main__":
    asyncio.run(seed_dashboard())
