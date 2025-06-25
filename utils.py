import pandas as pd
import json
from date_utils import parse_timestamp
from collections import defaultdict
import sqlite3
from config import DATABASE_PATH
from datetime import datetime

def load_transaction_data(csv_path):
    return pd.read_csv(csv_path)

def clean_and_enrich_transactions(df):
    processed_timestamps = []
    quality_flags = []

    for _, row in df.iterrows():
        flags = []

        timestamp = str(row.get("timestamp", "")).strip()
        timezone = str(row.get("timezone", "")).strip()

        parsed_dt = parse_timestamp(timestamp, timezone)
        if parsed_dt is None:
            flags.append("invalid_date_format")

        if timezone in ("", "nan", "NaN"):
            flags.append("missing_timezone")

        processed_timestamps.append(parsed_dt)
        quality_flags.append(flags)

    df["processed_timestamp"] = processed_timestamps

    # 🔁 Detect out-of-order rows
    out_of_order_idxs = detect_out_of_order(df)

    # 🔁 Add flags as JSON with combined logic
    final_flags = []
    for idx, flags in enumerate(quality_flags):
        if idx in out_of_order_idxs:
            flags.append("out_of_order")
        final_flags.append(json.dumps({"issues": flags} if flags else {}))

    df["data_quality_flags"] = final_flags
    return df


def detect_near_duplicates(df, threshold_seconds=10):
    """
    Detect near-duplicates based on:
    - Same customer_id
    - Same amount
    - Same status & category
    - Timestamps within `threshold_seconds`
    """
    duplicates = set()
    df_sorted = df.sort_values(by="processed_timestamp")

    for i in range(1, len(df_sorted)):
        prev = df_sorted.iloc[i - 1]
        curr = df_sorted.iloc[i]

        if pd.isnull(prev["processed_timestamp"]) or pd.isnull(curr["processed_timestamp"]):
            continue

        same_fields = (
            prev["customer_id"] == curr["customer_id"] and
            abs(prev["amount"] - curr["amount"]) < 0.01 and
            prev["status"] == curr["status"] and
            prev["product_category"] == curr["product_category"]
        )

        time_diff = abs((curr["processed_timestamp"] - prev["processed_timestamp"]).total_seconds())

        if same_fields and time_diff <= threshold_seconds:
            duplicates.add(df_sorted.index[i - 1])  # mark earlier one as duplicate

    print(f"🔁 Found {len(duplicates)} near-duplicates")
    return duplicates


def detect_out_of_order(df):
    """
    Identify rows where processed_timestamp is earlier than the previous row’s
    processed_timestamp (i.e., arrived later but happened earlier).
    Assumes df is in CSV/arrival order.
    """
    out_of_order_indices = []

    prev_ts = None
    for idx, row in df.iterrows():
        curr_ts = row["processed_timestamp"]
        if pd.isnull(curr_ts):
            continue  # skip bad rows
        if prev_ts is not None and curr_ts < prev_ts:
            out_of_order_indices.append(idx)
        prev_ts = curr_ts

    return out_of_order_indices



def insert_clean_data_into_db(df):
    """
    Insert cleaned and validated transactions into the SQLite DB.

    Assumes schema:
    - original_timestamp and original_timezone from CSV
    - processed_timestamp in UTC
    - data_quality_flags stored as JSON string
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions")
    
    insert_query = """
    INSERT OR REPLACE INTO transactions (
        transaction_id,
        customer_id,
        amount,
        currency,
        original_timestamp,
        original_timezone,
        processed_timestamp,
        processed_timezone,
        status,
        product_category,
        data_quality_flags,
        created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    rows_to_insert = []
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    duplicates = detect_near_duplicates(df)

    for idx, row in df.iterrows():
        try:
            processed_ts = (
                row['processed_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                if pd.notnull(row['processed_timestamp']) else None
            )

            # ✅ Parse and update data_quality_flags with duplicate flag if needed
            flags_json = row['data_quality_flags']
            if isinstance(flags_json, str):
                flags = json.loads(flags_json).get("issues", [])
            elif isinstance(flags_json, dict):
                flags = flags_json.get("issues", [])
            elif isinstance(flags_json, list):
                flags = flags_json
            else:
                flags = []

            if idx in duplicates and "duplicate_candidate" not in flags:
                flags.append("duplicate_candidate")

            flags_json_final = json.dumps({"issues": flags} if flags else {})

            rows_to_insert.append((
                row['transaction_id'],
                row['customer_id'],
                float(row['amount']),
                row['currency'],
                row['timestamp'],  # original raw input
                row['timezone'] if row['timezone'] else None,
                processed_ts,
                "UTC",
                row['status'],
                row['product_category'],
                flags_json_final,
                now
            ))

        except Exception as e:
            print(f"⚠️ Skipping row due to error: {e}")

    cursor.executemany(insert_query, rows_to_insert)
    conn.commit()
    conn.close()

    print(f"✅ Inserted {len(rows_to_insert)} rows into the database.")
    print(duplicates)
