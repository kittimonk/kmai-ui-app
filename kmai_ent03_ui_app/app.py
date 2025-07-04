import asyncio
import os, subprocess, time
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
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
from kmai_ent03_ui_app.vault import VaultConfig, VaultService

# Add the parent directory to sys.path to make backend importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our database module
#from backend.database import (
    #initialize_chat_history_table, 
    #initialize_feature_interaction_table,
    #log_chat_interaction, 
    #log_feature_interaction,
    #get_user_chat_history,
    #get_user_feature_history
#)

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

OIDC_CLIENT_ID = vault_service.get_secret("OIDC_CLIENT_ID", path)
OIDC_CLIENT_SECRET = vault_service.get_secret("OIDC_CLIENT_SECRET", path)
OIDC_AUTHORITY = "https://fedsit.rastest.ca"
OIDC_CALLBACK_URL = "https://kma03.dev.com/sso"

# OAuth configuration
oauth = OAuth()
oauth.register(
    name="oidc",
    client_id=OIDC_CLIENT_ID,
    client_secret=OIDC_CLIENT_SECRET,
    server_metadata_url=f"{OIDC_AUTHORITY}/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid CustomMemberOf",
    },
)

# Initialize FastAPI app
app = FastAPI(debug=True)

# Add SessionMiddleware
secure_random_key = secrets.token_hex(32)
app.add_middleware(
    SessionMiddleware,
    secret_key=secure_random_key,
    max_age=14 * 24 * 3600,
    https_only=False,
    same_site="lax"
)

# Session middleware to check authentication
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # Skip middleware for static files, auth routes, and health checks
    if (request.url.path.startswith("/static") or 
        request.url.path.startswith("/assets") or
        request.url.path in ["/", "/login", "/logout", "/sso/callback", "/health", "/api/health"] or
        request.url.path.startswith("/api/auth") or
        request.url.path.endswith(".js") or
        request.url.path.endswith(".css") or
        request.url.path.endswith(".ico") or
        request.url.path.endswith(".png") or
        request.url.path.endswith(".svg")):
        response = await call_next(request)
        return response
    
    # Check if user is authenticated for protected routes
    user = request.session.get("user")
    if not user and not request.url.path.startswith("/docs") and not request.url.path.startswith("/openapi"):
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

# Request Models
class ChatRequest(BaseModel):
    message: str
    max_tokens: int = 10000
    user_id: Optional[str] = None
    session_id: Optional[str] = None

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

# Initialize the database tables
#@app.on_event("startup")
#async def startup_db_client():
    #initialize_chat_history_table()
    #initialize_feature_interaction_table()

# Function to get user ID from request
def get_user_id(
    x_user_id: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    user_id = x_user_id or "anonymous"
    session_id = x_session_id or str(uuid.uuid4())
    return {"user_id": user_id, "session_id": session_id}

# Authentication endpoints
@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.oidc.authorize_redirect(request, redirect_uri)

@app.get("/sso/callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.oidc.authorize_access_token(request)
        user_info = token.get("userinfo")
        
        if user_info:
            # Extract user groups from the token
            groups = user_info.get("CustomMemberOf", [])
            
            # Check if user is in allowed groups
            allowed_groups = ["CN=GPT_Enterprise_Dev,OU=Groups,DC=test,DC=ca"]
            
            if any(group in allowed_groups for group in groups):
                # Store user info in session
                request.session["user"] = {
                    "id": user_info.get("sub"),
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "groups": groups
                }
                return RedirectResponse(url="/sso/callback")
            else:
                return JSONResponse(
                    status_code=403,
                    content={"error": "Access denied: User not in allowed groups"}
                )
        else:
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication failed"}
            )
    except Exception as e:
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
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"user": user}

# Health check endpoints
@app.get("/health")
def health():
    return {"status": "healthy", "service": "kmai-app"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "message": "API server is running"}

# Options route for CORS
@app.options("/api/{rest_of_path:path}")
async def options_route(rest_of_path: str):
    return {}

# History endpoints
@app.get("/api/chat/history")
async def get_chat_history(user_info: dict = Depends(get_user_id)):
    user_id = user_info.get("user_id")
    if user_id == "anonymous":
        return JSONResponse(content={"error": "User ID required"}, status_code=400)
    
    history = get_user_chat_history(user_id)
    return {"history": history}

