import asyncio
import os, subprocess, time
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential, get_bearer_token_provider
from azure.storage.blob import BlobServiceClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.search.documents.indexes.models import SimpleField
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
from fastapi.responses import JSONResponse, RedirectResponse
from typing import List, Dict, Optional
import re
import json
import uuid
from striprtf.striprtf import rtf_to_text
from pathlib import Path
import time
import sys
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import secrets
from vault import VaultConfig, VaultService
import logging

# Enable debug logging for authlib
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app_new.log"), # Save logs to app_new.log
        logging.StreamHandler(), # Also print logs to console
    ],
)
logger = logging.getLogger("authlib")

# Add the parent directory to sys.path to make backend importable
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database functions removed - using mock implementations

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
search_index_name = "gptenterprise03index"
msi = DefaultAzureCredential()

# Vault configuration
config = VaultConfig()
vault_service = VaultService(config)
current_environment = os.getenv("ENV", "test")
malcode = os.getenv("MALCODE", "mail")
if current_environment in ["local", "test"]:
    application = "nt03-eastus-as-km-tkm01-02"
    parts = application.split("-")
    if parts[3].lower() == "kmai":
        path = os.getenv(f"VAULT_{parts[4].upper()}_PATH", "") + os.getenv(
            "RELATIVEPATH", "/grc"
        )
    else:
        path = os.getenv(f"VAULT_{malcode.upper()}_PATH", "") + os.getenv(
            "RELATIVEPATH", "/grc"
        )

OIDC_CLIENT_ID = "20e08190-785c841eb1c9"
OIDC_CLIENT_SECRET = "e3qqGuCFd1HDjwHC4TiYhHt"
OIDC_AUTHORITY = "https://fedsit.rastest.ca"

# Use consistent callback URL for PingFed configuration
def get_callback_url(request: Request) -> str:
    """Generate callback URL - always use configured custom domain for production"""
    host = request.headers.get("host", "localhost:8000")
    
    # For production deployments, always use the custom domain configured in PingFed
    if "azurewebsites.net" in host or "kme03.dev.com" in host:
        return "https://kme03.dev.com/sso"
    else:
        # For local development
        return "http://localhost:8000/sso"

# OAuth configuration
oauth = OAuth()
oauth.register(
    name="oidc",
    client_id=OIDC_CLIENT_ID,
    client_secret=OIDC_CLIENT_SECRET,
    server_metadata_url=f"{OIDC_AUTHORITY}/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid DD_Custom_memberOf",
    },
)

# Initialize FastAPI app
app = FastAPI(debug=True)

# Add SessionMiddleware
SESSION_SECRET = os.getenv("SESSION_SECRET", secrets.token_hex(32))
print(f"Starting app with session secret key length: {len(secure_random_key)}")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    max_age=14 * 24 * 3600,
    https_only=True,  # Set to False for development/http, True for production/https
    same_site="None"
)

