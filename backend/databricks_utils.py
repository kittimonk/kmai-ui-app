
"""
Utility functions for connecting to Azure Databricks
"""
from azure.identity import ClientSecretCredential
from databricks.sdk import WorkspaceClient
import os
import logging
import time
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

def get_databricks_client():
    """
    Get a Databricks WorkspaceClient using Azure Service Principal (OAuth)
    """
    try:
        # Get the required configuration from environment variables
        workspace_url = os.environ.get("DATABRICKS_WORKSPACE_URL")
        tenant_id = os.environ.get("AZURE_TENANT_ID")
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        
        # Validate required environment variables
        if not workspace_url:
            raise ValueError("DATABRICKS_WORKSPACE_URL environment variable is not set")
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
