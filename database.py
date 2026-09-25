# database.py
import duckdb
import pandas as pd

DB_FILE = "data/ecommerce.duckdb"

def init_db():
    """Initializes DuckDB and loads matched CSV records."""
    con = duckdb.connect(DB_FILE)
    con.execute("""
        CREATE TABLE IF NOT EXISTS price_feed AS 
        SELECT * FROM read_csv_auto('data/price_history.csv');
    """)
    con.close()

def get_product_trend(canonical_id: str) -> pd.DataFrame:
    """Fetches price history and 7-day rolling average per store."""
    con = duckdb.connect(DB_FILE)
    query = """
        SELECT 
            timestamp,
            store,
            price,
            AVG(price) OVER (
                PARTITION BY store, canonical_id 
                ORDER BY timestamp 
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) AS rolling_avg_7d
        FROM price_feed
        WHERE canonical_id = ?
        ORDER BY timestamp ASC;
    """
    df = con.execute(query, [canonical_id]).fetchdf()
    con.close()
    return df

def get_deal_summary(canonical_id: str) -> dict:
    """Calculates lowest historic price, best current store, and potential savings."""
    con = duckdb.connect(DB_FILE)
    query = """
        WITH latest_date AS (
            SELECT MAX(timestamp) as max_date FROM price_feed
        ),
        current_prices AS (
            SELECT p.store, p.price
            FROM price_feed p, latest_date d
            WHERE p.canonical_id = ? AND p.timestamp = d.max_date
        ),
        historic_stats AS (
            SELECT 
                MIN(price) AS all_time_low,
                MAX(price) AS all_time_high,
                AVG(price) AS historical_avg
            FROM price_feed
            WHERE canonical_id = ?
        )
        SELECT 
            c.store AS best_current_store,
            c.price AS current_best_price,
            h.all_time_low,
            h.all_time_high,
            h.historical_avg
        FROM current_prices c, historic_stats h
        ORDER BY c.price ASC
        LIMIT 1;
    """
    res = con.execute(query, [canonical_id, canonical_id]).fetchone()
    con.close()
    
    if not res:
        return {}
    return {
        "best_store": res[0],
        "current_price": res[1],
        "all_time_low": res[2],
        "all_time_high": res[3],
        "avg_price": round(res[4], 2)
    }

if __name__ == "__main__":
    init_db()
    print("[+] DuckDB initialized and data ingested.")
