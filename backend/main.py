
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
