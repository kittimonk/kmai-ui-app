
"""
Script to test Databricks connectivity directly
"""
import os
import json
from databricks_utils import test_connection, list_clusters, execute_sql_query

def print_json(data):
    """Helper function to pretty print JSON data"""
    print(json.dumps(data, indent=2))

def main():
    """Main function to test Databricks connectivity"""
    print("\n=== Testing Databricks Connectivity ===\n")
    
    # Check for environment variables
    workspace_url = os.environ.get("DATABRICKS_WORKSPACE_URL")
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")
    cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")
    
    # Print status of required environment variables
    print("Required Environment Variables:")
    print(f"  DATABRICKS_WORKSPACE_URL: {'✓ Set' if workspace_url else '✗ NOT SET'}")
    print(f"  AZURE_TENANT_ID: {'✓ Set' if tenant_id else '✗ NOT SET'}")
    print(f"  AZURE_CLIENT_ID: {'✓ Set' if client_id else '✗ NOT SET'}")
    print(f"  AZURE_CLIENT_SECRET: {'✓ Set' if client_secret else '✗ NOT SET (SENSITIVE)'}")
    print(f"  DATABRICKS_CLUSTER_ID: {'✓ Set' if cluster_id else '✗ NOT SET (Optional)'}")
    
    if not all([workspace_url, tenant_id, client_id, client_secret]):
        print("\n❌ ERROR: Missing required environment variables. Please set them before testing.")
        return
    
    print("\n1. Testing connection...")
    try:
        result = test_connection()
        print_json(result)
    except Exception as e:
        print(f"Error testing connection: {str(e)}")
    
    print("\n2. Listing clusters...")
    try:
        result = list_clusters()
        print_json(result)
    except Exception as e:
        print(f"Error listing clusters: {str(e)}")
    
    print("\n3. Testing SQL query...")
    try:
        result = execute_sql_query("SELECT 1 AS test")
        print_json(result)
    except Exception as e:
        print(f"Error executing SQL query: {str(e)}")
    
    print("\n=== Databricks Testing Complete ===")

if __name__ == "__main__":
    main()
