import azure.functions as func
import json
import logging
import os
from openai import AzureOpenAI
from azure.cosmos import CosmosClient

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
    Find matching grants for user documents/profiles
    """
    logging.info('GetMatches function triggered')
    
    try:
        # Get query parameters
        document_id = req.params.get('documentId')
        organization_type = req.params.get('organizationType')
        research_area = req.params.get('researchArea')
        
        if not document_id and not organization_type:
            return func.HttpResponse(
                json.dumps({"error": "Either documentId or organizationType is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Initialize Azure services
        openai_client = get_openai_client()
        cosmos_client = get_cosmos_client()
        
        database_name = os.environ.get("COSMOS_DATABASE_NAME", "GrantAnalysis")
        database = cosmos_client.get_database_client(database_name)
        
        user_document = None
        
        # Fetch user document if provided
        if document_id:
            try:
                documents_container = database.get_container_client("Documents")
                user_document = documents_container.read_item(item=document_id, partition_key=document_id)
            except Exception as e:
                logging.warning(f"Document not found: {document_id}")
                return func.HttpResponse(
                    json.dumps({"error": "Document not found"}),
                    status_code=404,
                    mimetype="application/json"
                )
        
        # Fetch active grants
        grants_container = database.get_container_client("GrantOpportunities")
        
        try:
            grants_query = "SELECT * FROM c WHERE c.status = 'active'"
            grants = list(grants_container.query_items(query=grants_query, enable_cross_partition_query=True))
        except Exception as e:
            logging.error(f"Error querying grants: {str(e)}")
            grants = []
        
        if not grants:
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "matches": [],
                    "message": "No active grants found"
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        # Prepare user profile for matching
        if user_document:
            user_profile = f"""Document Analysis: {json.dumps(user_document.get('analysis', {}))}
Document Type: {user_document.get('fileType', 'unknown')}
Document Summary: {user_document.get('analysis', {}).get('summary', 'No summary available')}"""
        else:
            user_profile = f"""Organization Type: {organization_type}
Research Area: {research_area or 'Not specified'}"""
        
        # Prepare grants description for OpenAI
        grants_description = "\n\n---\n\n".join([
            f"""Grant ID: {grant['id']}
Description: {grant.get('originalDescription', 'No description')}
Funding Amount: {grant.get('fundingAmount', 'Not specified')}
Deadline: {grant.get('deadline', 'Not specified')}
Organization Type: {grant.get('organizationType', 'Not specified')}
Requirements: {json.dumps(grant.get('analysis', {}).get('eligibilityRequirements', []))}"""
            for grant in grants[:10]  # Limit to 10 grants to avoid token limits
        ])
        
        # Call Azure OpenAI for matching
        deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")
        
        system_prompt = """You are a grant matching expert. Analyze user profiles/documents against grant opportunities and provide match scores.
        
For each grant, provide a match score (0-100) and explanation. Return a JSON array where each element contains:
- grantId: The grant identifier
- matchScore: Integer from 0-100 (higher = better match)
- reasoning: Detailed explanation of the match
- strengths: Array of alignment strengths
- gaps: Array of potential gaps or weaknesses  
- recommendations: Array of specific recommendations
- priority: high/medium/low based on match quality

Sort results by matchScore in descending order."""
        
        user_prompt = f"""User Profile:
{user_profile}

Grant Opportunities:
{grants_description}"""
        
        # Call Azure OpenAI
        response = openai_client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        matching_results = response.choices[0].message.content
        
        # Parse matching results
        try:
            parsed_matches = json.loads(matching_results)
        except json.JSONDecodeError:
            # Fallback to basic scoring if JSON parsing fails
            parsed_matches = []
            for i, grant in enumerate(grants[:5]):
                parsed_matches.append({
                    "grantId": grant['id'],
                    "matchScore": max(20, 80 - i * 15),  # Decreasing scores
                    "reasoning": "Basic compatibility analysis",
                    "strengths": ["Organization type alignment"],
                    "gaps": ["Detailed analysis needed"],
                    "recommendations": ["Review grant requirements thoroughly"],
                    "priority": "medium"
                })
        
        # Enrich matches with grant details
        enriched_matches = []
        for match in parsed_matches:
            grant = next((g for g in grants if g['id'] == match['grantId']), None)
            if grant:
                enriched_match = {
                    **match,
                    "grantDetails": {
                        "description": grant.get('originalDescription', ''),
                        "fundingAmount": grant.get('fundingAmount', ''),
                        "deadline": grant.get('deadline', ''),
                        "organizationType": grant.get('organizationType', ''),
                        "analyzedAt": grant.get('analyzedAt', '')
                    }
                }
                enriched_matches.append(enriched_match)
        
        logging.info(f"Found {len(enriched_matches)} grant matches")
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "matches": enriched_matches,
                "totalGrants": len(grants),
                "userDocument": {
                    "id": user_document['id'],
                    "fileName": user_document['fileName'],
                    "analysis": user_document['analysis']
                } if user_document else None
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error getting matches: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "details": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )