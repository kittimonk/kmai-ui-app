
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

# ----------------------------
# Request Models
# ----------------------------
class ChatRequest(BaseModel):
    message: str  # Changed from 'prompt' to 'message' to match frontend
    max_tokens: int = 10000
    user_id: Optional[str] = None
    session_id: Optional[str] = None

# ----------------------------
# Utility Functions
# ----------------------------
def estimate_token_count(text: str) -> int:
    """Estimate token count. Roughly 4 chars per token for English text."""
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
            search_text="",  # required but ignored during vector search
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
@app.on_event("startup")
async def startup_db_client():
    initialize_chat_history_table()
    initialize_feature_interaction_table()

# Function to get user ID from request
def get_user_id(
    x_user_id: Optional[str] = Header(None),
    x_session_id: Optional[str] = Header(None)
):
    """Extract user ID from header or generate a temporary one"""
    user_id = x_user_id or "anonymous"
    session_id = x_session_id or str(uuid.uuid4())
    return {"user_id": user_id, "session_id": session_id}

# ----------------------------
# HEALTH CHECK ENDPOINTS
# ----------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "service": "kmai-app"
    }

@app.get("/api/health")
def api_health():
    return {"status": "ok", "message": "API server is running"}

# ----------------------------
# Update for explicit API access from frontend
# ----------------------------
@app.options("/api/{rest_of_path:path}")
async def options_route(rest_of_path: str):
    return {}  # Enable CORS preflight for all /api routes

# ----------------------------
# HISTORY ENDPOINTS
# ----------------------------
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

# ----------------------------
# CHAT ENDPOINTS
# ----------------------------
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
        
        # Log the interaction to the database
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
        # Still log failed interactions
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

# Updated chat endpoint: expects JSON payload matching ChatRequest model
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
        
        # Extract the response content
        ai_response = response.choices[0].message.content
        processing_time = time.time() - start_time
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        # Log the interaction to the database
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
        # Still log failed interactions
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

# ----------------------------
# CODE CONVERTER ENDPOINT
# ----------------------------
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
        
        # Log feature interaction
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
        # Log failed interactions
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

