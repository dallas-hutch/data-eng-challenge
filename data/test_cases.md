# Critical Test Scenarios

Your API must handle these specific edge cases correctly:

## 1. Daylight Saving Time Challenges

### Spring Forward (Clocks jump ahead)
**Date**: March 10, 2024, 2:00 AM → 3:00 AM in America/New_York

```
Problem Record:
  timestamp: "2024-03-10 02:30:00"
  timezone: "America/New_York"

Issue: This time literally doesn't exist!
Solutions:
  - Skip to 3:30 AM
  - Reject the record
  - Assume it's 1:30 AM (before jump)
  - Assume it's 3:30 AM (after jump)

Document your choice!
```

### Fall Back (Clocks jump backward)
**Date**: November 3, 2024, 2:00 AM → 1:00 AM in America/New_York

```
Problem: This hour happens TWICE
  First occurrence: 1:30 AM EDT (before fall back)
  Second occurrence: 1:30 AM EST (after fall back)

Test data includes multiple transactions at "2024-11-03 01:30:00"
How do you distinguish them?
```

## 2. Missing Timezone Scenarios

```csv
transaction_id,timestamp,timezone,amount
TXN-MISSING01,"2024-01-15 10:00:00","",129.99
TXN-MISSING02,"2024-01-15 22:00:00","",89.50
```

**Questions to answer:**
- Do you assume UTC?
- Do you guess based on business hours?
- Do you skip these records?
- Do you infer from other customer transactions?

## 3. Date Format Parsing Tests

Your parser should handle ALL of these correctly:

```csv
# Same logical time, different formats
TXN-FMT01,"2024-01-15 14:30:00","UTC",100.00
TXN-FMT02,"01/15/24 2:30 PM","UTC",100.00  
TXN-FMT03,"15-Jan-2024 14:30","UTC",100.00
TXN-FMT04,"2024-01-15T14:30:00Z","",100.00
TXN-FMT05,"2024-01-15T14:30:00","UTC",100.00
```

**Expected result**: All should convert to the same UTC timestamp.

## 4. Duplicate Detection

```csv
# Are these duplicates or separate transactions?
TXN-DUP01,CUST-1234,99.99,USD,"2024-01-15 10:00:00",UTC,completed,electronics
TXN-DUP02,CUST-1234,99.99,USD,"2024-01-15 10:00:03",UTC,completed,electronics
```

**Consider:**
- Same customer, amount, time (+3 seconds)
- Network retry vs. legitimate purchase?
- Your deduplication strategy?

## 5. Cross-Timezone API Tests

### Test Case: Daily Sales with Timezone Conversion

```bash
# Request: Daily sales in New York timezone
GET /api/sales/daily?start_date=2024-01-15&end_date=2024-01-15&timezone=America/New_York

# Database contains transactions:
# - 2024-01-15 23:30:00 UTC (6:30 PM NY time - should be included)
# - 2024-01-16 04:30:00 UTC (11:30 PM NY time - should be included) 
# - 2024-01-16 05:30:00 UTC (12:30 AM NY time - should NOT be included)
```

**Expected behavior**: Correctly convert UTC to NY time before filtering.

## 6. Sample Test Commands

Use these to validate your implementation:

```bash
# Basic functionality
curl -X GET "http://localhost:5000/api/sales/daily?start_date=2024-01-01&end_date=2024-01-31"

# Timezone handling
curl -X GET "http://localhost:5000/api/sales/daily?start_date=2024-01-01&end_date=2024-01-31&timezone=America/New_York"

# DST edge case
curl -X GET "http://localhost:5000/api/sales/hourly?date=2024-03-10&timezone=America/New_York"

# Error handling
curl -X GET "http://localhost:5000/api/sales/daily?start_date=invalid"

# Data quality
curl -X GET "http://localhost:5000/api/data-quality"
```
