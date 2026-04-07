"""Predict API route resolving ML decisions against live context parameters."""

import json
import logging
import os
import time

import pandas as pd
from confluent_kafka import Producer
from fastapi import APIRouter, HTTPException, Request

from src.api.schemas import FraudResponse, TransactionRequest
from src.db.models import FraudAlert
from src.db.session import get_session
from src.feature_store import redis_client
from src.features.engineer import engineer_features

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Prediction"])

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
ALERTS_TOPIC = "fraud-alerts"

_producer = None


def get_kafka_producer() -> Producer:
    """Lazy init Kafka producer for publishing alerts asynchronously."""
    global _producer
    if _producer is None:
        _producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP, "client.id": "api-alerts-publisher"})
    return _producer


@router.post("/predict", response_model=FraudResponse)
async def predict_fraud(txn: TransactionRequest, request: Request):
    """
    Evaluate a transaction against the ensemble models.
    Merges live request metadata symmetrically alongside dynamically cached
    point-in-time statistics stored efficiently within Redis.
    """
    model_wrapper = getattr(request.app.state, "model", None)
    if model_wrapper is None:
        raise HTTPException(status_code=503, detail="Inference models offline.")

    # Calculate precise process start leveraging middleware injection when accessible
    start_time = getattr(request.state, "start_time", time.perf_counter())

    r = await redis_client.get_redis()
    cache_key = f"prediction:{txn.transaction_id}"
    
    # 1. Idempotency Check
    cached_res = await r.get(cache_key)
    if cached_res:
        res_dict = json.loads(cached_res)
        res_dict["cached"] = True
        res_dict["latency_ms"] = (time.perf_counter() - start_time) * 1000.0
        return FraudResponse(**res_dict)

    # 2. Redis Feature Fetch
    user_features = await redis_client.get_user_features(txn.user_id)
    
    # 3. Parameter Merging & Vectorisation
    base_features = {
        "Time": txn.timestamp.timestamp(),
        "Amount": txn.amount,
    }
    # Attach dynamic vectorized parameters seamlessly
    for i in range(1, 29):
        k_lower = f"v{i}"
        k_upper = f"V{i}"
        base_features[k_upper] = getattr(txn, k_lower, 0.0)

    # Override standard dimensions smoothly matching latest cached derivations natively  
    base_features.update(user_features)

    df_req = pd.DataFrame([base_features])
    
    # Feature eng requires "Class" present nominally implicitly
    if "Class" not in df_req.columns:
        df_req["Class"] = 0
        
    try:
        df_eng = engineer_features(df_req)
        df_eng = df_eng.drop(columns=["Class"], errors="ignore")
    except Exception as e:
        logger.error("Feature mapping explicitly halted: %s", e)
        raise HTTPException(status_code=500, detail="Feature generation constraints prevented execution.")

    # 4. Model Decision Emulation
    try:
        prediction_result = model_wrapper.predict(df_eng)
    except Exception as e:
        logger.error("XGBoost/IsolationForest processing abruptly stopped: %s", e)
        raise HTTPException(status_code=500, detail="Matrix evaluation logic strictly rejected execution.")

    res = FraudResponse(
        transaction_id=txn.transaction_id,
        fraud=prediction_result["fraud"],
        xgb_score=prediction_result["xgb_score"],
        iso_score=prediction_result["iso_score"],
        confidence=prediction_result["confidence"],
        latency_ms=0.0,
        cached=False
    )

    # 5. Database Commit
    try:
        alert_db = FraudAlert(
            transaction_id=txn.transaction_id,
            user_id=txn.user_id,
            is_fraud=res.fraud,
            xgb_score=res.xgb_score,
            iso_score=res.iso_score,
            confidence=res.confidence
        )
        async with get_session() as session:
            session.add(alert_db)
    except Exception as e:
        # Strictly catch SQL errors without failing request delivery logic
        logger.error("Postgres execution prevented row preservation natively: %s", e)

    # 6. Messaging Relay (Fire-and-forget strictly on fraud)
    if res.fraud:
        try:
            p = get_kafka_producer()
            p.produce(ALERTS_TOPIC, key=txn.user_id, value=res.model_dump_json())
            p.poll(0)
        except Exception as e:
            logger.error("Kafka delivery explicitly halted sending downstream alerts: %s", e)

    # 7. Post-Execution Result Caching
    await r.set(cache_key, res.model_dump_json(), ex=300)

    res.latency_ms = (time.perf_counter() - start_time) * 1000.0
    return res
