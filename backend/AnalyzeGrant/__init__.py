import azure.functions as func
import json
import logging
import os
from openai import AzureOpenAI
from azure.cosmos import CosmosClient
from datetime import datetime
import hashlib

def get_openai_client():
    """Initialize Azure OpenAI client with SDK v2"""
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_KEY")
    
    if not endpoint or not api_key:
        raise ValueError("Azure OpenAI configuration missing")
    
    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-02-01"
    )

def get_cosmos_client():
    """Initialize Cosmos DB client"""
    endpoint = os.environ.get("COSMOS_ENDPOINT")
    key = os.environ.get("COSMOS_KEY")
    
    if not endpoint or not key:
        raise ValueError("Cosmos DB configuration missing")
    
    return CosmosClient(endpoint, key)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Analyze grant opportunities with Azure OpenAI
    """
    logging.info('AnalyzeGrant function triggered')
    
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
        
        grant_description = req_body.get('grantDescription')
        organization_type = req_body.get('organizationType', 'Not specified')
        funding_amount = req_body.get('fundingAmount', 'Not specified')
        deadline = req_body.get('deadline', 'Not specified')
        
        if not grant_description:
            return func.HttpResponse(
                json.dumps({"error": "grantDescription is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Initialize Azure services
        openai_client = get_openai_client()
        cosmos_client = get_cosmos_client()
        
        # Analyze grant with Azure OpenAI
        deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")
        
        system_prompt = """You are a grant analysis expert. Analyze the following grant opportunity and provide comprehensive assessment. 
        Return a JSON response with:
        - eligibilityRequirements: Array of key eligibility criteria
        - fundingDetails: Object with amount, duration, matching requirements
        - applicationRequirements: Array of required documents/information
        - evaluationCriteria: Array of evaluation criteria
        - strategicAlignment: Array of research/project areas supported
        - competitiveness: Assessment (low/medium/high)
        - recommendedApplicantProfile: Description of ideal applicant
        - keyDeadlines: Important dates and milestones
        - riskFactors: Potential challenges or risks
        - successFactors: What makes applications successful
        - applicationTips: Specific tips for strong application"""
        
        user_prompt = f"""Grant Description: {grant_description}
        
Organization Type: {organization_type}
Funding Amount: {funding_amount}
Deadline: {deadline}"""
        
        # Call Azure OpenAI
        response = openai_client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse JSON response
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            return func.HttpResponse(
                json.dumps({"error": "Failed to parse grant analysis from OpenAI"}),
                status_code=500,
                mimetype="application/json"
            )
        
        # Generate unique grant ID
        grant_id = f"grant_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(grant_description.encode()).hexdigest()[:8]}"
        
        # Store in Cosmos DB
        database_name = os.environ.get("COSMOS_DATABASE_NAME", "GrantAnalysis")
        container_name = "GrantOpportunities"
        
        database = cosmos_client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        grant_record = {
            "id": grant_id,
            "originalDescription": grant_description,
            "organizationType": organization_type,
            "fundingAmount": funding_amount,
            "deadline": deadline,
            "analysis": analysis,
            "analyzedAt": datetime.now().isoformat(),
            "status": "active"
        }
        
        container.create_item(grant_record)
        
        logging.info(f"Grant analyzed successfully: {grant_id}")
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "grantId": grant_id,
                "analysis": analysis
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error analyzing grant: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "details": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )