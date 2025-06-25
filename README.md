# E-commerce Analytics API Solution

**Candidate:** Dallas Hutchinson  
**Time Spent:** 4.5 hours  
**Language/Framework:** [Python/Flask]

## Quick Start

```bash
# Setup instructions
# 1. Clone the repo
git clone https://github.com/your-username/data-eng-challenge.git
cd data-eng-challenge

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate         # On macOS/Linux
venv\\Scripts\\activate          # On Windows

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Initialize the SQLite database and load data
python setup_db.py

# 5. Run the Flask API
python app.py

# See below for tests and API curl commands
```

**API Base URL:** `http://localhost:5000`

## Implementation Decisions

### 1. Date/Time Handling Strategy

**Missing Timezones:**
- [X] Assumed UTC
- [ ] Inferred from business hours  
- [ ] Skipped records
- [ ] Other: ___________

**Rationale:** [If timezone was an empty string or missing, UTC was assumed for consistency sake. Reduces any regional bias or guessing while allowing for standardization. Missing timezone was also flagged in the data quality flags to count these cases. Since a large portion of the dataset contained missing timezones, dropping records felt too costly.]

**DST Transitions:**
- **Spring Forward:** [Assumed a jump forward of +1 hour to account for non-existent times. The assumption here is that the timestamp moment of capture had not caught up with the spring forward in time.]
- **Fall Back:** [For local times that occured twice, I assumed the first occurrence was the true timestamp. I could understand using the second as the true time as well but this seemed more conservative.]

**Date Format Parsing:**
- Library used: [python-dateutil, pytz]
- Fallback strategy: [Unparseable dates were skipped and logged (low volume)]

### 2. Data Quality Approach

**Duplicate Detection:**
- Strategy: [Chosen time window for duplicate records was 10 seconds and then the greater of the two was chosen as the timestamp. Duplciate candidates flagged in the data quality flags. Matching customer ID, amount, status and category were used to determine duplicate eligbility. Chosing the later of the two felt like it would capture the true "corrected" record or a potential transaction processing error. The chosen threshold also felt short enough to avoid any instances of real nearly-identical purchases.]
- Threshold: [10 seconds tolerance]

**Invalid Data:**
- Invalid dates: [If the parser couldn't localize the date, the processed timestamp would return null. I did consider a rollback to the nearest valid date but that didn't seem justifiable. Invalid date format flag added for data quality.]
- Invalid timezones: [UTC was assumed for any missing timezone rows. The parser uses dayfirst to try to interpret ambiguous formats. And missing timezone was added to the data quality flag set.]
- Negative amounts: [Negative amounts were not handled in the data cleaning pipeline (would add in production if supported by business case), absolute value used in summary data modeling.]

**Records processed:** 5005/5006 timestamps
**Records skipped:** 1 (see data quality endpoint for details)

### 3. API Design Choices

**Timezone Parameter:**
- Default: [Default timezone assumed is UTC, set in config.]
- Validation: [Check for valid date format and period format. Then localize timestamp to match to user inputted timezone.]

**Error Responses:**
- Format: [The JSON structure for errors is fairly basic and could be more robust to handle more variety of potential errors. The structure is the error, message, code and then current timestamp for the user.]
- HTTP Status Codes: [Default status code is a 400 Bad Request code. Similar for hourly, daily and period comparison errors. Data quality report uses a 500 Interal Server Error status code.]

