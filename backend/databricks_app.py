
"""
Standalone FastAPI application for testing Databricks connectivity
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import os

# Import Databricks utilities
from databricks_utils import test_connection, execute_sql_query, list_clusters

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
            return HTTPException(
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
            return HTTPException(
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

@app.post("/query")
async def execute_query(request: SQLQueryRequest):
    """Execute a SQL query on Databricks"""
    try:
        logger.info(f"Executing SQL query: {request.query}")
        result = execute_sql_query(request.query, request.cluster_id)
        if not result.get("success"):
            return HTTPException(
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
