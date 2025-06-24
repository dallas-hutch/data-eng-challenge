# E-commerce Analytics API - Data Engineering Challenge

## Overview
Build a REST API that processes and serves e-commerce transaction data with proper date/time handling. The provided dataset contains real-world data quality issues that you'll need to resolve.

## Time Limit
**3-4 hours** (we're looking for working code, not perfection!)

## Quick Start

```bash
# Extract the zip file
unzip ecommerce-analytics-challenge.zip
cd ecommerce-analytics-challenge

# Install dependencies (Python example)
pip install -r requirements.txt

# Generate sample data and setup database
python setup_db.py

# Start building your API!
# (Create app.py, main.py, or your preferred entry point)
```

## Repository Structure

```
ecommerce-analytics-challenge/
├── README.md                 # This file
├── setup_db.py              # Database initialization script
├── requirements.txt          # Python dependencies (or package.json for Node)
├── requirements-node.txt     # Node.js alternative
├── data/
│   ├── schema.md            # Expected data structure
│   ├── test_cases.md        # Specific test scenarios
│   └── .gitkeep             # Files will be generated here
├── tests/
│   ├── test_examples.py     # Sample test cases
│   └── __init__.py
├── docs/
│   └── api_examples.md      # API usage examples
└── docker/
    ├── Dockerfile           # Optional containerization
    └── docker-compose.yml   # Optional orchestration
```

## The Challenge

You have transaction data from an e-commerce platform that operates globally. The data has several quality issues you must handle:

### Data Issues You'll Encounter:
- **Mixed timezones**: Some records in UTC, others in local time zones, some missing timezone info
- **Inconsistent date formats**: `2024-01-15`, `01/15/24`, `15-Jan-2024`, `2024-01-15 14:30:00`
- **Daylight Saving Time**: Transactions during DST transitions
- **Out-of-order timestamps**: Some events arrived late due to network issues
- **Partial data**: Missing hours, duplicate records with slight timestamp differences

### Required API Endpoints

Build these endpoints that handle the messy data correctly:

#### 1. Daily Sales Summary
```
GET /api/sales/daily?start_date=2024-01-01&end_date=2024-01-31&timezone=America/New_York
```
Response:
```json
{
  "data": [
    {
      "date": "2024-01-01",
      "total_sales": 15420.50,
      "transaction_count": 87,
      "average_order_value": 177.13
    }
  ],
  "timezone": "America/New_York",
  "period": "2024-01-01 to 2024-01-31"
}
```

#### 2. Hourly Sales (for a specific date)
```
GET /api/sales/hourly?date=2024-01-15&timezone=UTC
```
Response:
```json
{
  "data": [
    {
      "hour": "2024-01-15 00:00:00",
      "total_sales": 1240.30,
      "transaction_count": 12
    }
  ],
  "timezone": "UTC",
  "date": "2024-01-15"
}
```

#### 3. Period Comparison
```
GET /api/sales/compare?period1=2024-01&period2=2024-02&timezone=Europe/London
```
Response:
```json
{
  "period1": {
    "start": "2024-01-01",
    "end": "2024-01-31",
    "total_sales": 458920.30,
    "transaction_count": 2847
  },
  "period2": {
    "start": "2024-02-01",
    "end": "2024-02-29", 
    "total_sales": 523180.75,
    "transaction_count": 3102
  },
  "growth": {
    "sales_change_percent": 14.02,
    "transaction_change_percent": 8.96
  }
}
```

#### 4. Data Quality Report
```
GET /api/data-quality
```
Response showing how you handled data issues:
```json
{
  "total_records": 50000,
  "issues_found": {
    "invalid_dates": 127,
    "missing_timezones": 2341,
    "duplicate_transactions": 89,
    "out_of_order_records": 456
  },
  "resolution_summary": {
    "invalid_dates": "Excluded from analysis",
    "missing_timezones": "Assumed UTC based on server logs",
    "duplicates": "Kept latest timestamp version",
    "out_of_order": "Reordered by actual transaction time"
  }
}
```

## Sample Data

After running `python setup_db.py`, you'll have:
- `data/transactions.csv` - Main transaction data (messy!)
- `data/ecommerce.db` - SQLite database with indexed tables
- Sample records with various date/time formatting issues

### Sample Transaction Record:
```csv
transaction_id,customer_id,amount,currency,timestamp,timezone,status,product_category
TXN-001,CUST-5432,129.99,USD,"2024-01-15 14:30:00",America/New_York,completed,electronics
TXN-002,CUST-1234,89.50,EUR,15/01/2024 09:15,Europe/London,completed,clothing  
TXN-003,CUST-9876,234.75,USD,2024-01-15T19:45:00Z,,completed,home
```

## Evaluation Criteria

### Must Have (70%)
- ✅ API runs locally and responds to requests
- ✅ Handles basic date/timezone conversions
- ✅ Returns correct JSON structure
- ✅ Basic error handling (400/500 responses)

### Nice to Have (20%)
- ✅ Comprehensive data validation and cleaning
- ✅ Handles DST transitions correctly
- ✅ Performance optimization for large datasets
- ✅ API documentation (comments or OpenAPI)
- ✅ Unit tests for date handling logic

### Bonus Points (10%)
- ✅ Dockerfile for easy setup
- ✅ Database indexing strategy
- ✅ Monitoring/logging
- ✅ Creative solutions to data quality issues

## Technical Requirements

- **Language**: Python, Node.js, Go, or Java
- **Database**: SQLite (provided), PostgreSQL, or MySQL
- **Framework**: Your choice (Flask, FastAPI, Express, Spring Boot, etc.)
- **Must run locally** without external services

## Getting Help

- Check `data/schema.md` for data structure details
- Review `data/test_cases.md` for specific scenarios to handle
- See `docs/api_examples.md` for sample requests
- Look at `tests/test_examples.py` for test inspiration

## Submission

1. Create your API implementation
2. Include a `SOLUTION.md` with:
   - Setup instructions for your specific solution
   - API documentation
   - Assumptions you made about data quality issues
   - Known limitations/tradeoffs
   - How to test your implementation
3. Zip your entire solution folder
4. Submit via email

## Questions?

If you encounter any blockers or need clarification, email us. We're looking for working code and thoughtful problem-solving, not perfection!

---

**Time expectation**: 3-4 hours  
**Focus on**: Date/time handling, API design, data quality decisions
