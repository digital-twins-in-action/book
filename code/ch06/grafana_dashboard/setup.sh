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
if [ -f "$MEMGRAPH_LOAD_SCRIPT" ]; then
    # Ensure dependencies for the script are met before running
    # You may need to run 'pip install -r requirements.txt' if your script has dependencies
    python "$MEMGRAPH_LOAD_SCRIPT"
    if [ $? -ne 0 ]; then
        echo "Error: Memgraph data loading failed."
        # Keep services running for inspection, but alert the user
        # exit 1 
    else
        echo "Memgraph data loading complete."
    fi
else
    echo "Warning: Memgraph load script '$MEMGRAPH_LOAD_SCRIPT' not found. Skipping data load."
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
# NOTE: This step assumes you have dynamodump installed and your data is ready to restore.
dynamodump -m restore -r local -s "$DYNAMODB_TABLE_NAME" --host "$DYNAMODUMP_HOST" --port "$DYNAMODB_PORT" --region "$DYNAMODB_REGION" --dataOnly
if [ $? -ne 0 ]; then
    echo "Error: DynamoDB data loading failed. Ensure 'dynamodump' is installed and data files are present."
else
    echo "DynamoDB data loading complete."
fi

echo "=========================================================="
echo "✨ SETUP COMPLETE! All services are running and data loaded."
echo "=========================================================="
echo "Memgraph UI (Lab): http://localhost:3000 (connects to Bolt on port 7687)"
echo "DynamoDB Local: http://localhost:8000 (accessible via AWS CLI/SDKs)"
echo "To stop all services: 'docker compose down'"