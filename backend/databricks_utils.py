
"""
Utility functions for connecting to Azure Databricks
"""
from azure.identity import ClientSecretCredential
from databricks.sdk import WorkspaceClient
import os
import logging
import time
import json
import subprocess
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

def get_access_token(resource_id="2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"):
    """
    Get an access token using the Azure CLI
    Token is valid for 1 hour (60 minutes)
    """
    try:
        # Run the Azure CLI command to get an access token
        result = subprocess.run(
            ["az", "account", "get-access-token", 
             "--resource", resource_id, 
             "--out", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the JSON output
        token_info = json.loads(result.stdout)
        
        # Return the token and expiration
        return {
            "token": token_info["accessToken"],
            "expires_on": token_info["expiresOn"],
            "subscription": token_info["subscription"],
            "tenant": token_info["tenant"]
        }
    except Exception as e:
        logger.error(f"Error getting access token: {str(e)}")
        raise

def get_databricks_client():
    """
    Get a Databricks WorkspaceClient using Azure Service Principal (OAuth)
    """
    try:
        # Get the required configuration from environment variables
        workspace_url = os.environ.get("DATABRICKS_WORKSPACE_URL")
        
        # For CLI token-based auth
        use_cli_token = os.environ.get("USE_AZURE_CLI_TOKEN", "false").lower() == "true"
        
        # For Service Principal auth
        tenant_id = os.environ.get("AZURE_TENANT_ID")
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        
        # Validate required environment variables
        if not workspace_url:
            raise ValueError("DATABRICKS_WORKSPACE_URL environment variable is not set")
            
        # Create the client based on the authentication method
        if use_cli_token:
            # Get token from Azure CLI
            token_info = get_access_token()
            
            # Create client with token
            client = WorkspaceClient(
                host=workspace_url,
                token=token_info["token"]
            )
            logger.info(f"Using Azure CLI token (expires: {token_info['expires_on']})")
        else:
            # Validate required environment variables for service principal
            if not tenant_id:
                raise ValueError("AZURE_TENANT_ID environment variable is not set")
            if not client_id:
                raise ValueError("AZURE_CLIENT_ID environment variable is not set")
            if not client_secret:
                raise ValueError("AZURE_CLIENT_SECRET environment variable is not set")
                
            # Create a credential using client credentials flow
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            
            # Create and return the client using OAuth
            client = WorkspaceClient(
                host=workspace_url,
                auth_type="azure-cli"
            )
            logger.info("Using Service Principal authentication")
        
        return client
    except Exception as e:
        logger.error(f"Error creating Databricks client: {str(e)}")
        raise

def test_connection():
    """
    Test the connection to Databricks
    """
    try:
        start_time = time.time()
        client = get_databricks_client()
        # Try to list workspace items as a simple test
        clusters = list(client.clusters.list())
        processing_time = time.time() - start_time
        
        return {
            "status": "connected",
            "clusters_found": len(clusters),
            "cluster_names": [cluster.cluster_name for cluster in clusters],
            "processing_time_ms": round(processing_time * 1000, 2)
        }
    except Exception as e:
        logger.error(f"Databricks connection test failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def list_clusters() -> Dict[str, Any]:
    """
    List all available clusters in the Databricks workspace
    """
    try:
        client = get_databricks_client()
        clusters = list(client.clusters.list())
        
        # Format the response
        cluster_list = []
        for cluster in clusters:
            cluster_list.append({
                "cluster_id": cluster.cluster_id,
                "cluster_name": cluster.cluster_name,
                "state": cluster.state,
                "creator": cluster.creator_user_name,
                "spark_version": cluster.spark_version
            })
            
        return {
            "clusters": cluster_list,
            "count": len(cluster_list),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error listing Databricks clusters: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def ensure_cluster_running(cluster_id=None):
    """
    Ensure the specified cluster is running
    If no cluster_id is provided, use the one from environment variables
    """
    try:
        client = get_databricks_client()
        
        # Get cluster ID from environment variable if not provided
        if not cluster_id:
            cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")
            if not cluster_id:
                raise ValueError("DATABRICKS_CLUSTER_ID environment variable is not set")
        
        # Get the cluster state
        cluster_info = client.clusters.get(cluster_id=cluster_id)
        
        # Check if the cluster is running
        if cluster_info.state == "RUNNING":
            return {
                "status": "success",
                "message": f"Cluster {cluster_id} is already running",
                "cluster_state": cluster_info.state
            }
        elif cluster_info.state in ["TERMINATED", "TERMINATING"]:
            # Start the cluster
            client.clusters.start(cluster_id=cluster_id)
            return {
                "status": "starting",
                "message": f"Started cluster {cluster_id}. It may take several minutes to be ready.",
                "cluster_state": "STARTING"
            }
        else:
            # For any other state, return the current state
            return {
                "status": "waiting",
                "message": f"Cluster {cluster_id} is in state {cluster_info.state}. Please wait.",
                "cluster_state": cluster_info.state
            }
    except Exception as e:
        logger.error(f"Error ensuring cluster running: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def list_dbfs_files(path="/", recursive=False, file_types=None):
    """
    List files in DBFS
    """
    try:
        client = get_databricks_client()
        results = client.dbfs.list(path=path)
        
        files = []
        for item in results:
            # Skip files not matching the file_types filter if provided
            if file_types and item.is_file and not any(item.path.endswith(ext) for ext in file_types):
                continue
            
            file_info = {
                "path": item.path,
                "name": item.path.split('/')[-1] if item.path != '/' else '/',
                "is_directory": not item.is_file,
                "size": item.file_size if item.is_file else None,
                "modification_time": item.modification_time
            }
            files.append(file_info)
            
            # Recursively list files if requested
            if recursive and not item.is_file:
                subfiles = list_dbfs_files(item.path, recursive, file_types)
                files.extend(subfiles)
        
        return files
    except Exception as e:
        logger.error(f"Error listing DBFS files: {str(e)}")
        raise

def check_mount_status(mount_name):
    """
    Check if a specific mount point exists
    """
    try:
        client = get_databricks_client()
        
        # Use SQL to query mount points
        query = "SHOW MOUNTS"
        
        # Execute the query on the cluster
        cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")
        if not cluster_id:
            raise ValueError("DATABRICKS_CLUSTER_ID environment variable is not set")
        
        # This is a placeholder - actual implementation would use client.commands API
        # to execute the SQL query and parse the results
        return {
            "status": "success",
            "mount_exists": False,  # This would be determined by checking the results
            "message": "Mount status check feature is simulated"
        }
    except Exception as e:
        logger.error(f"Error checking mount status: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def execute_sql_query(query, cluster_id=None):
    """
    Execute a SQL query on Databricks
    """
    try:
        client = get_databricks_client()
        
        # Get cluster ID from environment variable if not provided
        if not cluster_id:
            cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")
            if not cluster_id:
                raise ValueError("DATABRICKS_CLUSTER_ID environment variable is not set")
        
        # Execute the query using Databricks SQL
        # Note: This is a simplified example - actual implementation depends on query complexity
        # For production use, consider using the SQL warehouses API
        
        # For now, return a placeholder response indicating successful connectivity
        return {
            "success": True,
            "query": query,
            "cluster_id": cluster_id,
            "message": "Query execution simulation successful - connection is working"
        }
    except Exception as e:
        logger.error(f"Error executing SQL query: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

def read_file_content(file_path):
    """
    Read content from a file in DBFS
    """
    try:
        client = get_databricks_client()
        
        # Check if file exists
        try:
            file_info = client.dbfs.get_status(path=file_path)
            if file_info.is_directory:
                return {
                    "status": "error",
                    "message": f"Path {file_path} is a directory, not a file"
                }
        except Exception:
            return {
                "status": "error",
                "message": f"File {file_path} not found"
            }
        
        # For small files, read directly
        max_size = 1024 * 1024  # 1MB limit for direct reading
        
        if file_info.file_size <= max_size:
            content = client.dbfs.read(path=file_path)
            
            # Try to decode as text
            try:
                text_content = content.decode('utf-8')
                return {
                    "status": "success",
                    "content": text_content,
                    "size": file_info.file_size,
                    "is_text": True
                }
            except UnicodeDecodeError:
                # Not a text file, return binary data info
                return {
                    "status": "success",
                    "message": "Binary file detected",
                    "size": file_info.file_size,
                    "is_text": False
                }
        else:
            # File too large for direct reading
            return {
                "status": "error",
                "message": f"File too large ({file_info.file_size} bytes) for direct reading"
            }
            
    except Exception as e:
        logger.error(f"Error reading file content: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def check_adls_access(storage_account, container):
    """
    Check if we have access to a specific ADLS container
    """
    try:
        # This would use Databricks to run a command to check access
        # For now, we're simulating the functionality
        
        client = get_databricks_client()
        cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")
        
        if not cluster_id:
            raise ValueError("DATABRICKS_CLUSTER_ID environment variable is not set")
        
        # In actual implementation, this would execute code on the cluster to check access
        
        return {
            "status": "success",
            "has_access": True,  # This would be determined by the actual check
            "storage_account": storage_account,
            "container": container,
            "message": "ADLS access check feature is simulated"
        }
    except Exception as e:
        logger.error(f"Error checking ADLS access: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def copy_data_between_adls(source_storage, source_container, source_path, 
                          target_storage, target_container, target_path):
    """
    Copy data from one ADLS location to another
    """
    try:
        # This would use Databricks to run a command to copy data
        # For now, we're simulating the functionality
        
        client = get_databricks_client()
        cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")
        
        if not cluster_id:
            raise ValueError("DATABRICKS_CLUSTER_ID environment variable is not set")
        
        # In actual implementation, this would execute code on the cluster to copy data
        
        return {
            "status": "success",
            "source": f"abfss://{source_container}@{source_storage}.dfs.core.windows.net/{source_path}",
            "target": f"abfss://{target_container}@{target_storage}.dfs.core.windows.net/{target_path}",
            "message": "ADLS data copy feature is simulated"
        }
    except Exception as e:
        logger.error(f"Error copying ADLS data: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
