import azure.functions as func
import json
import logging
import os
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import hashlib
from datetime import datetime

# Azure OpenAI configuration using SDK v2
def get_openai_client():
    """Initialize Azure OpenAI client with SDK v2"""
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_KEY")
    
    if not endpoint or not api_key:
        raise ValueError("Azure OpenAI configuration missing")
    
    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-02-01"  # Latest API version
    )

def get_storage_client():
    """Initialize Azure Storage client"""
    connection_string = os.environ.get("AzureWebJobsStorage")
    if not connection_string:
        raise ValueError("Storage connection string missing")
    return BlobServiceClient.from_connection_string(connection_string)

def get_cosmos_client():
    """Initialize Cosmos DB client"""
    endpoint = os.environ.get("COSMOS_ENDPOINT")
    key = os.environ.get("COSMOS_KEY")
    
    if not endpoint or not key:
        raise ValueError("Cosmos DB configuration missing")
    
    return CosmosClient(endpoint, key)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Process documents with Azure OpenAI for grant analysis
    """
    logging.info('ProcessDocument function triggered')
    
    try:
        # Parse request
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        document_content = req_body.get('documentContent')
        file_name = req_body.get('fileName')
        file_type = req_body.get('fileType', 'txt')
        
        if not document_content or not file_name:
            return func.HttpResponse(
                json.dumps({"error": "documentContent and fileName are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Initialize Azure services
        openai_client = get_openai_client()
        storage_client = get_storage_client()
        cosmos_client = get_cosmos_client()
        
        # Upload to blob storage
        container_name = "documents"
        blob_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_name}"
        
        container_client = storage_client.get_container_client(container_name)
        
        # Create container if it doesn't exist
        try:
            container_client.create_container()
        except Exception:
            pass  # Container already exists
        
        # Upload document
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(document_content, overwrite=True)
        
        # Analyze with Azure OpenAI
        deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")
        
        system_prompt = """You are a document analyzer specializing in grant-related content. 
        Analyze the following document and extract key information. Return a JSON response with:
        - summary: Brief document summary
        - documentType: Type (grant application, grant opportunity, research paper, etc.)
        - keyEntities: Important organizations, amounts, dates mentioned
        - isGrantRelated: boolean indicating if grant-related
        - confidence: confidence score (0-1)
        - grantRequirements: If grant opportunity, list key requirements
        - fundingAmount: Any funding amounts mentioned
        - deadlines: Important dates/deadlines found"""
        
        user_prompt = f"Document filename: {file_name}\nDocument content: {document_content[:4000]}"
        
        # Call Azure OpenAI with SDK v2
        response = openai_client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse JSON response from OpenAI
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            analysis = {
                "summary": analysis_text,
                "documentType": "unknown",
                "keyEntities": [],
                "isGrantRelated": False,
                "confidence": 0.5,
                "grantRequirements": [],
                "fundingAmount": None,
                "deadlines": []
            }
        
        # Store in Cosmos DB
        database_name = os.environ.get("COSMOS_DATABASE_NAME", "GrantAnalysis")
        container_name_cosmos = "Documents"
        
        database = cosmos_client.get_database_client(database_name)
        container = database.get_container_client(container_name_cosmos)
        
        document_record = {
            "id": blob_name,
            "fileName": file_name,
            "fileType": file_type,
            "blobUrl": blob_client.url,
            "analysis": analysis,
            "uploadedAt": datetime.now().isoformat(),
            "wordCount": len(document_content.split())
        }
        
        container.create_item(document_record)
        
        logging.info(f"Document processed successfully: {file_name}")
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "documentId": blob_name,
                "analysis": analysis,
                "blobUrl": blob_client.url,
                "wordCount": len(document_content.split())
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "details": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )