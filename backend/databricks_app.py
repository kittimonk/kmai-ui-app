
"""
Standalone FastAPI application for testing Databricks connectivity
"""
from fastapi import FastAPI, HTTPException, Query, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import os

# Import Databricks utilities
from databricks_utils import (
    test_connection, 
    execute_sql_query, 
    list_clusters,
    ensure_cluster_running,
    list_dbfs_files,
    read_file_content,
    check_mount_status,
    check_adls_access,
    copy_data_between_adls
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Databricks Connectivity Tester",
    description="Standalone API for testing Azure Databricks connectivity",
    version="0.1.0"
)

# Configure CORS for browser-based testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request model for SQL queries
class SQLQueryRequest(BaseModel):
    query: str
    cluster_id: Optional[str] = None

# Request model for ADLS access check
class ADLSAccessRequest(BaseModel):
    storage_account: str
    container: str

# Request model for ADLS data copy
class ADLSCopyRequest(BaseModel):
    source_storage: str
    source_container: str
    source_path: str
    target_storage: str
    target_container: str
    target_path: str

# ----------------------------
# API ENDPOINTS
# ----------------------------
@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "app": "Databricks Connectivity Tester",
        "status": "running",
        "endpoints": [
            {"method": "GET", "path": "/health", "description": "Health check endpoint"},
            {"method": "GET", "path": "/test", "description": "Test Databricks connectivity"},
            {"method": "GET", "path": "/clusters", "description": "List available Databricks clusters"},
            {"method": "GET", "path": "/cluster/{cluster_id}/ensure-running", "description": "Ensure cluster is running"},
            {"method": "GET", "path": "/dbfs/list", "description": "List files in DBFS"},
            {"method": "GET", "path": "/dbfs/read", "description": "Read file content from DBFS"},
            {"method": "GET", "path": "/mounts/check", "description": "Check mount status"},
            {"method": "POST", "path": "/adls/check-access", "description": "Check ADLS access"},
            {"method": "POST", "path": "/adls/copy", "description": "Copy data between ADLS locations"},
            {"method": "POST", "path": "/query", "description": "Execute SQL query on Databricks"}
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "databricks-connector"
    }

@app.get("/test")
async def test_databricks_connection():
    """Test endpoint to verify connection to Azure Databricks"""
    try:
        logger.info("Testing Databricks connection...")
        result = test_connection()
        logger.info(f"Connection test result: {result}")
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result
            )
        return result
    except Exception as e:
        logger.error(f"Databricks connection test failed with exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

@app.get("/clusters")
async def list_databricks_clusters():
    """List all available clusters in Databricks workspace"""
    try:
        logger.info("Fetching Databricks clusters...")
        result = list_clusters()
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result
            )
        return result
    except Exception as e:
        logger.error(f"Failed to list Databricks clusters: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

@app.get("/cluster/{cluster_id}/ensure-running")
async def ensure_cluster_is_running(cluster_id: str):
    """Ensure the specified cluster is running"""
    try:
        logger.info(f"Ensuring cluster {cluster_id} is running...")
        result = ensure_cluster_running(cluster_id)
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result
            )
        return result
    except Exception as e:
        logger.error(f"Failed to ensure cluster is running: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

@app.get("/dbfs/list")
async def list_dbfs_directory(
    path: str = "/",
    recursive: bool = False,
    file_types: Optional[str] = None
):
    """List files in DBFS"""
    try:
        logger.info(f"Listing DBFS directory: {path}")
        file_type_list = file_types.split(",") if file_types else None
        result = list_dbfs_files(path, recursive, file_type_list)
        return {
            "status": "success",
            "path": path,
            "files": result
        }
    except Exception as e:
        logger.error(f"Failed to list DBFS files: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

@app.get("/dbfs/read")
async def read_dbfs_file(path: str):
    """Read file content from DBFS"""
    try:
        logger.info(f"Reading file: {path}")
        result = read_file_content(path)
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result
            )
        return result
    except Exception as e:
        logger.error(f"Failed to read file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

@app.get("/mounts/check")
async def check_databricks_mount(mount_name: str):
    """Check if a mount exists"""
    try:
        logger.info(f"Checking mount status for: {mount_name}")
        result = check_mount_status(mount_name)
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result
            )
        return result
    except Exception as e:
        logger.error(f"Failed to check mount status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

@app.post("/adls/check-access")
async def check_adls_container_access(request: ADLSAccessRequest):
    """Check if we have access to an ADLS container"""
    try:
        logger.info(f"Checking ADLS access for: {request.storage_account}/{request.container}")
        result = check_adls_access(request.storage_account, request.container)
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result
            )
        return result
    except Exception as e:
        logger.error(f"Failed to check ADLS access: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

@app.post("/adls/copy")
async def copy_adls_data(request: ADLSCopyRequest):
    """Copy data between ADLS locations"""
    try:
        logger.info(f"Copying data from {request.source_storage}/{request.source_container} to {request.target_storage}/{request.target_container}")
        result = copy_data_between_adls(
            request.source_storage,
            request.source_container,
            request.source_path,
            request.target_storage,
            request.target_container,
            request.target_path
        )
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result
            )
        return result
    except Exception as e:
        logger.error(f"Failed to copy ADLS data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

@app.post("/query")
async def execute_query(request: SQLQueryRequest):
    """Execute a SQL query on Databricks"""
    try:
        logger.info(f"Executing SQL query: {request.query}")
        result = execute_sql_query(request.query, request.cluster_id)
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result
            )
        return result
    except Exception as e:
        logger.error(f"Failed to execute SQL query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )

# Start the application if running directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))  # Use a different port from main app
    uvicorn.run("databricks_app:app", host="0.0.0.0", port=port)
