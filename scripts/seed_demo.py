import time
import random
import requests
import json

API_URL = "http://localhost:8000/api/v1/predict"

def generate_transaction(is_fraud: bool):
    """
    Generate a synthetic transaction payload.
    Features might correspond to standard ML inputs like Amount, Location, Time, etc.
    """
    if is_fraud:
        # High amount, unusual location, high velocity
        return {
            "transaction_id": f"TX_{random.randint(100000, 999999)}_F",
            "amount": round(random.uniform(5000.0, 25000.0), 2),
            "merchant_category": random.choice(["jewelry", "electronics", "crypto"]),
            "is_foreign": True,
            "time_since_last_txn_sec": random.randint(1, 5),
            "user_age": random.randint(18, 80),
            "device_trust_score": round(random.uniform(0.0, 0.3), 2)
        }
    else:
        # Normal amount, normal parameters
        return {
            "transaction_id": f"TX_{random.randint(100000, 999999)}_N",
            "amount": round(random.uniform(5.0, 500.0), 2),
            "merchant_category": random.choice(["groceries", "restaurant", "transportation"]),
            "is_foreign": False,
            "time_since_last_txn_sec": random.randint(3600, 86400),
            "user_age": random.randint(18, 80),
            "device_trust_score": round(random.uniform(0.7, 1.0), 2)
        }

def seed_data(total=1000, frauds=50):
    print(f"Starting to seed {total} transactions ({frauds} fraudulent) to {API_URL}...")
    
    # Create list of transactions
    transactions = [generate_transaction(is_fraud=True) for _ in range(frauds)]
    transactions += [generate_transaction(is_fraud=False) for _ in range(total - frauds)]
    
    # Shuffle so frauds are interspersed
    random.shuffle(transactions)
    
    success_count = 0
    error_count = 0
    
    for i, txn in enumerate(transactions):
        try:
            # Send to API
            response = requests.post(API_URL, json=txn, timeout=5)
            if response.status_code == 200:
                success_count += 1
            else:
                error_count += 1
            
            # Print progress every 100 transactions
            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1}/{total} transactions. Success: {success_count}, Errors: {error_count}")
            
            # Small delay to simulate real-time stream
            time.sleep(0.05)
            
        except requests.exceptions.RequestException as e:
            error_count += 1
            print(f"Request failed: {e}")
            time.sleep(1) # wait a bit before retrying next

    print(f"Seeding completed! Total successful: {success_count}. Total errors: {error_count}.")

if __name__ == "__main__":
    seed_data()
