#!/usr/bin/env python3
# setup_db.py - Database initialization script

import sqlite3
import csv
import os
from datetime import datetime, timedelta
import random
import json

def create_directory_structure():
    """Create the required directory structure"""
    directories = ['data', 'tests', 'docs', 'docker']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Create .gitkeep files
    with open('data/.gitkeep', 'w') as f:
        f.write('')

def create_sample_data():
    """Generate messy sample transaction data"""
    
    # Different date formats and timezones to simulate real-world mess
    date_formats = [
        "%Y-%m-%d %H:%M:%S",    # Standard format
        "%m/%d/%y %I:%M %p",    # US format
        "%d-%b-%Y %H:%M",       # UK format
        "%Y-%m-%dT%H:%M:%SZ",   # ISO with Z
        "%Y-%m-%dT%H:%M:%S",    # ISO without timezone
    ]
    
    timezones = [
        "America/New_York", "Europe/London", "Asia/Tokyo", "UTC",
        "", "America/Los_Angeles", "Europe/Paris", "Australia/Sydney"
    ]
    
    currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
    categories = ["electronics", "clothing", "home", "books", "sports", "beauty", "toys"]
    statuses = ["completed", "pending", "failed"]
    
    sample_transactions = []
    base_date = datetime(2024, 1, 1)
    
    print("Generating sample transactions...")
    
    # Generate 5000 base transactions
    for i in range(5000):
        # Random date in Jan-March 2024
        days_offset = random.randint(0, 89)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        seconds_offset = random.randint(0, 59)
        
        trans_date = base_date + timedelta(
            days=days_offset, 
            hours=hours_offset, 
            minutes=minutes_offset,
            seconds=seconds_offset
        )
        
        # Apply different date formats to create parsing challenges
        format_choice = random.choice(date_formats)
        try:
            if format_choice == "%m/%d/%y %I:%M %p":
                timestamp = trans_date.strftime(format_choice)
            elif format_choice == "%d-%b-%Y %H:%M":
                timestamp = trans_date.strftime(format_choice)
            elif format_choice == "%Y-%m-%dT%H:%M:%SZ":
                timestamp = trans_date.strftime(format_choice)
            else:
                timestamp = trans_date.strftime(format_choice)
        except:
            timestamp = trans_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create some duplicate transactions with slight differences
        if i > 0 and random.random() < 0.02:  # 2% chance of duplicate
            prev_trans = sample_transactions[-1]
            # Copy previous transaction but with slight timestamp difference
            # Handle different timestamp formats from previous transaction
            prev_timestamp = prev_trans['timestamp']
            try:
                # Try to parse the previous timestamp in various formats
                if 'T' in prev_timestamp and prev_timestamp.endswith('Z'):
                    base_time = datetime.strptime(prev_timestamp.replace('Z', ''), "%Y-%m-%dT%H:%M:%S")
                elif 'T' in prev_timestamp:
                    base_time = datetime.strptime(prev_timestamp, "%Y-%m-%dT%H:%M:%S")
                elif '/' in prev_timestamp and ('AM' in prev_timestamp or 'PM' in prev_timestamp):
                    base_time = datetime.strptime(prev_timestamp, "%m/%d/%y %I:%M %p")
                elif '-' in prev_timestamp and len(prev_timestamp) > 16:
                    if prev_timestamp.count('-') == 3:  # Format like "15-Jan-2024 14:30"
                        base_time = datetime.strptime(prev_timestamp, "%d-%b-%Y %H:%M")
                    else:
                        base_time = datetime.strptime(prev_timestamp, "%Y-%m-%d %H:%M:%S")
                else:
                    base_time = datetime.strptime(prev_timestamp, "%Y-%m-%d %H:%M:%S")
                
                duplicate_time = base_time + timedelta(seconds=random.randint(1, 5))
                timestamp = duplicate_time.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                # If parsing fails, just use the current transaction's timestamp
                pass
        
        transaction = {
            'transaction_id': f"TXN-{i+1:05d}",
            'customer_id': f"CUST-{random.randint(1000, 9999)}",
            'amount': round(random.uniform(5.99, 999.99), 2),
            'currency': random.choice(currencies),
            'timestamp': timestamp,
            'timezone': random.choice(timezones),
            'status': random.choice(statuses),
            'product_category': random.choice(categories)
        }
        
        sample_transactions.append(transaction)
    
    # Add specific problematic records for testing
    problematic_records = [
        # Invalid date format
        {
            'transaction_id': 'TXN-BAD01',
            'customer_id': 'CUST-1111',
            'amount': 99.99,
            'currency': 'USD',
            'timestamp': '2024-13-45 25:99:99',  # Invalid date
            'timezone': 'UTC',
            'status': 'completed',
            'product_category': 'electronics'
        },
        # DST transition - spring forward (this time doesn't exist)
        {
            'transaction_id': 'TXN-DST01',
            'customer_id': 'CUST-2222',
            'amount': 150.00,
            'currency': 'USD',
            'timestamp': '2024-03-10 02:30:00',
            'timezone': 'America/New_York',
            'status': 'completed',
            'product_category': 'clothing'
        },
        # DST transition - fall back (this time occurs twice)
        {
            'transaction_id': 'TXN-DST02',
            'customer_id': 'CUST-3333',
            'amount': 200.00,
            'currency': 'USD',
            'timestamp': '2024-11-03 01:30:00',
            'timezone': 'America/New_York',
            'status': 'completed',
            'product_category': 'home'
        },
        # Missing timezone
        {
            'transaction_id': 'TXN-NOTZ01',
            'customer_id': 'CUST-4444',
            'amount': 75.50,
            'currency': 'EUR',
            'timestamp': '2024-01-15 12:00:00',
            'timezone': '',  # Empty timezone
            'status': 'completed',
            'product_category': 'books'
        },
        # Different date formats for same logical time
        {
            'transaction_id': 'TXN-FMT01',
            'customer_id': 'CUST-5555',
            'amount': 123.45,
            'currency': 'GBP',
            'timestamp': '15/01/2024 3:45 PM',  # US format
            'timezone': 'Europe/London',
            'status': 'completed',
            'product_category': 'sports'
        },
        {
            'transaction_id': 'TXN-FMT02',
            'customer_id': 'CUST-6666',
            'amount': 67.89,
            'currency': 'EUR',
            'timestamp': '15-Jan-2024 15:45',  # UK format
            'timezone': 'Europe/Paris',
            'status': 'completed',
            'product_category': 'beauty'
        }
    ]
    
    sample_transactions.extend(problematic_records)
    
    # Write to CSV
    csv_path = 'data/transactions.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['transaction_id', 'customer_id', 'amount', 'currency', 
                     'timestamp', 'timezone', 'status', 'product_category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_transactions)
    
    print(f"✅ Generated {len(sample_transactions)} sample transactions")
    print(f"   📁 Saved to: {csv_path}")
    return len(sample_transactions)

