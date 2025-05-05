
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
    cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")
    
    if not workspace_url:
        print("WARNING: DATABRICKS_WORKSPACE_URL environment variable is not set!")
    else:
        print(f"Using Databricks workspace: {workspace_url}")
    
    if not cluster_id:
        print("NOTE: DATABRICKS_CLUSTER_ID environment variable is not set (optional for some operations)")
    else:
        print(f"Using Databricks cluster ID: {cluster_id}")
    
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
