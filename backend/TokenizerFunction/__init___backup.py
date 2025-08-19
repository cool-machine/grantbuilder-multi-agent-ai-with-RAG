import azure.functions as func
import json
import logging
import os

def simple_tokenize_text(text: str, model: str = "simple", return_tokens: bool = True, return_token_ids: bool = True) -> dict:
    """Simple word-based tokenization for testing"""
    try:
        # Simple word tokenization (split by spaces and punctuation)
        import re
        tokens = re.findall(r'\b\w+\b|\S', text)
        token_ids = [hash(token) % 50257 for token in tokens]  # Simple hash-based IDs
        
        result = {
            "success": True,
            "model": model,
            "text": text,
            "token_count": len(tokens),
            "vocab_size": 50257,
            "special_tokens": {
                "pad_token": "<PAD>",
                "unk_token": "<UNK>",
                "cls_token": None,
                "sep_token": None,
                "mask_token": None
            },
            "note": "This is a simple tokenizer for testing. Full transformers integration coming soon."
        }
        
        # Add tokens and token_ids based on request parameters
        if return_tokens:
            result["tokens"] = tokens
        if return_token_ids:
            result["token_ids"] = token_ids
        
        return result
        
    except Exception as e:
        logging.error(f"Simple tokenization failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model": model,
            "text": text
        }

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main Azure Function entry point"""
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        method = req.method
        
        if method == "GET":
            default_model = os.environ.get('DEFAULT_MODEL', 'simple')
            return func.HttpResponse(
                json.dumps({
                    "message": "Simple Tokenizer API is running",
                    "status": "TESTING MODE - Transformers not yet installed",
                    "default_model": default_model,
                    "supported_methods": ["GET", "POST"],
                    "usage": {
                        "POST": "/api/tokenizerfunction",
                        "body": {
                            "text": "Text to tokenize (required)",
                            "model": "Model name (optional, currently using simple tokenizer)"
                        }
                    }
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
                
                # Accept both 'model' and 'model_name' parameters for compatibility
                model_name = req_body.get('model_name') or req_body.get('model', 'simple')
                return_tokens = req_body.get('return_tokens', True)
                return_token_ids = req_body.get('return_token_ids', True)
                
                # Use simple tokenization for now
                result = simple_tokenize_text(text, model_name, return_tokens, return_token_ids)
                
                status_code = 200 if result.get('success') else 500
                return func.HttpResponse(
                    json.dumps(result, indent=2),
                    mimetype="application/json",
                    status_code=status_code
                )
                
            except ValueError as e:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON in request body"}),
                    mimetype="application/json",
                    status_code=400
                )
            except Exception as e:
                logging.error(f"POST request error: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": f"Request processing failed: {str(e)}"}),
                    mimetype="application/json",
                    status_code=500
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