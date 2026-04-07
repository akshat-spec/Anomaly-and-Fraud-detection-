"""Pydantic schemas for the FastAPI inference server."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class TransactionRequest(BaseModel):
    """Incoming payload for a fraud prediction request."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    user_id: str = Field(..., min_length=1, description="User identifier")
    timestamp: datetime = Field(..., description="ISO8601 transaction timestamp")
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")

    # V1 through V28 features
    v1: Optional[float] = 0.0
    v2: Optional[float] = 0.0
    v3: Optional[float] = 0.0
    v4: Optional[float] = 0.0
    v5: Optional[float] = 0.0
    v6: Optional[float] = 0.0
    v7: Optional[float] = 0.0
    v8: Optional[float] = 0.0
    v9: Optional[float] = 0.0
    v10: Optional[float] = 0.0
    v11: Optional[float] = 0.0
    v12: Optional[float] = 0.0
    v13: Optional[float] = 0.0
    v14: Optional[float] = 0.0
    v15: Optional[float] = 0.0
    v16: Optional[float] = 0.0
    v17: Optional[float] = 0.0
    v18: Optional[float] = 0.0
    v19: Optional[float] = 0.0
    v20: Optional[float] = 0.0
    v21: Optional[float] = 0.0
    v22: Optional[float] = 0.0
    v23: Optional[float] = 0.0
    v24: Optional[float] = 0.0
    v25: Optional[float] = 0.0
    v26: Optional[float] = 0.0
    v27: Optional[float] = 0.0
    v28: Optional[float] = 0.0

    @field_validator("user_id")
    def user_id_must_not_be_empty(cls, v: str, info: ValidationInfo) -> str:
        if not v.strip():
            raise ValueError("user_id cannot be blank")
        return v


class FraudResponse(BaseModel):
    """Output payload representing the fraud decision."""

    transaction_id: str
    fraud: bool
    xgb_score: float
    iso_score: int
    confidence: float
    latency_ms: float
    cached: bool = False
