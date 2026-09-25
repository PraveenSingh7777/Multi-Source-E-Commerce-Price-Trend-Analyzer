# data_pipeline.py
import os
import random
from datetime import datetime, timedelta
import pandas as pd
from rapidfuzz import fuzz, process

os.makedirs("data", exist_ok=True)

# 1. Canonical list of reference products
CANONICAL_PRODUCTS = [
    {"id": "PROD_001", "name": "Apple iPhone 15 128GB"},
    {"id": "PROD_002", "name": "Sony WH-1000XM5 Wireless Headphones"},
    {"id": "PROD_003", "name": "Samsung Galaxy S24 Ultra 256GB"},
    {"id": "PROD_004", "name": "Apple MacBook Air M2 8GB 256GB"},
]

# 2. Simulate messy listings across three stores
MOCK_LISTINGS = [
    # Store A (Amazon style)
    {"store": "Store_A", "raw_title": "Apple iPhone 15 (128 GB) - Black", "base_price": 79900},
    {"store": "Store_A", "raw_title": "Sony WH1000XM5 Noise Cancelling Over-Ear Headphones", "base_price": 29990},
    {"store": "Store_A", "raw_title": "Samsung Galaxy S24 Ultra 5G AI Smartphone 256GB", "base_price": 129999},
    {"store": "Store_A", "raw_title": "Apple 2022 MacBook Air Laptop with M2 chip: 13.6-inch, 8GB RAM, 256GB SSD", "base_price": 99900},
    # Store B (Flipkart style)
    {"store": "Store_B", "raw_title": "iPhone 15 (Black, 128 GB)", "base_price": 78999},
    {"store": "Store_B", "raw_title": "SONY WH-1000XM5 Bluetooth Headset (Black)", "base_price": 28490},
    {"store": "Store_B", "raw_title": "SAMSUNG Galaxy S24 Ultra 5G (Titanium Gray, 256 GB)", "base_price": 128500},
    {"store": "Store_B", "raw_title": "Apple MacBook Air Apple M2 - (8 GB/256 GB SSD/macOS)", "base_price": 98990},
    # Store C (Croma style)
    {"store": "Store_C", "raw_title": "Apple iPhone 15 128GB Blue", "base_price": 79500},
    {"store": "Store_C", "raw_title": "Sony WH-1000XM5 Over-Ear Active Noise Cancellation Headphones", "base_price": 29490},
    {"store": "Store_C", "raw_title": "Samsung S24 Ultra 5G 256GB ROM", "base_price": 129500},
    {"store": "Store_C", "raw_title": "MacBook Air M2 13.6 inch 8GB RAM 256GB Storage", "base_price": 99490},
]

def match_product(raw_title: str, threshold: int = 65) -> str:
    """Matches raw scraped titles to canonical products using Token Set Ratio."""
    choices = {prod["name"]: prod["id"] for prod in CANONICAL_PRODUCTS}
    match, score, _ = process.extractOne(
        raw_title, choices.keys(), scorer=fuzz.token_set_ratio
    )
    return choices[match] if score >= threshold else "UNKNOWN"

def generate_pricing_history(days: int = 30) -> pd.DataFrame:
    """Generates time-series pricing data with natural price variations."""
    records = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    for item in MOCK_LISTINGS:
        canonical_id = match_product(item["raw_title"])
        current_date = start_date
        current_price = item["base_price"]

        while current_date <= end_date:
            # Random price fluctuation between -4% and +3%
            variation = random.uniform(-0.04, 0.03)
            current_price = round(current_price * (1 + variation), 2)

            records.append({
                "timestamp": current_date.strftime("%Y-%m-%d"),
                "canonical_id": canonical_id,
                "store": item["store"],
                "raw_title": item["raw_title"],
                "price": current_price
            })
            current_date += timedelta(days=1)

    df = pd.DataFrame(records)
    df.to_csv("data/price_history.csv", index=False)
    return df

if __name__ == "__main__":
    df = generate_pricing_history()
    print(f"[+] Pipeline executed successfully: {len(df)} records generated and matched.")
