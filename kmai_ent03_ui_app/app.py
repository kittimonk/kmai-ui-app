
import asyncio
import os, subprocess, time
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from pydantic import BaseModel
import requests
import httpx
import openai
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Request, Form, FastAPI, HTTPException, UploadFile, File, Depends, Header
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import re
import json
import uuid
from striprtf.striprtf import rtf_to_text
from pathlib import Path
import time

# Import our database module
from backend.database import (
    initialize_chat_history_table, 
    initialize_feature_interaction_table,
    log_chat_interaction, 
    log_feature_interaction,
    get_user_chat_history,
    get_user_feature_history
)

# Azure Configuration
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "210da3-aff")
client_id = os.environ.get("CLIENT_ID", "7abbd-acdc17")
object_id = os.environ.get("OBJECT_ID", "644106-4d8a")
openai_resource_group_name = os.environ.get("OPENAI_RESOURCE_GROUP", "nt03-eastus-km-openai-900")
openai_account_name = os.environ.get("OPENAI_ACCOUNT_NAME", "nt03-eastus-km-openai-900")
openai_api_version = os.environ.get("OPENAI_API_VERSION", "2024-10-21")
openai_embedding_model = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
openai_lang_model = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-2024-05-13-tpm")

search_service = "https://nt03-eastus-km-search-9893.search.windows.net"
search_index_name = "gptentern01index"
msi = DefaultAzureCredential()

# Initialize FastAPI
app = FastAPI()

# Configure CORS more explicitly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you'd want to be more specific
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Function to get token for OpenAI
def get_bearer_token_provider(credential, scope):
    def get_token():
        token = credential.get_token(scope)
        return token.token
    return get_token

# Initialize OpenAI client with token provider
client = AzureOpenAI(
    azure_endpoint=f"https://{openai_account_name}.openai.azure.com",
    api_version=openai_api_version,
    azure_ad_token_provider=get_bearer_token_provider(msi, "https://cognitiveservices.azure.com/.default")
)

# Initialize search client
search_client = SearchClient(
    endpoint=search_service,
    index_name=search_index_name,
    credential=msi,
)

# ... keep existing code (Request Models, Utility Functions, Database Initialization, User ID extraction)

# ... keep existing code (Health Check Endpoints)

# ... keep existing code (API Access configuration)

# ... keep existing code (History Endpoints)

# ... keep existing code (Chat Endpoints)

# ... keep existing code (Code Converter Endpoint)

# ... keep existing code (Code Explainer Endpoint)

# ... keep existing code (Knowledge Base Endpoint)

# ... keep existing code (Archer / Remediation Endpoints)

#Determine the static directory path
static_dir = Path(__file__).parent / "static"
#Mount static files - only if directory exists
if static_dir.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    print(f"Static files mounted from: {static_dir}")
else:
    print("WARNING: Could not mount static files - directory doesn\'t exist")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
