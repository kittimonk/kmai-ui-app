
# FastAPI Backend for RAG System with SSO Authentication

This backend provides API endpoints for authentication via PingFederate SSO and a Retrieval Augmented Generation (RAG) system for document search and chat.

## Setup Instructions

1. Create a Python virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:
   ```
   uvicorn api:app --host 0.0.0.0 --port 8000 --reload
   ```

## Configuration

Set the following environment variables for your Azure resources:

- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
- `AZURE_CLIENT_ID`: Your Azure client ID
- `AZURE_OBJECT_ID`: Your Azure object ID

- `OPENAI_RESOURCE_GROUP`: Resource group for Azure OpenAI
- `OPENAI_ACCOUNT_NAME`: Account name for Azure OpenAI
- `OPENAI_API_VERSION`: API version for Azure OpenAI
- `OPENAI_EMBEDDING_MODEL`: Name of your embedding model
- `OPENAI_CHAT_MODEL`: Name of your chat model

- `PING_ISSUER`: Your PingFederate issuer URL
- `PING_CLIENT_ID`: Your PingFederate client ID
- `PING_CLIENT_SECRET`: Your PingFederate client secret
- `PING_REDIRECT_URI`: Your application's callback URL

- `ADLS_ACCOUNT_NAME`: Azure Data Lake Storage account name
- `ADLS_CONTAINER_NAME`: Container name in ADLS for document storage

## API Endpoints

- `GET /`: Root endpoint to check if the API is running
- `POST /chat/`: Chat endpoint to interact with Azure OpenAI
- `POST /documents/upload/`: Upload endpoint for document ingestion
- `POST /search/`: Search endpoint for document retrieval
- `POST /auth/verify`: Endpoint for token verification

## Authentication

This API uses Azure Managed Identity for authenticating with Azure services and PingFederate SSO for user authentication. The application will automatically use the Managed Identity when deployed to Azure App Service, or fall back to the specified client ID for local development.
