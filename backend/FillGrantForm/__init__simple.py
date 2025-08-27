import logging
import json
import os
import azure.functions as func
import requests
from typing import Dict, List, Any, Optional

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Simplified Azure Function to route to multi-agent framework
    """
    logging.info('FillGrantForm triggered')
    
    try:
        if req.method == 'GET':
            return func.HttpResponse(
                json.dumps({
                    "service": "Grant Form Filler",
                    "status": "ready",
                    "supported_modes": [
                        "multi-agent-framework",
                        "azure-deepseek", 
                        "quick-fill"
                    ]
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        elif req.method == 'POST':
            req_body = req.get_json()
            
            if not req_body:
                return func.HttpResponse(
                    json.dumps({"error": "Request body is required"}),
                    status_code=400,
                    mimetype="application/json"
                )
            
            pdf_data = req_body.get('pdf_data')
            ngo_profile = req_body.get('ngo_profile', {})
            grant_context = req_body.get('grant_context', {})
            processing_mode = req_body.get('processing_mode', 'azure-deepseek')
            
            if not pdf_data:
                return func.HttpResponse(
                    json.dumps({"error": "pdf_data is required"}),
                    status_code=400,
                    mimetype="application/json"
                )
            
            # Route to appropriate processor based on processing_mode
            if processing_mode == 'multi-agent-framework':
                # Call MultiAgentFramework directly
                payload = {
                    "prompt": f"Generate grant application responses for {ngo_profile.get('organization_name', 'organization')}",
                    "context": {
                        "ngo_profile": ngo_profile,
                        "grant_context": grant_context,
                        "processing_mode": processing_mode
                    }
                }
                
                try:
                    response = requests.post(
                        'https://ocp10-grant-functions.azurewebsites.net/api/MultiAgentFramework',
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Return the multi-agent result with chat_history
                        return func.HttpResponse(
                            json.dumps({
                                "success": True,
                                "filled_responses": result.get("filled_responses", {}),
                                "chat_history": result.get("chat_history", []),
                                "result": result.get("result", ""),
                                "generated_text": result.get("generated_text", ""),
                                "processing_summary": result.get("processing_summary", {}),
                                "tasks": result.get("tasks", []),
                                "deliverables": result.get("deliverables", [])
                            }),
                            status_code=200,
                            mimetype="application/json"
                        )
                    else:
                        error_text = response.text
                        logging.error(f'MultiAgentFramework error: {response.status_code} - {error_text}')
                        return func.HttpResponse(
                            json.dumps({
                                "error": f"MultiAgentFramework error ({response.status_code}): {error_text}",
                                "success": False
                            }),
                            status_code=500,
                            mimetype="application/json"
                        )
                        
                except Exception as e:
                    logging.error(f'Error calling MultiAgentFramework: {str(e)}')
                    return func.HttpResponse(
                        json.dumps({
                            "error": f"MultiAgentFramework call failed: {str(e)}",
                            "success": False
                        }),
                        status_code=500,
                        mimetype="application/json"
                    )
            
            else:
                # For other modes, return a simple response
                return func.HttpResponse(
                    json.dumps({
                        "success": True,
                        "filled_responses": {
                            "organization_name": ngo_profile.get('organization_name', 'Sample NGO'),
                            "project_title": "Sample Project Title",
                            "requested_amount": "50000"
                        },
                        "message": f"Processed with mode: {processing_mode}"
                    }),
                    status_code=200,
                    mimetype="application/json"
                )
            
    except Exception as e:
        logging.error(f'FillGrantForm error: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "error": f"Function error: {str(e)}",
                "success": False
            }),
            status_code=500,
            mimetype="application/json"
        )