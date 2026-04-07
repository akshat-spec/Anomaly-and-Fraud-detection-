# Streaming Pipeline — Setup & Usage

## Prerequisites

| Tool | Version |
|------|---------|
| Docker & Docker Compose | v2+ |
| Python | 3.11 |
| Apache Spark (for aggregator) | 3.5.x |

---

## 1. Start Infrastructure

```bash
# Launch Kafka, Zookeeper, Kafdrop, Redis, PostgreSQL
docker compose -f docker-compose.infra.yml up -d

# Verify all services are healthy
docker compose -f docker-compose.infra.yml ps
```

Access **Kafdrop UI** at [http://localhost:9000](http://localhost:9000) to inspect topics.

---

## 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials — especially KAGGLE_USERNAME / KAGGLE_KEY
```

---

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Download Dataset (if not already done)

```bash
python -m src.data.loader
```

---

## 5. Run the Producer

The producer replays the CSV dataset to `raw-transactions` at a configurable rate.

```bash
# Default: 100 TPS
python -m src.streaming.producer

# Custom rate
python -m src.streaming.producer --tps 500
```

---

## 6. Run the Consumer

Open a **separate terminal**:

```bash
python -m src.streaming.consumer
```

The consumer will:
1. Read from `raw-transactions`
2. Run feature engineering
3. Cache features → **Redis** (`user:{id}:features`, TTL 600 s)
4. Persist raw record → **PostgreSQL** (`raw_transactions` table)
5. Forward enriched event → `enriched-transactions`

Malformed messages are routed to the `dead-letter-queue` topic.

---

## 7. Run the Spark Aggregator (optional — requires Spark)

```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  src/streaming/spark_aggregator.py
```

This creates 1-min, 5-min, and 30-min sliding-window aggregations per user and writes them to Redis (`user:{id}:window_features`).

---

## 8. Verify Data Flow

```bash
# Check Redis features
redis-cli GET "user:user_0042:features"

# Check Postgres
docker exec -it fraud-postgres psql -U fraud -d fraud_detection \
  -c "SELECT count(*) FROM raw_transactions;"

# Check Kafdrop for topic lag
open http://localhost:9000
```

---

## 9. Tear Down

```bash
docker compose -f docker-compose.infra.yml down -v
```