# ----------------------------
# CODE EXPLAINER ENDPOINT
# ----------------------------
class CodeExplainRequest(BaseModel):
    code: str
    action: str = "explain"
    max_tokens: int = 300
    user_id: Optional[str] = None
    session_id: Optional[str] = None

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
        
        # Log feature interaction
        log_feature_interaction(
            user_id=user_id,
            feature_type=f"code_explainer_{request.action}",
            input_data=request.code,
            output_data=output_response,
            endpoint_used="/code-explainer",
            processing_time=processing_time,
            tokens_used=tokens_used,
            session_id=session_id
        )
        
        return output_response
    except Exception as e:
        print(f"Error in code explainer: {str(e)}")
        # Log failed interactions
        log_feature_interaction(
            user_id=user_id,
            feature_type=f"code_explainer_{request.action}",
            input_data=request.code,
            output_data=f"Error: {str(e)}",
            endpoint_used="/code-explainer",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# ----------------------------
# KNOWLEDGE BASE ENDPOINT
# ----------------------------
class KnowledgeBaseRequest(BaseModel):
    message: str
    max_tokens: int = 1000
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@app.post("/api/knowledge-base/query")
async def query_knowledge_base(request: KnowledgeBaseRequest, user_info: dict = Depends(get_user_id)):
    user_id = request.user_id or user_info.get("user_id")
    session_id = request.session_id or user_info.get("session_id")
    start_time = time.time()
    
    try:
        # Generate embeddings for the query
        embedding = await generate_embedding(request.message)
        
        # Use the embeddings to search the knowledge base
        loop = asyncio.get_running_loop()
        search_results = await loop.run_in_executor(None, fetch_vector_search_results, embedding)
        
        # Format and return the results
        output_response = {
            "query": request.message,
            "results": search_results
        }
        
        processing_time = time.time() - start_time
        
        # Log the knowledge base query
        log_feature_interaction(
            user_id=user_id,
            feature_type="knowledge_base",
            input_data=request.message,
            output_data=str(search_results),
            endpoint_used="/api/knowledge-base/query",
            processing_time=processing_time,
            session_id=session_id,
            metadata={"result_count": len(search_results)}
        )
        
        return output_response
    except Exception as e:
        print(f"Error in knowledge base query: {str(e)}")
        # Log failed interactions
        log_feature_interaction(
            user_id=user_id,
            feature_type="knowledge_base",
            input_data=request.message,
            output_data=f"Error: {str(e)}",
            endpoint_used="/api/knowledge-base/query",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# ----------------------------
# Archer / Remediation Endpoints
# ----------------------------
class ArcherRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    user_id: Optional[str] = None
    session_id: Optional[str] = None

def ignore_rtf_to_text(rtf_content):
    text = re.sub(r'^\{\\rtf1.*\}\s*', '', rtf_content)
    text = re.sub(r'\\[a-zA-Z0-9]+(-?[0-9]+)?\\s?', '', text)
    text = re.sub(r'\\\'[0-9a-fA-F]{2}', '', text)
    prev_text = ""
    while prev_text != text:
        prev_text = text
        text = re.sub(r'\\\{.*?\\\}', '', text)
    text = re.sub(r'\\par\s?', '\n', text)
    text = re.sub(r'\\line\s?', '\n', text)
    text = re.sub(r'\\[a-z]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\\([{}\\])', r'\1', text)
    return text.strip()

@app.post("/archer/")
async def process_remediation_files(
    remediationPlan: Optional[UploadFile] = File(None),
    complianceRequirements: Optional[UploadFile] = File(None),
    findingsDetails: Optional[UploadFile] = File(None),
    remediationPlan_content: Optional[str] = Form(None),
    complianceRequirements_content: Optional[str] = Form(None),
    findingsDetails_content: Optional[str] = Form(None),
    customPrompt: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None)
):
    if not any([
        remediationPlan, complianceRequirements, findingsDetails,
        remediationPlan_content, complianceRequirements_content, findingsDetails_content
    ]):
        raise HTTPException(status_code=400, detail="No files or content were provided")

    # If no user_id provided in form, get from header
    if not user_id or not session_id:
        user_info = get_user_id()
        user_id = user_id or user_info.get("user_id")
        session_id = session_id or user_info.get("session_id")
    
    start_time = time.time()
    file_contents = {}

    if remediationPlan_content:
        file_contents["remediation_plan"] = remediationPlan_content
    elif remediationPlan:
        content = await remediationPlan.read()
        content_str = content.decode("utf-8", errors="ignore")
        if remediationPlan.filename.lower().endswith('.rtf'):
            content_str = rtf_to_text(content_str)
        file_contents["remediation_plan"] = optimize_content_for_tokens(content_str)
    
    if complianceRequirements_content:
        file_contents["compliance_requirements"] = complianceRequirements_content
    elif complianceRequirements:
        content = await complianceRequirements.read()
        content_str = content.decode("utf-8", errors="ignore")
        if complianceRequirements.filename.lower().endswith('.rtf'):
            content_str = rtf_to_text(content_str)
        file_contents["compliance_requirements"] = optimize_content_for_tokens(content_str)

    if findingsDetails_content:
        file_contents["findings_details"] = findingsDetails_content
    elif findingsDetails:
        content = await findingsDetails.read()
        content_str = content.decode("utf-8", errors="ignore")
        if findingsDetails.filename.lower().endswith('.rtf'):
            content_str = rtf_to_text(content_str)
        file_contents["findings_details"] = optimize_content_for_tokens(content_str)

    prompt = customPrompt if customPrompt else """
Below is an audit finding and the associated remediation plan.
Please analyze the remediation plan and determine if it adequately addresses the compliance requirements
and findings details provided. Provide your assessment with clear, actionable feedback.
Return the response with clear sections for:
- Control ID
- Finding Details
- Remediation Details
- Overall Risk Score
- Confidence Score
- Compliance Status
- Identified Gaps
- Recommendations
- Final Rating
"""

    total_content_length = sum(len(content) for content in file_contents.values())
    if total_content_length > 30000:
        scale_factor = 30000 / total_content_length
        for file_type, content in file_contents.items():
            max_len = int(len(content) * scale_factor)
            file_contents[file_type] = optimize_content_for_tokens(content, max_len)

    for file_type, content in file_contents.items():
        prompt += f"\n\n{file_type.upper()}:\n{content}"

    try:
        api_url = f"https://{openai_account_name}.openai.azure.com/openai/deployments/gpt-4o-2024-05-13-tpm/chat/completions?api-version=2023-01-01-preview"
        print("apiUrl::", api_url)
        response = await client.chat.completions.create(
            model="gpt-4o-2024-05-13-tpm",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a strict GRC Analyst and expert in compliance. Evaluate remediation plans against provided documents and return detailed feedback."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        reply_content = response.choices[0].message.content.strip()
        
        processing_time = time.time() - start_time
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        # Log feature interaction
        log_feature_interaction(
            user_id=user_id,
            feature_type="remediation_analysis",
            input_data=f"Remediation plan analysis with {len(file_contents)} documents",
            output_data=reply_content,
            endpoint_used="/archer",
            processing_time=processing_time,
            tokens_used=tokens_used,
            session_id=session_id,
            metadata={"file_types": list(file_contents.keys())}
        )
        
        return JSONResponse(content={"response": reply_content})
    except Exception as e:
        print(f"Error calling OpenAI: {str(e)}")
        # Log failed interaction
        log_feature_interaction(
            user_id=user_id,
            feature_type="remediation_analysis",
            input_data=f"Remediation plan analysis with {len(file_contents)} documents",
            output_data=f"Error: {str(e)}",
            endpoint_used="/archer",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e), "file_types": list(file_contents.keys())}
        )
        raise HTTPException(status_code=500, detail=f"Error processing with OpenAI: {str(e)}")

