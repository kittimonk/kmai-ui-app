
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy", "service": "kmai-app"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "message": "API server is running"}

# Determine the static directory path
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    print(f"Static files mounted from: {static_dir}")
else:
    print("WARNING: Could not mount static files - directory doesn't exist")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