# Session middleware to check authentication for API endpoints only
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # Allow all static files and UI routes to pass through
    if (request.url.path.startswith("/static") or 
        request.url.path.startswith("/assets") or
        request.url.path.startswith("/dist") or
        request.url.path in ["/", "/logout", "/sso", "/health", "/api/health", "/protected"] or
        request.url.path.startswith("/api/auth") or
        request.url.path.startswith("/auth/") or
        request.url.path.startswith("/sso") or
        request.url.path.endswith(".js") or
        request.url.path.endswith(".css") or
        request.url.path.endswith(".ico") or
        request.url.path.endswith(".png") or
        request.url.path.endswith(".svg") or
        request.url.path.endswith(".html") or
        request.url.path.startswith("/docs") or
        request.url.path.startswith("/openapi")):
        response = await call_next(request)
        return response
    
    # Only check authentication for API endpoints (chat, converter, etc.)
    if (request.url.path.startswith("/chat") or
        request.url.path.startswith("/converter") or 
        request.url.path.startswith("/explainer") or
        request.url.path.startswith("/remediation") or
        request.url.path.startswith("/ingestion") or
        request.url.path.startswith("/knowledge")):
        
        user = request.session.get("user")
        if not user:
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
    
    response = await call_next(request)
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize OpenAI client with token provider
client = openai.AsyncAzureOpenAI(
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

# Function to get token for OpenAI
def get_bearer_token_provider(credential, scope):
    def get_token():
        token = credential.get_token(scope)
        return token.token
    return get_token

# Function to get user ID from request
def get_user_id(
    x_user_id: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    user_id = x_user_id or "anonymous"
    session_id = x_session_id or str(uuid.uuid4())
    return {"user_id": user_id, "session_id": session_id}

# Authentication endpoints
@app.get("/auth/sso")
async def sso_login(request: Request):
    # Generate a secure state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    logger.debug(f"Stored generated state value: {request.session["oauth_state"]}")
    
    # Dynamically generate callback URL based on current request
    redirect_uri = get_callback_url(request)
    logger.debug(f"SSO Login redirect URI: {redirect_uri}")
    print(f"SSO Login redirect URI: {redirect_uri}")
    
    return await oauth.oidc.authorize_redirect(request, redirect_uri, state=state)

@app.get("/sso")
async def auth_callback(request: Request):
    try:
        # Verify state parameter for CSRF protection
        received_state = request.query_params.get("state")
        stored_state = request.session.get("oauth_state")
        logger.debug(f"Received state value: {received_state}")
        logger.debug(f"Stored state value: {stored_state}")
        
        if not received_state or received_state != stored_state:
            print(f"State mismatch: received={received_state}, stored={stored_state}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid state parameter - CSRF protection"}
            )
        
        # Clear the state from session
        request.session.pop("oauth_state", None)
        
        # Exchange code for token
        token = await oauth.oidc.authorize_access_token(request)
        user_info = token.get("userinfo")
        logger.debug(f"Token received value is: {token}")
        logger.debug(f"User information accessing is: {user_info}")
        
        print(f"Token received: {token}")
        print(f"User info: {user_info}")
        
        if user_info:
            # Extract user groups from the token
            user_groups = user_info.get("DD_memberOf", [])
            logger.debug(f"User Groups captured is: {user_groups}")
            
            # Check if user is in allowed groups
            allowed_group = "TKMAI_KME03_RO"
            
            # Handle both string and list formats
            if isinstance(user_groups, str):
                user_groups = [user_groups]
                
            logger.debug(f"Allowed groups captured is: {allowed_group}")
            print(f"User groups: {user_groups}, Allowed: {allowed_group}")
            
            if allowed_group in user_groups:
                # Store user info in session
                request.session["user"] = {
                    "id": user_info.get("sub"),
                    "email": user_info.get("email", user_info.get("preferred_username", "unknown")),
                    "name": user_info.get("name", user_info.get("preferred_username", "User")),
                    "groups": user_groups
                }
                logger.debug(f"User has been authenticated successfully: {request.session['user']}")
                print(f"User authenticated successfully: {request.session['user']}")
                # Redirect to frontend SSO callback handler
                return RedirectResponse(url="/sso/callback")
            else:
                print(f"Access denied: User groups {user_groups} not in allowed group {allowed_group}")
                return JSONResponse(
                    status_code=403,
                    content={"error": f"Access denied: User not in required group {allowed_group}"}
                )
        else:
            print("No user info in token")
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication failed - no user info"}
            )
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Authentication error: {str(e)}"}
        )

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@app.get("/api/auth/status")
async def auth_status(request: Request):
    user = request.session.get("user")
    logger.debug(f"API Auth status accessed by user: {user}")
    if user:
        return {
            "isAuthenticated": True,
            "user": {
                "id": user.get("id"),
                "email": user.get("email"),
                "name": user.get("name")
            }
        }
    else:
        return {"isAuthenticated": False, "user": None}

# Protected endpoint to get user info
@app.get("/protected")
async def protected_route(request: Request):
    user = request.session.get("user")
    logger.debug(f"Protected route accessed by user: {user}")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"user": user}

# Request Models
class ChatRequest(BaseModel):
    message: str
    max_tokens: int = 10000

class CodeExplainRequest(BaseModel):
    code: str
    action: str = "explain"
    max_tokens: int = 300
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class RemediationRequest(BaseModel):
    code: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

# Utility Functions
def estimate_token_count(text: str) -> int:
    return len(text) // 4

async def generate_embedding(user_prompt: str) -> list:
    try:
        response = await client.embeddings.create(
            model=openai_embedding_model,
            input=[user_prompt]
        )
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"Embedding generation failed: {str(e)}")

