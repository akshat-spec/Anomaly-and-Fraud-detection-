"""FastAPI inference server app."""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.middleware.latency import LatencyLoggingMiddleware
from src.api.routes import predict
from src.feature_store import redis_client

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def relog_connection(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fraud_api.main")

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models on startup and tear down connections on shutdown."""
    logger.info("Initializing FastAPI Fraud Inference server...")
    
    try:
        # Load models globally into state
        from src.models.ensemble import FraudEnsemble
        app.state.model = FraudEnsemble()
        logger.info("Ensemble model wrapper successfully loaded.")
    except Exception as e:
        logger.error("Failed to load ML models. API will return 503 on model requests. Error: %s", e)
        app.state.model = None

    yield
    
    logger.info("Tearing down database and Redis connections...")
    await redis_client.close()


app = FastAPI(
    title="Real-Time Fraud Detection Inference Server",
    version="1.0.0",
    description="FastAPI REST service predicting real-time transaction fraudulence natively.",
    lifespan=lifespan
)

# Middlewares and Prometheus Config
app.add_middleware(LatencyLoggingMiddleware)

# Expose generic p50, p95, p99 endpoint latency timings automatically via prometheus-fastapi-instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.websocket("/ws/transactions")
async def websocket_endpoint(websocket: WebSocket):
    await manager.relog_connection(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.include_router(predict.router)
app.state.manager = manager


@app.get("/health")
async def health_check():
    """Verify inference readiness gracefully."""
    uptime_sec = time.time() - START_TIME
    
    redis_status = "ok"
    try:
        r = await redis_client.get_redis()
        await r.ping()
    except Exception as e:
        logger.error("Healthcheck — Redis offline: %s", e)
        redis_status = "unreachable"

    model_loaded = getattr(app.state, "model", None) is not None
    if not model_loaded:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "ML models failed to load"}
        )
        
    return {
        "status": "healthy",
        "uptime_seconds": round(uptime_sec, 2),
        "model_version": "fraud_ensemble_v1",
        "redis_status": redis_status
    }
