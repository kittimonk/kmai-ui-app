import os
import secrets
from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# Configuration
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "dist")  # Adjust if 'build'
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID", "your-client-id")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET", "your-client-secret")
OIDC_AUTHORITY = os.getenv("OIDC_AUTHORITY", "https://your-oidc-authority.com")
OIDC_CALLBACK_URL = os.getenv("OIDC_CALLBACK_URL", "http://localhost:8000/sso")

# Generate a strong session secret if not set (do NOT rely on this in production!)
SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    print("No SESSION_SECRET in environment, generating a random one for this session!")
    SESSION_SECRET = secrets.token_hex(32)

app = FastAPI()

# CORS - loosen for local development, lock down for prod!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",  # Use 'strict' or 'none' for prod as needed
    https_only=False  # True in production with HTTPS
)

# Serve React static files
app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")

# OAuth / OIDC setup
config_data = {
    'OIDC_CLIENT_ID': OIDC_CLIENT_ID,
    'OIDC_CLIENT_SECRET': OIDC_CLIENT_SECRET,
}
cfg = Config(environ=config_data)
oauth = OAuth(cfg)

oauth.register(
    name="oidc",
    client_id=OIDC_CLIENT_ID,
    client_secret=OIDC_CLIENT_SECRET,
    server_metadata_url=f"{OIDC_AUTHORITY}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)

def get_user_session(request: Request):
    return request.session.get("user")

# SSO login endpoint
@app.get("/login")
async def login(request: Request):
    redirect_uri = OIDC_CALLBACK_URL
    return await oauth.oidc.authorize_redirect(request, redirect_uri)

# OIDC callback endpoint
@app.route("/sso", methods=["GET"])
async def sso_callback(request: Request):
    token = await oauth.oidc.authorize_access_token(request)
    user = await oauth.oidc.parse_id_token(request, token)
    request.session["user"] = {
        "email": user.get("email"),
        "name": user.get("name", user.get("preferred_username", "")),
        "sub": user.get("sub"),
    }
    # Redirect to frontend's /sso/callback route to complete login in React
    return RedirectResponse("/sso/callback")

# Logout endpoint
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    # Optionally, redirect to OIDC provider's logout endpoint
    return RedirectResponse("/")

# Auth status endpoint for frontend
@app.get("/api/auth/status")
async def auth_status(request: Request):
    user = request.session.get("user")
    if user:
        return JSONResponse({"authenticated": True, "user": user})
    else:
        return JSONResponse({"authenticated": False})

# Catch-all for React Router
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    return FileResponse(index_file)

# Uvicorn entrypoint for development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
