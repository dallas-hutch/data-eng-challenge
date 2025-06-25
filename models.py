import sqlite3
from config import DATABASE_PATH
import pandas as pd
import pytz
import calendar

def get_daily_sales_summary(start_date_str, end_date_str, timezone_str):
    """
    Summarize daily sales between two dates in a given timezone.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    query = """
    SELECT processed_timestamp, amount
    FROM transactions
    WHERE processed_timestamp IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return {
            "data": [],
            "timezone": timezone_str,
            "period": f"{start_date_str} to {end_date_str}",
            "summary": {
                "total_sales": 0,
                "total_transactions": 0,
                "average_daily_sales": 0
            }
        }

    # Parse dates and apply timezone
    df["processed_timestamp"] = pd.to_datetime(df["processed_timestamp"], utc=True)
    local_tz = pytz.timezone(timezone_str)
    df["local_dt"] = df["processed_timestamp"].dt.tz_convert(local_tz)

    # Filter to requested date range in local time
    start_date = pd.to_datetime(start_date_str).date()
    end_date = pd.to_datetime(end_date_str).date()
    df = df[(df["local_dt"].dt.date >= start_date) & (df["local_dt"].dt.date <= end_date)]


    # Group by local date
    df["local_date"] = df["local_dt"].dt.date
    summary_df = df.groupby("local_date").agg(
        total_sales=("amount", "sum"),
        transaction_count=("amount", "count"),
        average_order_value=("amount", "mean")
    ).reset_index()

    # Prepare detailed per-day records
    summary_df["date"] = summary_df["local_date"].astype(str)
    summary_df["total_sales"] = summary_df["total_sales"].round(2)
    summary_df["average_order_value"] = summary_df["average_order_value"].round(2)

    records = summary_df[["date", "total_sales", "transaction_count", "average_order_value"]].to_dict(orient="records")

    # Compute overall summary
    total_sales = round(summary_df["total_sales"].sum(), 2)
    total_tx = int(summary_df["transaction_count"].sum())
    avg_daily_sales = round(total_sales / len(summary_df), 2)

    return {
        "data": records,
        "timezone": timezone_str,
        "period": f"{start_date_str} to {end_date_str}",
        "summary": {
            "total_sales": total_sales,
            "total_transactions": total_tx,
            "average_daily_sales": avg_daily_sales
        }
    }


def get_hourly_sales_summary(date_str, timezone_str):
    """
    Return total sales and transaction counts for each hour of a specific date.
    """
    conn = sqlite3.connect(DATABASE_PATH)

    # Query all rows where processed_timestamp is on the given date
    query = """
    SELECT 
        processed_timestamp,
        amount
    FROM transactions
    WHERE 
        processed_timestamp IS NOT NULL AND
        DATE(processed_timestamp) = ?
    """
    df = pd.read_sql_query(query, conn, params=(date_str,))
    conn.close()

    if df.empty:
        return {
            "data": [],
            "timezone": timezone_str,
            "date": date_str
        }

    df["processed_timestamp"] = pd.to_datetime(df["processed_timestamp"], utc=True)
    local_tz = pytz.timezone(timezone_str)
    df["local_hour"] = df["processed_timestamp"].dt.tz_convert(local_tz).dt.floor("H")

    summary = df.groupby("local_hour").agg(
        total_sales=("amount", "sum"),
        transaction_count=("amount", "count")
    ).reset_index()

    # Format output
    summary["hour"] = summary["local_hour"].dt.strftime("%Y-%m-%d %H:%M:%S")
    summary["total_sales"] = summary["total_sales"].round(2)

    return {
        "data": summary[["hour", "total_sales", "transaction_count"]].to_dict(orient="records"),
        "timezone": timezone_str,
        "date": date_str
    }

def get_period_comparison(period1_str, period2_str, timezone_str):
    def get_period_bounds(period_str):
        year, month = map(int, period_str.split("-"))
        start = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end = f"{year}-{month:02d}-{last_day}"
        return start, end

    conn = sqlite3.connect(DATABASE_PATH)

    p1_start, p1_end = get_period_bounds(period1_str)
    p2_start, p2_end = get_period_bounds(period2_str)

    query = """
    SELECT processed_timestamp, amount
    FROM transactions
    WHERE processed_timestamp IS NOT NULL
      AND DATE(processed_timestamp) BETWEEN ? AND ?
    """

    # Get both periods
    df1 = pd.read_sql_query(query, conn, params=(p1_start, p1_end))
    df2 = pd.read_sql_query(query, conn, params=(p2_start, p2_end))
    conn.close()

    def summarize(df):
        if df.empty:
            return {"total_sales": 0, "transaction_count": 0}
        return {
            "total_sales": round(df["amount"].sum(), 2),
            "transaction_count": int(df["amount"].count())
        }

    s1 = summarize(df1)
    s2 = summarize(df2)

    # Calculate percent change
    def pct_change(v1, v2):
        if v1 == 0:
            return None
        return round(((v2 - v1) / v1) * 100, 2)

    return {
        "period1": {
            "start": p1_start,
            "end": p1_end,
            **s1
        },
        "period2": {
            "start": p2_start,
            "end": p2_end,
            **s2
        },
        "growth": {
            "sales_change_percent": pct_change(s1["total_sales"], s2["total_sales"]),
            "transaction_change_percent": pct_change(s1["transaction_count"], s2["transaction_count"])
        }
    }

def get_data_quality_report():
    conn = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql_query("SELECT data_quality_flags FROM transactions", conn)
    conn.close()

    def count_flag(df, keyword):
        return int(df["data_quality_flags"].str.contains(keyword).sum())

    total = int(len(df))

    return {
        "total_records": total,
        "issues_found": {
            "invalid_dates": count_flag(df, "invalid_date_format"),
            "missing_timezones": count_flag(df, "missing_timezone"),
            "duplicate_transactions": count_flag(df, "duplicate_candidate"),
            "out_of_order_records": count_flag(df, "out_of_order") # will update, hardcoded for now
        },
        "resolution_summary": {
            "invalid_dates": "Unparseable dates excluded, localized timestamp if possible",
            "missing_timezones": "Assumed UTC if local timestamp was valid",
            "duplicates": "Kept latest timestamp version within 10 second threshold",
            "out_of_order": "Reordered by actual transaction time"
        }
    }