def fetch_vector_search_results(embedding: list):
    try:
        results = search_client.search(
            search_text="",
            vector_queries=[{"kind": "vector", "vector": embedding, "fields": "contentVector", "k_nearest_neighbors": 5}],
            select=["content", "sourcefile"]
        )
        return [
            {
                "content": doc["content"],
                "source": doc["sourcefile"]
            }
            for doc in results
        ]
    except Exception as e:
        raise RuntimeError(f"Vector search failed: {str(e)}")

def optimize_content_for_tokens(content, max_length=10000):
    if len(content) <= max_length:
        return content
    half_max = max_length // 2
    beginning = content[:half_max]
    end = content[-half_max:]
    return f"{beginning}\n\n[...{len(content) - max_length} characters truncated...]\n\n{end}"

# Chat endpoints
@app.post("/chat/context")
async def chat_context(request: ChatRequest, user_info: dict = Depends(get_user_id)):
    user_prompt = request.message
    user_id = request.user_id or user_info.get("user_id")
    session_id = request.session_id or user_info.get("session_id")
    
    start_time = time.time()
    print("Context chat request:", user_prompt)
    
    try:
        embedding = await generate_embedding(user_prompt)
        loop = asyncio.get_running_loop()
        matched_docs = await loop.run_in_executor(None, fetch_vector_search_results, embedding)
        context_chunks = [doc["content"] for doc in matched_docs]
        context = "\n\n".join(context_chunks)
        messages = [
            {"role": "system", "content": "You are a helpful assistant from Enterprise Data Product Team. Answer a summary only based on the provided context from the Data Products (DP) Documents."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_prompt}"}
        ]
        print("Context messages:", messages)
        response = await client.chat.completions.create(
            model=openai_lang_model,
            messages=messages
        )
        
        ai_response = response.choices[0].message.content.strip()
        processing_time = time.time() - start_time
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        reply = {
            "answer": ai_response,
            "citations": matched_docs
        }
        return reply
    except Exception as e:
        print(f"Error in chat_context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/chat")
