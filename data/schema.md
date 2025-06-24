# Transaction Data Schema

## Expected CSV Structure

```csv
transaction_id,customer_id,amount,currency,timestamp,timezone,status,product_category
TXN-00001,CUST-5432,129.99,USD,"2024-01-15 14:30:00",America/New_York,completed,electronics
TXN-00002,CUST-1234,89.50,EUR,15/01/2024 09:15,Europe/London,completed,clothing  
TXN-00003,CUST-9876,234.75,USD,2024-01-15T19:45:00Z,,completed,home
```

## Field Definitions

| Field | Type | Description | Data Quality Issues |
|-------|------|-------------|-------------------|
| `transaction_id` | String | Unique identifier (TXN-##### format) | Generally clean |
| `customer_id` | String | Customer identifier (CUST-#### format) | Generally clean |
| `amount` | Decimal | Transaction amount (positive values) | Generally clean |
| `currency` | String | ISO 4217 currency code | Generally clean |
| `timestamp` | String | **MESSY** - Various formats | ⚠️ **Major Issues** |
| `timezone` | String | IANA timezone name | ⚠️ **Often Missing** |
| `status` | String | completed, pending, failed | Generally clean |
| `product_category` | String | Product category | Generally clean |

## Known Timestamp Formats

Your parser needs to handle ALL of these:

1. **Standard ISO**: `2024-01-15 14:30:00`
2. **US Format**: `01/15/24 2:30 PM`
3. **UK Format**: `15-Jan-2024 14:30`
4. **ISO with UTC**: `2024-01-15T14:30:00Z`
5. **ISO without timezone**: `2024-01-15T14:30:00`
6. **Microseconds**: `2024-01-15 14:30:00.123456`
7. **Date only**: `2024-01-15` (assume midnight)

## Known Timezone Issues

- **Empty string**: `""` (about 15% of records)
- **Mixed formats**: Some use abbreviations vs full names
- **Invalid zones**: A few records have typos
- **DST complications**: Times during transitions

## Database Schema (SQLite)

After processing, your clean data should fit this structure:

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE NOT NULL,
    customer_id TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT NOT NULL,
    original_timestamp TEXT NOT NULL,        -- Raw input
    original_timezone TEXT,                  -- Raw input
    processed_timestamp DATETIME,            -- Cleaned UTC timestamp
    processed_timezone TEXT DEFAULT 'UTC',  -- Target timezone
    status TEXT NOT NULL,
    product_category TEXT NOT NULL,
    data_quality_flags TEXT,                 -- JSON with issues found
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Data Quality Flags

Track issues found during processing:

```json
{
  "issues": [
    "missing_timezone",
    "ambiguous_dst", 
    "invalid_date_format",
    "duplicate_candidate"
  ],
  "resolution": "assumed_utc",
  "confidence": "medium"
}
```
