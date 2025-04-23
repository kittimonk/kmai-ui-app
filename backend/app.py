
@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "service": "kmai-app"
    }