@app.get("/api/feature/history")
async def get_feature_history(
    feature_type: Optional[str] = None, 
    user_info: dict = Depends(get_user_id)
):
    user_id = user_info.get("user_id")
    if user_id == "anonymous":
        return JSONResponse(content={"error": "User ID required"}, status_code=400)
    
    history = get_user_feature_history(user_id, feature_type)
    return {"history": history}

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
        
        log_chat_interaction(
            user_id=user_id,
            user_message=user_prompt,
            ai_response=ai_response,
            endpoint_used="/chat/context",
            processing_time=processing_time,
            tokens_used=tokens_used,
            session_id=session_id,
            metadata={"matched_docs": len(matched_docs)}
        )
        
        reply = {
            "answer": ai_response,
            "citations": matched_docs
        }
        return reply
    except Exception as e:
        print(f"Error in chat_context: {str(e)}")
        log_chat_interaction(
            user_id=user_id,
            user_message=user_prompt,
            ai_response=f"Error: {str(e)}",
            endpoint_used="/chat/context",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/api/chat")
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
        
        log_chat_interaction(
            user_id=user_id,
            user_message=user_prompt,
            ai_response=ai_response,
            endpoint_used="/api/chat",
            processing_time=processing_time,
            tokens_used=tokens_used,
            session_id=session_id
        )
        
        return {"response": ai_response}
    except Exception as e:
        print(f"Error in chat_api: {str(e)}")
        log_chat_interaction(
            user_id=user_id,
            user_message=user_prompt,
            ai_response=f"Error: {str(e)}",
            endpoint_used="/api/chat",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Code converter endpoint
@app.post("/converter/")
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
        
        log_feature_interaction(
            user_id=user_id,
            feature_type="code_converter",
            input_data=request.message,
            output_data=output_response,
            endpoint_used="/converter",
            processing_time=processing_time,
            tokens_used=tokens_used,
            session_id=session_id
        )
        
        return {"response": output_response}
    except Exception as e:
        print(f"Error in code converter: {str(e)}")
        log_feature_interaction(
            user_id=user_id,
            feature_type="code_converter",
            input_data=request.message,
            output_data=f"Error: {str(e)}",
            endpoint_used="/converter",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Code explainer endpoint
@app.post("/code-explainer/")
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
        
        log_feature_interaction(
            user_id=user_id,
            feature_type="code_explainer",
            input_data=request.code,
            output_data=output_response,
            endpoint_used="/code-explainer",
            processing_time=processing_time,
            tokens_used=tokens_used,
            session_id=session_id,
            metadata={"action": request.action}
        )
        
        return {"response": output_response}
    except Exception as e:
        print(f"Error in code explainer: {str(e)}")
        log_feature_interaction(
            user_id=user_id,
            feature_type="code_explainer",
            input_data=request.code,
            output_data=f"Error: {str(e)}",
            endpoint_used="/code-explainer",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"action": request.action, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Remediation endpoints
@app.post("/remediation/validate/")
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
        
        log_feature_interaction(
            user_id=user_id,
            feature_type="remediation_validate",
            input_data=request.code,
            output_data=analysis_result,
            endpoint_used="/remediation/validate",
            processing_time=processing_time,
            tokens_used=tokens_used,
            session_id=session_id
        )
        
        return {"analysis": analysis_result}
    except Exception as e:
        print(f"Error in remediation validate: {str(e)}")
        log_feature_interaction(
            user_id=user_id,
            feature_type="remediation_validate",
            input_data=request.code,
            output_data=f"Error: {str(e)}",
            endpoint_used="/remediation/validate",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e)}
        )
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
        
        log_feature_interaction(
            user_id=user_id,
            feature_type="remediation_rewrite",
            input_data=request.code,
            output_data=rewritten_code,
            endpoint_used="/remediation/rewrite",
            processing_time=processing_time,
            tokens_used=tokens_used,
            session_id=session_id
        )
        
        return {"rewritten_code": rewritten_code}
    except Exception as e:
        print(f"Error in remediation rewrite: {str(e)}")
        log_feature_interaction(
            user_id=user_id,
            feature_type="remediation_rewrite",
            input_data=request.code,
            output_data=f"Error: {str(e)}",
            endpoint_used="/remediation/rewrite",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e)}
        )
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
        
        log_feature_interaction(
            user_id=user_id,
            feature_type="document_ingestion",
            input_data=f"File: {file.filename}, Size: {file_size} bytes",
            output_data=f"Successfully processed {len(content)} characters",
            endpoint_used="/ingestion/upload",
            processing_time=processing_time,
            session_id=session_id,
            metadata={
                "filename": file.filename,
                "file_size": file_size,
                "content_length": len(content)
            }
        )
        
        return {
            "message": "File uploaded and processed successfully",
            "filename": file.filename,
            "size": file_size,
            "content_preview": content[:500] + "..." if len(content) > 500 else content
        }
    except Exception as e:
        print(f"Error in file upload: {str(e)}")
        log_feature_interaction(
            user_id=user_id,
            feature_type="document_ingestion",
            input_data=f"File: {file.filename if file else 'Unknown'}",
            output_data=f"Error: {str(e)}",
            endpoint_used="/ingestion/upload",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# Static file serving
app.mount("/static", StaticFiles(directory="dist"), name="static")

# Catch-all route for frontend
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Serve static files
    if full_path.startswith("assets/") or full_path.endswith(('.js', '.css', '.ico', '.png', '.svg')):
        file_path = Path("dist") / full_path
        if file_path.exists():
            return FileResponse(file_path)
    
    # Serve index.html for all other routes (SPA)
    return FileResponse("dist/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
