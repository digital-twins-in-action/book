#!/bin/bash

# --- Configuration ---
MEMGRAPH_PORT=7687
DYNAMODB_PORT=8000
DYNAMODB_REGION="us-east-1"
DYNAMODB_ENDPOINT="http://localhost:${DYNAMODB_PORT}"
DYNAMODB_TABLE_NAME="sensor-data"
MEMGRAPH_LOAD_SCRIPT="../../ch05/load_home_kg.py"
DYNAMODUMP_HOST="127.0.0.1"

# Function to check if a port is open
wait_for_port() {
  local port=$1
  local service_name=$2
  local count=0
  echo "Waiting for ${service_name} on port ${port}..."
  
  # Wait for a maximum of 30 seconds
  while ! nc -z localhost ${port} >/dev/null 2>&1; do
    sleep 1
    count=$((count+1))
    if [ $count -ge 30 ]; then
      echo "Error: ${service_name} failed to start after 30 seconds."
      exit 1
    fi
  done
  echo "${service_name} is running!"
}


# --- Step 1: Wait for Services to be Ready ---
wait_for_port $MEMGRAPH_PORT "Memgraph"
wait_for_port $DYNAMODB_PORT "DynamoDB Local"


# --- Step 2: Load Data to Memgraph ---
echo "--- 2. Loading data to Memgraph using ${MEMGRAPH_LOAD_SCRIPT} ---"
MEMGRAPH_LOAD_FAILED=false
if [ -f "$MEMGRAPH_LOAD_SCRIPT" ]; then
    # Ensure dependencies for the script are met before running
    # You may need to run 'pip install -r requirements.txt' if your script has dependencies
    python "$MEMGRAPH_LOAD_SCRIPT"
    if [ $? -ne 0 ]; then
        echo "Error: Memgraph data loading failed."
        MEMGRAPH_LOAD_FAILED=true
    else
        echo "Memgraph data loading complete."
    fi
else
    echo "Warning: Memgraph load script '$MEMGRAPH_LOAD_SCRIPT' not found. Skipping data load."
    MEMGRAPH_LOAD_FAILED=true
fi


# --- Step 3: Create DynamoDB Table ---
echo "--- 3. Creating DynamoDB table: $DYNAMODB_TABLE_NAME ---"
# Check if the table already exists to avoid errors
if aws dynamodb describe-table --table-name "$DYNAMODB_TABLE_NAME" --endpoint-url "$DYNAMODB_ENDPOINT" --region "$DYNAMODB_REGION" 2>/dev/null; then
    echo "Table '$DYNAMODB_TABLE_NAME' already exists. Skipping creation."
else
    aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE_NAME" \
        --attribute-definitions AttributeName=partKey,AttributeType=S AttributeName=sortKey,AttributeType=N \
        --key-schema AttributeName=partKey,KeyType=HASH AttributeName=sortKey,KeyType=RANGE \
        --billing-mode PAY_PER_REQUEST \
        --endpoint-url "$DYNAMODB_ENDPOINT" \
        --region "$DYNAMODB_REGION"
    
    if [ $? -ne 0 ]; then
        echo "Error: DynamoDB table creation failed."
    else
        echo "DynamoDB table '$DYNAMODB_TABLE_NAME' created successfully."
        
        # Wait for table to become active before loading data
        echo "Waiting for DynamoDB table to become active..."
        aws dynamodb wait table-exists --table-name "$DYNAMODB_TABLE_NAME" --endpoint-url "$DYNAMODB_ENDPOINT" --region "$DYNAMODB_REGION"
        echo "DynamoDB table is active."
    fi
fi


# --- Step 4: Load Data to DynamoDB Table ---
echo "--- 4. Loading data to DynamoDB table: $DYNAMODB_TABLE_NAME ---"

DYNAMODB_LOAD_FAILED=false
# Check if dynamodump is installed
if ! command -v dynamodump &> /dev/null; then
    echo "Error: 'dynamodump' is not installed or not in PATH."
    echo "Install it with: pip install dynamodump"
    echo "(Make sure your virtual environment is activated before running this script)"
    DYNAMODB_LOAD_FAILED=true
else
    dynamodump -m restore -r local -s "$DYNAMODB_TABLE_NAME" --host "$DYNAMODUMP_HOST" --port "$DYNAMODB_PORT" --region "$DYNAMODB_REGION" --dataOnly
    if [ $? -ne 0 ]; then
        echo "Error: DynamoDB data loading failed. Check that data files are present in ./sensor-data/"
        DYNAMODB_LOAD_FAILED=true
    else
        echo "DynamoDB data loading complete."
    fi
fi

# --- Summary ---
echo "=========================================================="
echo "Services:"
nc -z localhost $MEMGRAPH_PORT 2>/dev/null && echo "  ✓ Memgraph running on port $MEMGRAPH_PORT" || echo "  ✗ Memgraph NOT running"
nc -z localhost $DYNAMODB_PORT 2>/dev/null && echo "  ✓ DynamoDB Local running on port $DYNAMODB_PORT" || echo "  ✗ DynamoDB Local NOT running"
nc -z localhost 3000 2>/dev/null && echo "  ✓ Grafana running on port 3000" || echo "  ✗ Grafana NOT running"
echo ""
echo "Data loading:"
[ "$MEMGRAPH_LOAD_FAILED" = true ] && echo "  ✗ Memgraph data load FAILED" || echo "  ✓ Memgraph data loaded"
[ "$DYNAMODB_LOAD_FAILED" = true ] && echo "  ✗ DynamoDB data load FAILED" || echo "  ✓ DynamoDB data loaded"
echo "=========================================================="
echo "Grafana:        http://localhost:3000 (default login: admin/admin)"
echo "Memgraph:       bolt://localhost:7687 (use mgconsole or Python client)"
echo "DynamoDB Local: http://localhost:8000 (accessible via AWS CLI/SDKs)"
echo ""
echo "To query Memgraph: docker exec -it memgraph mgconsole"
echo "To stop all services: docker compose down"