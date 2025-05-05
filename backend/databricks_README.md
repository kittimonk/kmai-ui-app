
# Databricks Connectivity Testing

This module provides utilities and tools for testing connectivity to Azure Databricks.

## Prerequisites

- Python 3.7+
- Azure account with Databricks workspace
- Proper permissions for Azure Databricks access

## Environment Variables

Set the following environment variables:

```bash
export DATABRICKS_WORKSPACE_URL="https://your-workspace.azuredatabricks.net"
export DATABRICKS_CLUSTER_ID="your-cluster-id"  # Optional, only needed for some operations
```

## Testing Options

### Option 1: Direct Script Testing

Run the Python test script directly:

```bash
cd backend
python test_databricks.py
```

### Option 2: API Testing with FastAPI

Start the standalone FastAPI application:

```bash
cd backend
uvicorn databricks_app:app --reload
```

Then test the API endpoints:

1. **Browser Testing**: Open `http://localhost:8000` in your browser to see available endpoints
2. **Command-line Testing**:

```bash
# Test connection
curl http://localhost:8000/test

# List clusters
curl http://localhost:8000/clusters

# Execute SQL query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT 1 AS test"}'
```

## Troubleshooting

If you encounter issues:

1. Check that the environment variables are set correctly
2. Verify that your Azure credentials are valid and have proper permissions
3. Check that your Databricks workspace is accessible
4. Ensure your cluster is running if you're trying to execute SQL queries
5. Check for network connectivity issues or firewalls

## Integration

Once you've verified that the Databricks connection works, you can integrate the functionality into your main application.
