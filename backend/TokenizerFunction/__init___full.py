import azure.functions as func
import json
import logging
import os
from transformers import AutoTokenizer
from typing import Optional, Dict, Any

# Global tokenizer cache to avoid reloading
_tokenizer_cache = {}

def get_tokenizer(model_name: str) -> AutoTokenizer:
    """Get or load tokenizer with caching"""
    if model_name not in _tokenizer_cache:
        try:
            logging.info(f"Loading tokenizer for model: {model_name}")
            _tokenizer_cache[model_name] = AutoTokenizer.from_pretrained(model_name)
            logging.info(f"Successfully loaded tokenizer for {model_name}")
        except Exception as e:
            logging.error(f"Failed to load tokenizer for {model_name}: {str(e)}")
            raise e
    return _tokenizer_cache[model_name]

def tokenize_text(text: str, model_name: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Tokenize text using the specified model"""
    if options is None:
        options = {}
    
    try:
        tokenizer = get_tokenizer(model_name)
        
        # Tokenize the text
        tokens = tokenizer.tokenize(text)
        token_ids = tokenizer.encode(text, add_special_tokens=options.get('add_special_tokens', True))
        
        # Additional tokenizer information
        result = {
            "success": True,
            "model": model_name,
            "text": text,
            "tokens": tokens,
            "token_ids": token_ids,
            "token_count": len(token_ids),
            "vocab_size": tokenizer.vocab_size,
            "special_tokens": {
                "pad_token": tokenizer.pad_token,
                "unk_token": tokenizer.unk_token,
                "cls_token": getattr(tokenizer, 'cls_token', None),
                "sep_token": getattr(tokenizer, 'sep_token', None),
                "mask_token": getattr(tokenizer, 'mask_token', None)
            }
        }
        
        # Optional: decode tokens back to verify
        if options.get('include_decoded', False):
            decoded_text = tokenizer.decode(token_ids)
            result["decoded_text"] = decoded_text
            
        return result
        
    except Exception as e:
        logging.error(f"Tokenization failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model": model_name,
            "text": text
        }

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main Azure Function entry point"""
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        # Get the request method
        method = req.method
        
        if method == "GET":
            # GET request - return API information
            default_model = os.environ.get('DEFAULT_MODEL', 'openai/gpt-oss-120b')
            return func.HttpResponse(
                json.dumps({
                    "message": "Tokenizer API is running",
                    "default_model": default_model,
                    "supported_methods": ["GET", "POST"],
                    "usage": {
                        "POST": "/api/TokenizerFunction",
                        "body": {
                            "text": "Text to tokenize (required)",
                            "model": f"Model name (optional, default: {default_model})",
                            "options": {
                                "add_special_tokens": "bool (optional, default: True)",
                                "include_decoded": "bool (optional, default: False)"
                            }
                        }
                    }
                }, indent=2),
                mimetype="application/json",
                status_code=200
            )
        
        elif method == "POST":
            # POST request - perform tokenization
            try:
                req_body = req.get_json()
                if not req_body:
                    return func.HttpResponse(
                        json.dumps({"error": "Request body must be JSON"}),
                        mimetype="application/json",
                        status_code=400
                    )
                
                # Extract parameters
                text = req_body.get('text', '')
                if not text:
                    return func.HttpResponse(
                        json.dumps({"error": "Text parameter is required"}),
                        mimetype="application/json",
                        status_code=400
                    )
                
                model_name = req_body.get('model', os.environ.get('DEFAULT_MODEL', 'openai/gpt-oss-120b'))
                options = req_body.get('options', {})
                
                # Perform tokenization
                result = tokenize_text(text, model_name, options)
                
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
                logging.error(f"Unexpected error: {str(e)}")
                return func.HttpResponse(
                    json.dumps({"error": f"Internal server error: {str(e)}"}),
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