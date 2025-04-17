import asyncio
import os, subprocess, time
import pyodbc, redis
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential, get_bearer_token_provider
from azure.storage.blob import BlobServiceClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from openai import AzureOpenAI
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField
from azure.search.documents import SearchClient
from pydantic import BaseModel
import requests
import httpx
import openai
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, Form, FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import re
import json
from striprtf.striprtf import rtf_to_text

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

# Initialize FastAPI
app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # Alternative development port if needed
    "http://localhost:8080",  # Alternative local development port
    os.environ.get("WEBSITE_HOSTNAME", "*")  # Azure Web App hostname
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Azure authentication - works both locally and in Azure
try:
    # Try Managed Identity first (for Azure deployment)
    msi = ManagedIdentityCredential(client_id=None if os.getenv("WEBSITE_INSTANCE_ID") else client_id)
    # Test the credential to see if it works
    msi.get_token("https://management.azure.com/.default")
except Exception:
    # Fall back to Default Azure Credential for local development
    msi = DefaultAzureCredential()

# Initialize OpenAI client
client = openai.AzureOpenAI(
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

# ----------------------------
# HEALTH CHECK ENDPOINTS
# ----------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "message": "API server is running"}

# ----------------------------
# CHAT ENDPOINTS
# ----------------------------
@app.post("/chat/context")
async def chat_context(request: ChatRequest):
    user_prompt = request.message
    print("Context chat request:", user_prompt)
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
    reply = {
        "answer": response.choices[0].message.content.strip(),
        "citations": matched_docs
    }
    return reply

# Updated chat endpoint: expects JSON payload matching ChatRequest model
@app.post("/api/chat")
async def chat_api(request: ChatRequest):
    print(f"Processing chat_api with message: {request.message}")
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-2024-05-13-tpm",
            temperature=0.3,
            messages=[{"role": "user", "content": request.message}],
            stream=False
        )
        
        # Extract the response content
        content = response.choices[0].message.content
        
        return {"response": content}
    except Exception as e:
        print(f"Error in chat_api: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# ----------------------------
# CODE CONVERTER ENDPOINT
# ----------------------------
@app.post("/converter/")
async def converter(request: ChatRequest):
    print("Converter request message:", request.message)
    system_prompt = "You are an expert in converting legacy COBOL code to modern Python Code."
    user_prompt = f"Convert the following COBOL code to Python code:\n{request.message}"
    
    response = await client.chat.completions.create(
        model="gpt-4o-2024-05-13-tpm",
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=False
    )
    return {"response": response.choices[0].message.content}

# ----------------------------
# CODE EXPLAINER ENDPOINT
# ----------------------------
class CodeExplainRequest(BaseModel):
    code: str
    action: str = "explain"
    max_tokens: int = 300

@app.post("/code-explainer/")
async def code_explainer(request: CodeExplainRequest):
    print("Received code explain request for action:", request.action)
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

    response = await client.chat.completions.create(
        model=openai_lang_model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=False
    )
    return response.choices[0].message.content.strip()

# ----------------------------
# Archer / Remediation Endpoints
# ----------------------------
class ArcherRequest(BaseModel):
    prompt: str
    max_tokens: int = 100

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
    customPrompt: Optional[str] = Form(None)
):
    if not any([
        remediationPlan, complianceRequirements, findingsDetails,
        remediationPlan_content, complianceRequirements_content, findingsDetails_content
    ]):
        raise HTTPException(status_code=400, detail="No files or content were provided")

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
        return JSONResponse(content={"response": reply_content})
    except Exception as e:
        print(f"Error calling OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing with OpenAI: {str(e)}")

@app.post("/archer/rewrite")
async def rewrite_remediation(
    remediationPlan: UploadFile = File(...),
    analysisContext: str = Form(...),
    action: str = Form(...)
):
    if action != "rewrite":
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid action: {action}. Expected 'rewrite'"}
        )
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
    return {
        "rewrittenPlan": rewritten_plan,
        "originalLength": len(file_content),
        "rewrittenLength": len(rewritten_plan)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
