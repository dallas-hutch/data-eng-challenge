# API Usage Examples

## Sample Requests

### 1. Daily Sales Summary

```bash
# Basic request
curl "http://localhost:5000/api/sales/daily?start_date=2024-01-01&end_date=2024-01-31"

# With timezone conversion
curl "http://localhost:5000/api/sales/daily?start_date=2024-01-01&end_date=2024-01-31&timezone=America/New_York"

# Single day
curl "http://localhost:5000/api/sales/daily?start_date=2024-01-15&end_date=2024-01-15"
```

### 2. Hourly Sales

```bash
# Hourly breakdown for a specific date
curl "http://localhost:5000/api/sales/hourly?date=2024-01-15&timezone=UTC"

# Different timezone
curl "http://localhost:5000/api/sales/hourly?date=2024-01-15&timezone=Europe/London"
```

### 3. Period Comparison

```bash
# Compare two months
curl "http://localhost:5000/api/sales/compare?period1=2024-01&period2=2024-02"

# With timezone
curl "http://localhost:5000/api/sales/compare?period1=2024-01&period2=2024-02&timezone=America/New_York"
```

### 4. Data Quality Report

```bash
curl "http://localhost:5000/api/data-quality"
```

## Expected Response Formats

### Daily Sales Response
```json
{
  "data": [
    {
      "date": "2024-01-01",
      "total_sales": 15420.50,
      "transaction_count": 87,
      "average_order_value": 177.13
    },
    {
      "date": "2024-01-02", 
      "total_sales": 18932.25,
      "transaction_count": 104,
      "average_order_value": 182.04
    }
  ],
  "timezone": "America/New_York",
  "period": "2024-01-01 to 2024-01-31",
  "summary": {
    "total_sales": 458920.30,
    "total_transactions": 2847,
    "average_daily_sales": 14803.88
  }
}
```

### Error Response Format
```json
{
  "error": "Invalid date format",
  "message": "start_date must be in YYYY-MM-DD format",
  "code": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Testing Edge Cases

### DST Transition Day
```bash
# Test spring forward (March 10, 2024)
curl "http://localhost:5000/api/sales/hourly?date=2024-03-10&timezone=America/New_York"

# Test fall back (November 3, 2024)  
curl "http://localhost:5000/api/sales/hourly?date=2024-11-03&timezone=America/New_York"
```

### Invalid Requests
```bash
# Invalid date format
curl "http://localhost:5000/api/sales/daily?start_date=invalid&end_date=2024-01-31"

# Invalid timezone
curl "http://localhost:5000/api/sales/daily?start_date=2024-01-01&end_date=2024-01-31&timezone=Invalid/Zone"
```
