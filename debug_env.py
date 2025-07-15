#!/usr/bin/env python3
"""
Debug script to check environment variables and database connection
"""

import os
import sys
from urllib.parse import quote_plus

print("=== Environment Variables Debug ===")
print(f"MYSQL_HOST: {os.environ.get('MYSQL_HOST', 'NOT SET')}")
print(f"MYSQL_USER: {os.environ.get('MYSQL_USER', 'NOT SET')}")
print(f"MYSQL_PASSWORD: {os.environ.get('MYSQL_PASSWORD', 'NOT SET')}")
print(f"MYSQL_DB: {os.environ.get('MYSQL_DB', 'NOT SET')}")

# Test URL encoding
mysql_password = os.environ.get('MYSQL_PASSWORD', '')
if mysql_password:
    escaped_password = quote_plus(mysql_password)
    print(f"Original password: {mysql_password}")
    print(f"Escaped password: {escaped_password}")
    
    mysql_host = os.environ.get('MYSQL_HOST', 'mysql')
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_db = os.environ.get('MYSQL_DB', 'gmail_ai_agent')
    
    connection_string = f"mysql+pymysql://{mysql_user}:{escaped_password}@{mysql_host}/{mysql_db}"
    print(f"Connection string: {connection_string}")

# Test basic MySQL connection
try:
    import pymysql
    
    connection = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'mysql'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', ''),
        database=os.environ.get('MYSQL_DB', 'gmail_ai_agent'),
        charset='utf8mb4'
    )
    print("✅ MySQL connection successful!")
    connection.close()
    
except Exception as e:
    print(f"❌ MySQL connection failed: {e}")

# Test config import
try:
    sys.path.insert(0, '/app')
    from config.config import Config
    config = Config()
    print(f"✅ Config import successful!")
    print(f"Database URI: {config.SQLALCHEMY_DATABASE_URI}")
    
except Exception as e:
    print(f"❌ Config import failed: {e}")
