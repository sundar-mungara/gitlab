# Kubernetes and CI/CD Integration Tests

This project contains Kubernetes deployments and integration tests for MySQL, Elasticsearch, and Nginx services.

## Project Structure

```
.
├── Dockerfile                    # Custom devops-tools Docker image
├── .gitlab-ci.yml               # GitLab CI/CD pipeline configuration
├── requirements.txt             # Python dependencies
├── deployments/                 # Kubernetes manifests
│   ├── mysql-deployment.yaml
│   ├── mysql-init-job.yaml
│   ├── elasticsearch-deployment.yaml
│   ├── elasticsearch-init-job.yaml
│   └── nginx-deployment.yaml
└── tests/                       # Pytest test scripts
    ├── __init__.py
    ├── conftest.py
    ├── test_mysql.py
    ├── test_elasticsearch.py
    └── test_nginx.py
```

## Prerequisites

### Environment Variables (GitLab CI/CD Variables)

The following environment variables must be configured in GitLab CI/CD settings:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `VAULT_ADDR`
- `VAULT_TOKEN`

### Docker Image Setup

Build the `devops-tools` Docker image on your EC2 instance:

```bash
docker build -t devops-tools .
```

Verify the image:

```bash
docker run --rm devops-tools aws --version
docker run --rm devops-tools vault version
docker run --rm devops-tools kubectl version --client
docker run --rm devops-tools python3 --version
docker run --rm devops-tools pytest --version
```

## GitLab Runner Setup

Ensure your GitLab Runner is configured with the `data-core` tag and can use the `devops-tools` image.

## Pipeline Stages

### 1. Deploy Stage

- Creates `test-namespace` namespace
- Deploys MySQL, Elasticsearch, and Nginx
- Waits for all pods to be ready
- Runs initialization jobs:
  - MySQL: Creates database, table, and inserts test record
  - Elasticsearch: Creates index and inserts test documents

### 2. Test Stage

- Runs pytest tests to validate all deployments:
  - **MySQL Test**: Connects via NodePort, queries test record
  - **Elasticsearch Test**: Queries for test_id="VAFT-004" and verifies status="pass"
  - **Nginx Test**: Fetches default page and verifies "Welcome to nginx" text

## Test Details

### Test 1: MySQL Database

- **Deployment**: MySQL 8.0 with emptyDir volume
- **Service**: NodePort on port 30306
- **Database**: `testdb`
- **Table**: `results` with columns:
  - `id` (INT AUTO_INCREMENT PRIMARY KEY)
  - `test_id` (VARCHAR(50))
  - `status` (VARCHAR(10))
  - `executed_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- **Test Record**: test_id='TEST-001', status='pass'

### Test 2: Elasticsearch

- **Deployment**: Elasticsearch 8.11.0 with security disabled
- **Service**: NodePort on port 30200
- **Index**: `test-results` with mapping for:
  - `test_id` (keyword)
  - `name` (text)
  - `status` (keyword)
  - `duration_ms` (integer)
  - `timestamp` (date)
- **Test Documents**: 3 records including VAFT-004 with status="pass"

### Test 3: Nginx Web Server

- **Deployment**: Latest Nginx image
- **Service**: NodePort on port 30080
- **Test**: Verifies default welcome page contains "Welcome to nginx"

## Running Tests Locally

1. Ensure kubectl is configured and pointing to your cluster
2. Deploy the resources:
   ```bash
   kubectl apply -f deployments/mysql-deployment.yaml
   kubectl apply -f deployments/elasticsearch-deployment.yaml
   kubectl apply -f deployments/nginx-deployment.yaml
   kubectl apply -f deployments/mysql-init-job.yaml
   kubectl apply -f deployments/elasticsearch-init-job.yaml
   ```

3. Get the node IP:
   ```bash
   export KUBERNETES_NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
   export MYSQL_NODE_IP=$KUBERNETES_NODE_IP
   export ES_NODE_IP=$KUBERNETES_NODE_IP
   export NGINX_NODE_IP=$KUBERNETES_NODE_IP
   ```

4. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

5. Run tests:
   ```bash
   pytest tests/ -v
   ```

## Troubleshooting

### Pods not starting
- Check resource limits and node capacity
- Verify images are accessible
- Check pod logs: `kubectl logs <pod-name> -n test-namespace`

### Tests failing to connect
- Verify NodePort services are accessible
- Check firewall rules for NodePort ports (30306, 30200, 30080)
- Ensure node IP is correctly set

### Initialization jobs failing
- Check job logs: `kubectl logs job/<job-name> -n test-namespace`
- Verify dependent services are ready before running jobs

## Cleanup

To remove all resources:

```bash
kubectl delete namespace test-namespace
```

