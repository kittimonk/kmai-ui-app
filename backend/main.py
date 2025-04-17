
import os
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# ... keep existing code (import statements)

app = FastAPI()

# Update the origins list to include all necessary domains
origins = [
    "http://localhost:3000",  # Primary local development port
    "http://localhost:8080",  # Alternative local development port
    os.environ.get("WEBSITE_HOSTNAME", "*")  # Azure Web App hostname or wildcard
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Updated to use the more specific origins list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... keep existing code (health check endpoint)

# ... keep existing code (authentication endpoints)

# ... keep existing code (chat endpoints)

# ... keep existing code (document processing endpoints)

# ... keep existing code (code conversion endpoints)

# ... keep existing code (knowledge base endpoints)

# ... keep existing code (AI remediation endpoints)

# ... keep existing code (any other API endpoints that were present in the original file)