**Performance Optimizations:**
- Database indexing: [Indices only added to modeling SQL queries to reset returned datasets.]
- Query optimization: [In the future, I'd try to use stored views to store historical unchanged data and only update outputs as necessary.]
- Caching: [Not implented yet]

## API Documentation

### Endpoints Implemented

- [x] `GET /api/sales/daily`
- [x] `GET /api/sales/hourly` 
- [x] `GET /api/sales/compare`
- [x] `GET /api/data-quality`
- [ ] Additional endpoints: ___________


## Testing

### How to Test

```bash
# Run unit tests
# 1 expected to fail
python -m pytest tests/

# API testing
# Daily sales
curl "http://localhost:5000/api/sales/daily?start_date=2024-01-01&end_date=2024-01-31&timezone=America/New_York"

# Hourly breakdown
curl "http://localhost:5000/api/sales/hourly?date=2024-01-15&timezone=UTC"

# Period comparison
curl "http://localhost:5000/api/sales/compare?period1=2024-01&period2=2024-02"

# Data quality report
curl "http://localhost:5000/api/data-quality"

# Test spring forward (March 10, 2024)
curl "http://localhost:5000/api/sales/hourly?date=2024-03-10&timezone=America/New_York"

# Test fall back (November 3, 2024)  
# NOTE: will throw error and this case is a known limitation of the API design
curl "http://localhost:5000/api/sales/hourly?date=2024-11-03&timezone=America/New_York"

# Invalid date format
curl "http://localhost:5000/api/sales/daily?start_date=invalid&end_date=2024-01-31"
```

### Edge Cases Handled

- [x] DST spring forward (non-existent time)
- [] DST fall back (ambiguous time)  
- [x] Missing timezone information
- [x] Multiple date formats
- [x] Invalid dates
- [x] Duplicate transactions
- [x] Cross-timezone queries
- [X] Other: _Out of order data quality flag__

### Known Issues

1. **Issue:** [The handling of the DST fall back is not working as intended. It seems like pytz can handle ambiguous time errors and then I should be able to localize and force DST to be true. If working on this, I'd need to be do some debugging to see where this part of the parser is going wrong. Possibility for slow API requests for large date ranges. The daily summary model specifically has an un-optimized query to initially pull data. I also think FastAPI framework works better at handling large datasets and could be beneficial in a production system.]
**Impact:** [There is a failed API unit test due to the DST fall back not being handled properly. This will also impact the get request for that timestamp day.]
**Workaround:** [Avoiding fall back date until it's fixed.]

2. **Performance:** [Query optimization could use work, especially as the dataset becomes larger. Need to increase flexibility to handle more timestamp data errors like the DST fall back.]

## Architecture

### Database Schema

[Final transactions table retains the recommended structure seen in schema.md]

### Code Structure

```
data-eng-challenge/
├── app.py                 # Main application
├── models.py              # Data models
├── utils.py               # Helper functions
├── date_utils.py          # Date/time handling
├── config.py              # Configuration
└── tests/
    ├── test_api.py        # API tests
    └── test_date_utils.py # Date handling tests
```

## Time Allocation

- **Data exploration/understanding:** 0.25 hours
- **Date/time handling logic:** 2-2.5 hours  
- **API implementation:** 0.75-1 hours
- **Testing and debugging:** 0.75 hours
- **Documentation:** 0.5 hours

**Total:** 4.5 hours

## Reflection

### What Went Well
- [I'm most proud of the data cleaning pipeline. While it has some flaws, getting to a relatively clean table to build endpoints off was a good feat considering a recent lack of experience in processing complicated timestamp data.]

### What Was Challenging  
- [I've been primarily coding in R the past two and a half years and forgot just how versatile Python was. I also don't work with timestamp data very often. Ambiguous timestamps/timezones, edge case handling, and building the parser took the majority of my time. I probably spent too much time trying to fix my DST fall back limitation. Went down a rabbit hole and could've used that time better to improve the API design and architecture.]

### What You'd Do Differently
- [I'd love to spend more time building out more endpoint capabilities and unit testing. Also, trying out different frameworks for data cleaning, handling time data and API frameworks seems useful to see if any others are easier/more flexible to use. Would also love to dive deeper into the unused columns (customer ID assumptions baked into the data cleaning process, currency conversion, status categorization).]

### Production Considerations
- [What would you add for a production system? Optimized SQL queries (views, smart batch processing), newer API framework to handle larger datasets, improved and more thorough code documentation, increased testing and validation, containerization]
- Monitoring and logging [some basic logging is used, but would add error log that allows it to be traceable back in time]
- Authentication/authorization [role-based access control, secure keys]
- Rate limiting [Flask has a rate limiter I believe to control user requests]
- Database connection pooling [a switch to a Snowflake db could protect overflow and support concurrent requests]
- Error tracking
- Deployment strategy [containerization for staging and dev systems, versioning, CI/CD considerations]

---

*Thank you for reviewing my solution!*
