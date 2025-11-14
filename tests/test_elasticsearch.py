import pytest
import requests
import os
import time
from elasticsearch import Elasticsearch

# Configuration
ES_HOST = os.getenv('ES_NODE_IP', 'localhost')
ES_PORT = int(os.getenv('ES_NODE_PORT', '30200'))
ES_URL = f"http://{ES_HOST}:{ES_PORT}"

def get_elasticsearch_client():
    """Get Elasticsearch client with retry logic"""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            es = Elasticsearch([ES_URL], request_timeout=5)
            if es.ping():
                return es
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise
    
    raise Exception("Failed to connect to Elasticsearch after all retries")

def test_elasticsearch_connection():
    """Test 1: Connect to Elasticsearch using NodePort"""
    es = get_elasticsearch_client()
    assert es.ping()
    print("✓ Successfully connected to Elasticsearch")

def test_elasticsearch_index_exists():
    """Test 2: Verify test-results index exists"""
    es = get_elasticsearch_client()
    assert es.indices.exists(index="test-results")
    print("✓ Index 'test-results' exists")

def test_elasticsearch_query_vaft_004():
    """Test 3: Query for test_id='VAFT-004' and assert status is 'pass'"""
    es = get_elasticsearch_client()
    
    # Refresh index to ensure all documents are searchable
    es.indices.refresh(index="test-results")
    
    # Query for test_id="VAFT-004"
    query = {
        "query": {
            "term": {
                "test_id": "VAFT-004"
            }
        }
    }
    
    response = es.search(index="test-results", body=query)
    
    assert response is not None, "Search response is None"
    assert 'hits' in response, "No 'hits' in response"
    assert 'total' in response['hits'], "No 'total' in response['hits']"
    
    total = response['hits']['total']
    if isinstance(total, dict):
        total_count = total['value']
    else:
        total_count = total
    
    assert total_count > 0, f"Expected at least 1 document with test_id='VAFT-004', found {total_count}"
    
    # Get the first hit
    hits = response['hits']['hits']
    assert len(hits) > 0, "No hits returned"
    
    document = hits[0]['_source']
    assert 'test_id' in document, "Document missing 'test_id' field"
    assert 'status' in document, "Document missing 'status' field"
    
    assert document['test_id'] == 'VAFT-004', f"Expected test_id='VAFT-004', got '{document['test_id']}'"
    assert document['status'] == 'pass', f"Expected status='pass', got '{document['status']}'"
    
    print(f"✓ Found document with test_id='VAFT-004' and status='pass'")
    print(f"  Document details: {document}")

def test_elasticsearch_all_records():
    """Test 4: Verify all three test records exist"""
    es = get_elasticsearch_client()
    es.indices.refresh(index="test-results")
    
    response = es.search(index="test-results", body={"query": {"match_all": {}}})
    
    total = response['hits']['total']
    if isinstance(total, dict):
        total_count = total['value']
    else:
        total_count = total
    
    assert total_count >= 3, f"Expected at least 3 documents, found {total_count}"
    print(f"✓ Verified {total_count} documents exist in index")

