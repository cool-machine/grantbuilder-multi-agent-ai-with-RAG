import azure.functions as func
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Simple test version without transformers"""
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        method = req.method
        
        if method == "GET":
            return func.HttpResponse(
                json.dumps({
                    "message": "Simple Tokenizer Test API is running",
                    "status": "OK",
                    "python_version": "Test mode - no transformers yet",
                    "supported_methods": ["GET", "POST"]
                }, indent=2),
                mimetype="application/json",
                status_code=200
            )
        
        elif method == "POST":
            try:
                req_body = req.get_json()
                if not req_body:
                    return func.HttpResponse(
                        json.dumps({"error": "Request body must be JSON"}),
                        mimetype="application/json",
                        status_code=400
                    )
                
                text = req_body.get('text', '')
                if not text:
                    return func.HttpResponse(
                        json.dumps({"error": "Text parameter is required"}),
                        mimetype="application/json",
                        status_code=400
                    )
                
                # Simple tokenization (just split by spaces for testing)
                simple_tokens = text.split()
                
                result = {
                    "success": True,
                    "mode": "simple_test",
                    "text": text,
                    "simple_tokens": simple_tokens,
                    "token_count": len(simple_tokens),
                    "message": "This is a test version. Full transformers integration coming next."
                }
                
                return func.HttpResponse(
                    json.dumps(result, indent=2),
                    mimetype="application/json",
                    status_code=200
                )
                
            except ValueError as e:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )
        
        else:
            return func.HttpResponse(
                json.dumps({"error": f"Method {method} not allowed"}),
                mimetype="application/json",
                status_code=405
            )
            
    except Exception as e:
        logging.error(f"Function execution error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Function execution failed: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )