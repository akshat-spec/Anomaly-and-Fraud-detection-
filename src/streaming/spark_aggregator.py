"""PySpark Structured Streaming aggregator.

Reads from Kafka `raw-transactions`, computes watermarked window
aggregations (1 min, 5 min, 30 min) per user_id, and writes
results to Redis as `user:{user_id}:window_features`.

Usage:
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
                 src/streaming/spark_aggregator.py
"""

import json
import logging
import os

import redis
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    from_json,
    max as spark_max,
    mean as spark_mean,
    stddev as spark_stddev,
    window,
)
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Schema that matches the producer output
TXN_SCHEMA = StructType(
    [
        StructField("transaction_id", StringType(), False),
        StructField("timestamp", DoubleType(), False),  # epoch seconds
        StructField("amount", DoubleType(), False),
        StructField("user_id", StringType(), False),
    ]
)


def write_window_to_redis(batch_df, batch_id: int) -> None:
    """foreachBatch sink — push aggregated features per user to Redis."""
    rows = batch_df.collect()
    if not rows:
        return

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    for row in rows:
        user_id = row["user_id"]
        features = {
            "window_start": str(row["window"]["start"]),
            "window_end": str(row["window"]["end"]),
            "txn_count": int(row["txn_count"]),
            "mean_amount": float(row["mean_amount"]) if row["mean_amount"] else 0.0,
            "std_amount": float(row["std_amount"]) if row["std_amount"] else 0.0,
            "max_amount": float(row["max_amount"]) if row["max_amount"] else 0.0,
        }
        key = f"user:{user_id}:window_features"
        r.set(key, json.dumps(features), ex=1800)
    r.close()
    logger.info("Batch %d: wrote %d window features to Redis.", batch_id, len(rows))


def start_query(spark: SparkSession, window_duration: str, query_name: str):
    """Create a single streaming query for the given window size."""
    raw_stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", "raw-transactions")
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )

    parsed = (
        raw_stream.selectExpr("CAST(value AS STRING) as json_str")
        .select(from_json(col("json_str"), TXN_SCHEMA).alias("data"))
        .select(
            col("data.transaction_id"),
            col("data.user_id"),
            col("data.amount"),
            col("data.timestamp").cast(TimestampType()).alias("event_time"),
        )
    )

    windowed = (
        parsed.withWatermark("event_time", "1 minute")
        .groupBy(col("user_id"), window(col("event_time"), window_duration))
        .agg(
            count("*").alias("txn_count"),
            spark_mean("amount").alias("mean_amount"),
            spark_stddev("amount").alias("std_amount"),
            spark_max("amount").alias("max_amount"),
        )
    )

    query = (
        windowed.writeStream
        .queryName(query_name)
        .outputMode("update")
        .foreachBatch(write_window_to_redis)
        .option("checkpointLocation", f"/tmp/spark-checkpoints/{query_name}")
        .trigger(processingTime="10 seconds")
        .start()
    )
    return query


def main() -> None:
    spark = (
        SparkSession.builder.appName("FraudWindowAggregator")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    logger.info("Starting Spark window aggregation queries…")
    q1 = start_query(spark, "1 minute", "window_1min")
    q5 = start_query(spark, "5 minutes", "window_5min")
    q30 = start_query(spark, "30 minutes", "window_30min")

    # block until any query terminates (or manual kill)
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
