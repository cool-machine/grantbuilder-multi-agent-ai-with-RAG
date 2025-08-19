import azure.functions as func
import requests
import json
import logging
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to proxy requests to Gemma Flask API on VM
    """
    logging.info('🔄 GemmaProxy function triggered')
    
    try:
        # Get configuration
        flask_endpoint = os.environ.get('AZURE_ML_GEMMA_ENDPOINT', 'http://10.0.0.4:8000/generate')
        auth_key = os.environ.get('AZURE_ML_GEMMA_KEY', '')
        
        # Determine API type
        is_managed_endpoint = 'inference.ml.azure.com' in flask_endpoint
        is_flask_api = flask_endpoint.startswith('http://10.0.0.4:8000') or flask_endpoint.startswith('http://132.196.98.227:8000')
        
        # Handle GET requests (health check)
        if req.method == 'GET':
            if is_managed_endpoint:
                # Managed endpoints don't have health endpoints, so return basic status
                return func.HttpResponse(
                    json.dumps({
                        "proxy_status": "healthy",
                        "target_status": "managed_endpoint",
                        "endpoint": flask_endpoint,
                        "model": "gemma-3-270m-it",
                        "type": "azure_ml_managed"
                    }),
                    status_code=200,
                    mimetype="application/json"
                )
            else:
                # Flask API health check
                health_url = flask_endpoint.replace('/generate', '/health')
                try:
                    response = requests.get(health_url, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        result['proxy_status'] = 'healthy'
                        return func.HttpResponse(
                            json.dumps(result),
                            status_code=200,
                            mimetype="application/json"
                        )
                    else:
                        return func.HttpResponse(
                            json.dumps({
                                "error": f"Flask API returned status {response.status_code}",
                                "proxy_status": "healthy",
                                "target_status": "error"
                            }),
                            status_code=502,
                            mimetype="application/json"
                        )
                except Exception as e:
                    return func.HttpResponse(
                        json.dumps({
                            "error": f"Cannot reach Flask API: {str(e)}",
                            "proxy_status": "healthy", 
                            "target_status": "unreachable",
                            "endpoint": flask_endpoint
                        }),
                        status_code=502,
                        mimetype="application/json"
                    )
        
        # Handle POST requests (text generation)
        elif req.method == 'POST':
            try:
                # Get request body
                req_body = req.get_json()
                if not req_body:
                    return func.HttpResponse(
                        json.dumps({"error": "No JSON body provided", "success": False}),
                        status_code=400,
                        mimetype="application/json"
                    )
                
                logging.info(f'📤 Forwarding request to: {flask_endpoint}')
                
                if is_managed_endpoint:
                    # Azure ML Managed Endpoint format
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {auth_key}'
                    }
                    
                    # Convert Flask API format to managed endpoint format
                    managed_payload = {
                        "input_data": {
                            "input_string": [req_body.get('prompt', '')],
                            "parameters": {
                                "max_new_tokens": req_body.get('max_new_tokens', 150),
                                "temperature": req_body.get('temperature', 0.7),
                                "do_sample": req_body.get('do_sample', True)
                            }
                        }
                    }
                    
                    response = requests.post(
                        flask_endpoint,
                        json=managed_payload,
                        timeout=60,
                        headers=headers
                    )
                else:
                    # Flask API format
                    response = requests.post(
                        flask_endpoint,
                        json=req_body,
                        timeout=60,  # 60 seconds for model generation
                        headers={'Content-Type': 'application/json'}
                    )
                
                logging.info(f'📥 Received response with status: {response.status_code}')
                
                if response.status_code == 200:
                    if is_managed_endpoint:
                        # Convert managed endpoint response to Flask API format
                        managed_response = response.json()
                        flask_format = {
                            "generated_text": managed_response.get('output', ''),
                            "model": "gemma-3-270m-it",
                            "success": True,
                            "source": "azure_ml_managed"
                        }
                        return func.HttpResponse(
                            json.dumps(flask_format),
                            status_code=200,
                            mimetype="application/json"
                        )
                    else:
                        # Flask API response - return as is
                        return func.HttpResponse(
                            response.text,
                            status_code=response.status_code,
                            mimetype="application/json"
                        )
                else:
                    # Error response
                    return func.HttpResponse(
                        response.text,
                        status_code=response.status_code,
                        mimetype="application/json"
                    )
                
            except requests.exceptions.Timeout:
                return func.HttpResponse(
                    json.dumps({
                        "error": "Request timeout - model generation took too long",
                        "success": False
                    }),
                    status_code=504,
                    mimetype="application/json"
                )
            except Exception as e:
                logging.error(f'❌ Proxy error: {str(e)}')
                return func.HttpResponse(
                    json.dumps({
                        "error": f"Proxy error: {str(e)}",
                        "success": False,
                        "endpoint": flask_endpoint
                    }),
                    status_code=500,
                    mimetype="application/json"
                )
        
        else:
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed", "allowed": ["GET", "POST"]}),
                status_code=405,
                mimetype="application/json"
            )
            
    except Exception as e:
        logging.error(f'❌ GemmaProxy function error: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "error": f"Function error: {str(e)}",
                "success": False
            }),
            status_code=500,
            mimetype="application/json"
        )