import pytest
import requests
import os
import time

# Configuration
NGINX_HOST = os.getenv('NGINX_NODE_IP', 'localhost')
NGINX_PORT = int(os.getenv('NGINX_NODE_PORT', '30080'))
NGINX_URL = f"http://{NGINX_HOST}:{NGINX_PORT}"

def get_nginx_response():
    """Get Nginx response with retry logic"""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(NGINX_URL, timeout=5)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise

def test_nginx_connection():
    """Test 1: Connect to Nginx using NodePort"""
    response = get_nginx_response()
    assert response.status_code == 200
    print("✓ Successfully connected to Nginx")

def test_nginx_welcome_message():
    """Test 2: Fetch default HTML page and verify it contains 'Welcome to nginx'"""
    response = get_nginx_response()
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    content = response.text
    assert 'Welcome to nginx' in content, f"Expected 'Welcome to nginx' in response, got: {content[:200]}"
    
    print("✓ Nginx welcome message verified")
    print(f"  Response preview: {content[:100]}...")

def test_nginx_content_type():
    """Test 3: Verify content type is HTML"""
    response = get_nginx_response()
    
    content_type = response.headers.get('Content-Type', '')
    assert 'text/html' in content_type, f"Expected 'text/html' in Content-Type, got '{content_type}'"
    
    print(f"✓ Content-Type verified: {content_type}")

