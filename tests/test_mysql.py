import pytest
import pymysql
import os
import time

# Configuration
MYSQL_HOST = os.getenv('MYSQL_NODE_IP', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_NODE_PORT', '30306'))
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'rootpassword'
MYSQL_DATABASE = 'testdb'

def get_mysql_connection():
    """Get MySQL connection with retry logic"""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            connection = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                connect_timeout=5
            )
            return connection
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

def test_mysql_connection():
    """Test 1: Connect to MySQL using NodePort"""
    connection = get_mysql_connection()
    assert connection is not None
    connection.close()
    print("✓ Successfully connected to MySQL")

def test_mysql_query_record():
    """Test 2: Query the record and verify data"""
    connection = get_mysql_connection()
    
    try:
        with connection.cursor() as cursor:
            # Query the results table
            cursor.execute("SELECT id, test_id, status, executed_at FROM results ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            
            assert result is not None, "No record found in results table"
            
            # Verify record structure
            assert len(result) == 4, f"Expected 4 columns, got {len(result)}"
            
            record_id, test_id, status, executed_at = result
            
            # Verify data
            assert test_id == 'TEST-001', f"Expected test_id='TEST-001', got '{test_id}'"
            assert status == 'pass', f"Expected status='pass', got '{status}'"
            assert executed_at is not None, "executed_at should not be None"
            
            print(f"✓ Record verified: id={record_id}, test_id={test_id}, status={status}, executed_at={executed_at}")
            
    finally:
        connection.close()

def test_mysql_table_structure():
    """Test 3: Verify table structure"""
    connection = get_mysql_connection()
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE results")
            columns = cursor.fetchall()
            
            column_names = [col[0] for col in columns]
            assert 'id' in column_names, "Column 'id' not found"
            assert 'test_id' in column_names, "Column 'test_id' not found"
            assert 'status' in column_names, "Column 'status' not found"
            assert 'executed_at' in column_names, "Column 'executed_at' not found"
            
            print("✓ Table structure verified")
            
    finally:
        connection.close()

