import pytest
import os
import subprocess
import time

def get_node_ip():
    """Get the Kubernetes node IP address"""
    try:
        result = subprocess.run(
            ['kubectl', 'get', 'nodes', '-o', 'jsonpath={.items[0].status.addresses[?(@.type=="InternalIP")].address}'],
            capture_output=True,
            text=True,
            check=True
        )
        node_ip = result.stdout.strip()
        if node_ip:
            return node_ip
    except Exception as e:
        print(f"Warning: Could not get node IP: {e}")
    
    # Fallback to environment variable or localhost
    return os.getenv('KUBERNETES_NODE_IP', 'localhost')

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Setup environment variables for tests"""
    node_ip = get_node_ip()
    print(f"Using Kubernetes node IP: {node_ip}")
    
    # Set environment variables for all tests
    os.environ['MYSQL_NODE_IP'] = node_ip
    os.environ['ES_NODE_IP'] = node_ip
    os.environ['NGINX_NODE_IP'] = node_ip
    
    yield
    
    # Cleanup if needed
    pass