async def chat_api(request: ChatRequest, user_info: dict = Depends(get_user_id)):
    user_prompt = request.message
    user_id = request.user_id or user_info.get("user_id")
    session_id = request.session_id or user_info.get("session_id")
    
    start_time = time.time()
    print(f"Processing chat_api with message: {user_prompt}")
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-2024-05-13-tpm",
            temperature=0.3,
            messages=[{"role": "user", "content": user_prompt}],
            stream=False
        )
        
        ai_response = response.choices[0].message.content
        processing_time = time.time() - start_time
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        return {"response": ai_response}
    except Exception as e:
        print(f"Error in chat_api: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Code converter endpoint
@app.post("/converter")
async def converter(request: ChatRequest, user_info: dict = Depends(get_user_id)):
    print("Converter request message:", request.message)
    user_id = request.user_id or user_info.get("user_id")
    session_id = request.session_id or user_info.get("session_id")
    start_time = time.time()
    
    system_prompt = "You are an expert in converting legacy COBOL code to modern Python Code."
    user_prompt = f"Convert the following COBOL code to Python code:\n{request.message}"
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-2024-05-13-tpm",
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False
        )
        
        output_response = response.choices[0].message.content
        processing_time = time.time() - start_time
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        return {"response": output_response}
    except Exception as e:
        print(f"Error in code converter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Code explainer endpoint
@app.post("/code-explainer")
async def code_explainer(request: CodeExplainRequest, user_info: dict = Depends(get_user_id)):
    print("Received code explain request for action:", request.action)
    
    user_id = request.user_id or user_info.get("user_id")
    session_id = request.session_id or user_info.get("session_id")
    start_time = time.time()
    
    if request.action == "simplify":
        system_prompt = "You are a senior software engineer who simplifies complex code without changing functionality."
        user_prompt = f"Simplify this code:\n{request.code}"
        temperature = 0.5
    elif request.action == "optimize":
        system_prompt = "You are a performance-oriented software engineer. Optimize the following code for speed and efficiency."
        user_prompt = f"Optimize this code:\n{request.code}"
        temperature = 0.5
    elif request.action == "summarize":
        system_prompt = "You are a software engineer. Provide a high-level summary of what this code does."
        user_prompt = f"Summarize this code:\n{request.code}"
        temperature = 0.5
    else:
        system_prompt = (
            "You are a Senior Software Engineer expert in all programming languages. "
            "Provide an explanation for the given code."
        )
        user_prompt = f"Explain the following code:\n{request.code}"
        temperature = 0.5

    try:
        response = await client.chat.completions.create(
            model=openai_lang_model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False
        )
        
        output_response = response.choices[0].message.content.strip()
        processing_time = time.time() - start_time
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        return {"response": output_response}
    except Exception as e:
        print(f"Error in code explainer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Remediation endpoints
@app.post("/remediation/validate")
async def remediation_validate(request: RemediationRequest, user_info: dict = Depends(get_user_id)):
    user_id = request.user_id or user_info.get("user_id")
    session_id = request.session_id or user_info.get("session_id")
    start_time = time.time()
    
    system_prompt = """You are a cybersecurity expert specializing in code vulnerability analysis.
    Analyze the provided code for potential security vulnerabilities and provide detailed findings.
    
    Your response should include:
    1. Overall risk assessment (High/Medium/Low)
    2. Specific vulnerabilities found with line numbers
    3. Brief explanation of each vulnerability
    4. Recommended fixes
    
    Format your response as structured text that can be easily parsed."""
    
    user_prompt = f"Analyze this code for security vulnerabilities:\n\n{request.code}"
    
    try:
        response = await client.chat.completions.create(
            model=openai_lang_model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False
        )
        
        analysis_result = response.choices[0].message.content.strip()
        processing_time = time.time() - start_time
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        return {"analysis": analysis_result}
    except Exception as e:
        print(f"Error in remediation validate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/remediation/rewrite/")
async def remediation_rewrite(request: RemediationRequest, user_info: dict = Depends(get_user_id)):
    user_id = request.user_id or user_info.get("user_id")
    session_id = request.session_id or user_info.get("session_id")
    start_time = time.time()
    
    system_prompt = """You are a cybersecurity expert and senior software engineer.
    Rewrite the provided code to fix all security vulnerabilities while maintaining the original functionality.
    
    Your response should:
    1. Provide the complete rewritten code
    2. Maintain the original logic and functionality
    3. Fix all identified security issues
    4. Add appropriate security measures
    5. Include comments explaining the security fixes made
    
    Only return the rewritten code with security comments."""
    
    user_prompt = f"Rewrite this code to fix all security vulnerabilities:\n\n{request.code}"
    
    try:
        response = await client.chat.completions.create(
            model=openai_lang_model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False
        )
        
        rewritten_code = response.choices[0].message.content.strip()
        processing_time = time.time() - start_time
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        return {"rewritten_code": rewritten_code}
    except Exception as e:
        print(f"Error in remediation rewrite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Document ingestion endpoint
@app.post("/ingestion/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_info: dict = Depends(get_user_id)
):
    user_id = user_info.get("user_id")
    session_id = user_info.get("session_id")
    start_time = time.time()
    
    try:
        file_content = await file.read()
        file_size = len(file_content)
        
        # Process different file types
        if file.filename.endswith('.txt'):
            content = file_content.decode('utf-8')
        elif file.filename.endswith('.rtf'):
            content = rtf_to_text(file_content.decode('utf-8'))
        else:
            content = file_content.decode('utf-8', errors='ignore')
        
        processing_time = time.time() - start_time
        
        return {
            "message": "File uploaded and processed successfully",
            "filename": file.filename,
            "size": file_size,
            "content_preview": content[:500] + "..." if len(content) > 500 else content
        }
    except Exception as e:
        print(f"Error in file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

static_path = os.path.join(os.path.dirname(__file__), "dist")

# Serve static files and handle SPA routing
@app.get("/{full_path:path}")
async def serve_static_files(request: Request, full_path: str):
    """Serve static files and handle SPA routing"""
    # Skip for API routes and auth routes that are already handled
    if (full_path.startswith("api/") or 
        full_path.startswith("chat") or 
        full_path.startswith("auth/") or 
        full_path.startswith("logout") or 
        full_path.startswith("sso") or 
        full_path.startswith("protected") or
        full_path.startswith("converter") or
        full_path.startswith("explainer") or
        full_path.startswith("remediation") or
        full_path.startswith("ingestion") or
        full_path.startswith("knowledge") or
        full_path.startswith("health") or
        full_path.startswith("docs") or
        full_path.startswith("openapi")):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Try to serve the requested file
    file_path = os.path.join(static_path, full_path)
    
    # If it's a directory or doesn't exist, serve index.html for SPA routing
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="Static files not found")
    
    return FileResponse(file_path)

# Alternative: Mount static files if the directory exists
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="debug", reload=True)