@app.post("/archer/rewrite")
async def rewrite_remediation(
    remediationPlan: UploadFile = File(...),
    analysisContext: str = Form(...),
    action: str = Form(...),
    user_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None)
):
    if action != "rewrite":
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid action: {action}. Expected 'rewrite'"}
        )
        
    # If no user_id provided in form, get from header
    if not user_id or not session_id:
        user_info = get_user_id()
        user_id = user_id or user_info.get("user_id")
        session_id = session_id or user_info.get("session_id")
    
    start_time = time.time()
    
    content = await remediationPlan.read()
    file_content = content.decode("utf-8")
    if remediationPlan.filename.lower().endswith('.rtf'):
        file_content = rtf_to_text(file_content)
    optimized_plan = optimize_content_for_tokens(file_content, 2000)
    system_prompt = """
You are a compliance expert tasked with improving a remediation plan based on analysis feedback.
Consider compliance requirements, timelines, accountability, and validation steps.
Rewrite the remediation plan in a clear, structured format.
"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-2024-05-13-tpm",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the original remediation plan:\n\n{optimized_plan}\n\nHere is the analysis feedback:\n\n{analysisContext}\n\nPlease rewrite the remediation plan to address all issues."}
            ],
            stream=False
        )
        rewritten_plan = response.choices[0].message.content
        
        processing_time = time.time() - start_time
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        # Log feature interaction
        log_feature_interaction(
            user_id=user_id,
            feature_type="remediation_rewrite",
            input_data=f"Original plan: {optimized_plan[:200]}... + Analysis context",
            output_data=rewritten_plan,
            endpoint_used="/archer/rewrite",
            processing_time=processing_time,
            tokens_used=tokens_used,
            session_id=session_id
        )
        
        return {
            "rewrittenPlan": rewritten_plan,
            "originalLength": len(file_content),
            "rewrittenLength": len(rewritten_plan)
        }
    except Exception as e:
        print(f"Error in remediation rewrite: {str(e)}")
        # Log failed interaction
        log_feature_interaction(
            user_id=user_id,
            feature_type="remediation_rewrite",
            input_data=f"Original plan + Analysis context",
            output_data=f"Error: {str(e)}",
            endpoint_used="/archer/rewrite",
            processing_time=time.time() - start_time,
            session_id=session_id,
            metadata={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error processing with OpenAI: {str(e)}")

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
