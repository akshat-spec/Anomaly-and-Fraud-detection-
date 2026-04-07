"""SQLAlchemy async models for the fraud detection pipeline."""

import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


class RawTransaction(Base):
    """Stores every raw transaction ingested from Kafka."""

    __tablename__ = "raw_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Float, nullable=False)
    # V1–V28 stored as a JSON blob for flexibility
    features_json = Column(Text, nullable=False)
    ingested_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow,
    )


class FraudAlert(Base):
    """Persists every fraud decision produced by the ensemble."""

    __tablename__ = "fraud_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(
        String(64), nullable=False, index=True
    )
    user_id = Column(String(64), nullable=False, index=True)
    is_fraud = Column(Boolean, nullable=False)
    xgb_score = Column(Float, nullable=False)
    iso_score = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow,
    )
