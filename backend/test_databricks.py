
"""
Script to test Databricks connectivity directly
"""
import os
import json
import time
from databricks_utils import (
    test_connection,
    list_clusters,
    ensure_cluster_running,
    list_dbfs_files,
    execute_sql_query,
    read_file_content,
    check_mount_status,
    check_adls_access,
    copy_data_between_adls,
    get_access_token
)

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
    use_cli_token = os.environ.get("USE_AZURE_CLI_TOKEN", "false").lower() == "true"
    
    # Print status of required environment variables
    print("Required Environment Variables:")
    print(f"  DATABRICKS_WORKSPACE_URL: {'✓ Set' if workspace_url else '✗ NOT SET'}")
    
    if use_cli_token:
        print("  Using Azure CLI Token for authentication")
    else:
        print(f"  AZURE_TENANT_ID: {'✓ Set' if tenant_id else '✗ NOT SET'}")
        print(f"  AZURE_CLIENT_ID: {'✓ Set' if client_id else '✗ NOT SET'}")
        print(f"  AZURE_CLIENT_SECRET: {'✓ Set' if client_secret else '✗ NOT SET (SENSITIVE)'}")
    
    print(f"  DATABRICKS_CLUSTER_ID: {'✓ Set' if cluster_id else '✗ NOT SET (Optional)'}")
    
    if use_cli_token and not workspace_url:
        print("\n❌ ERROR: Missing required environment variables. Please set them before testing.")
        return
    elif not use_cli_token and not all([workspace_url, tenant_id, client_id, client_secret]):
        print("\n❌ ERROR: Missing required environment variables. Please set them before testing.")
        return
    
    # If using CLI token, try to get a token
    if use_cli_token:
        print("\n0. Testing Azure CLI token generation...")
        try:
            token_info = get_access_token()
            print(f"✓ Successfully obtained token (expires: {token_info['expires_on']})")
            print(f"  Tenant ID: {token_info['tenant']}")
            print(f"  Subscription: {token_info['subscription']}")
        except Exception as e:
            print(f"Error getting token: {str(e)}")
    
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
    
    if cluster_id:
        print("\n3. Ensuring cluster is running...")
        try:
            result = ensure_cluster_running(cluster_id)
            print_json(result)
            
            # If the cluster is starting, wait a bit and check again
            if result.get("status") == "starting":
                print("\n   Waiting 30 seconds to check status again...")
                time.sleep(30)
                result = ensure_cluster_running(cluster_id)
                print_json(result)
        except Exception as e:
            print(f"Error ensuring cluster is running: {str(e)}")
    
        print("\n4. Testing SQL query...")
        try:
            result = execute_sql_query("SELECT 1 AS test")
            print_json(result)
        except Exception as e:
            print(f"Error executing SQL query: {str(e)}")
    
        print("\n5. Listing DBFS files in root...")
        try:
            files = list_dbfs_files("/")
            print_json(files[:10] if len(files) > 10 else files)  # Limit output for large directories
            print(f"Found {len(files)} files/directories at root level")
        except Exception as e:
            print(f"Error listing DBFS files: {str(e)}")
    
        print("\n6. Checking mount status...")
        try:
            result = check_mount_status("my_mount")
            print_json(result)
        except Exception as e:
            print(f"Error checking mount status: {str(e)}")
    
        print("\n7. Checking ADLS access...")
        try:
            result = check_adls_access("mystorageaccount", "mycontainer")
            print_json(result)
        except Exception as e:
            print(f"Error checking ADLS access: {str(e)}")
    
    print("\n=== Databricks Testing Complete ===")

if __name__ == "__main__":
    main()