def setup_database():
    """Initialize SQLite database with proper schema and indexes"""
    db_path = 'data/ecommerce.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Setting up database schema...")
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            customer_id TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            currency TEXT NOT NULL,
            original_timestamp TEXT NOT NULL,
            original_timezone TEXT,
            processed_timestamp DATETIME,
            processed_timezone TEXT DEFAULT 'UTC',
            status TEXT NOT NULL,
            product_category TEXT NOT NULL,
            data_quality_flags TEXT,  -- JSON string for tracking issues
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for query performance
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_processed_timestamp ON transactions(processed_timestamp)',
        'CREATE INDEX IF NOT EXISTS idx_customer_id ON transactions(customer_id)',
        'CREATE INDEX IF NOT EXISTS idx_status ON transactions(status)',
        'CREATE INDEX IF NOT EXISTS idx_currency ON transactions(currency)',
        'CREATE INDEX IF NOT EXISTS idx_category ON transactions(product_category)',
        'CREATE INDEX IF NOT EXISTS idx_transaction_id ON transactions(transaction_id)'
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    # Create data quality summary table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_quality_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_records INTEGER,
            invalid_dates INTEGER DEFAULT 0,
            missing_timezones INTEGER DEFAULT 0,
            duplicate_transactions INTEGER DEFAULT 0,
            out_of_order_records INTEGER DEFAULT 0,
            other_issues INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database setup complete")
    print(f"   📁 Database location: {db_path}")

def create_additional_files():
    """Create additional repository files"""
    
    # Create requirements.txt for Python
    requirements_python = """# Core API dependencies
flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
pytz==2023.3
python-dateutil==2.8.2

# Optional but recommended
requests==2.31.0
flask-restx==1.1.0  # For API documentation

# Development and testing
pytest==7.4.0
pytest-flask==1.2.0
black==23.7.0
flake8==6.0.0

# Alternative frameworks (choose one)
# fastapi==0.103.0
# uvicorn==0.23.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_python)
    
    # Create package.json for Node.js alternative
    package_json = {
        "name": "ecommerce-analytics-api",
        "version": "1.0.0",
        "description": "E-commerce Analytics API Challenge",
        "main": "app.js",
        "scripts": {
            "start": "node app.js",
            "dev": "nodemon app.js",
            "test": "jest"
        },
        "dependencies": {
            "express": "^4.18.2",
            "cors": "^2.8.5",
            "sqlite3": "^5.1.6",
            "moment-timezone": "^0.5.43",
            "csv-parser": "^3.0.0"
        },
        "devDependencies": {
            "nodemon": "^3.0.1",
            "jest": "^29.6.0",
            "supertest": "^6.3.3"
        }
    }
    
    with open('package.json', 'w') as f:
        json.dump(package_json, f, indent=2)
    
    print("✅ Created additional repository files:")
    print("   📄 requirements.txt (Python dependencies)")
    print("   📄 package.json (Node.js alternative)")

if __name__ == "__main__":
    print("🚀 Setting up E-commerce Analytics Challenge Repository...")
    print("=" * 60)
    
    print("1. Creating directory structure...")
    create_directory_structure()
    
    print("2. Generating messy sample data...")
    record_count = create_sample_data()
    
    print("3. Setting up SQLite database...")
    setup_database()
    
    print("4. Creating additional repository files...")
    create_additional_files()
    
    print("=" * 60)
    print("🎉 Repository setup complete!")
    print(f"   📊 Generated {record_count} sample transactions")
    print(f"   🗄️  SQLite database created at data/ecommerce.db")
    print(f"   📁 Sample CSV data at data/transactions.csv")
    print()
    print("🏁 Next steps for candidates:")
    print("   1. Choose your tech stack (Python/Flask, Node.js/Express, etc.)")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Start building your API!")
    print("   4. Test with the examples in docs/api_examples.md")
    print()
    print("💡 This repository is ready to be zipped and shared!")