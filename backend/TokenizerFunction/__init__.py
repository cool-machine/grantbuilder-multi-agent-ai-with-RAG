import azure.functions as func
import json
import logging
import os
from typing import Dict, Any

def call_local_azure_ml_gemma(text: str, analysis_type: str = "general") -> dict:
    """Call local Azure ML Gemma model - NO FALLBACKS"""
    import requests
    import os
    
    # Get Azure ML model endpoint from environment
    azure_ml_endpoint = os.environ.get('AZURE_ML_GEMMA_ENDPOINT')
    
    if not azure_ml_endpoint:
        return {
            "success": False, 
            "error": "AZURE_ML_GEMMA_ENDPOINT environment variable not set",
            "error_type": "configuration_error",
            "required_action": "Set AZURE_ML_GEMMA_ENDPOINT to point to local Gemma model service"
        }
    
    # Create analysis-specific prompt
    if analysis_type == "grant_analysis":
        prompt = f"""You are a grant writing expert. Analyze this grant opportunity and provide structured insights.

Grant Description: {text[:1500]}

Provide:
1. Key eligibility requirements
2. Competitiveness level (low/medium/high)
3. Success factors
4. Recommended applicant profile

Format as clear, actionable insights."""
    elif analysis_type == "document_analysis":
        prompt = f"""You are a document analyzer. Analyze this document and determine its type and key information.

Document Content: {text[:1500]}

Provide:
1. Document type (grant application, grant opportunity, research paper, etc.)
2. Key entities and organizations mentioned
3. Whether this is grant-related (yes/no)
4. Brief summary

Be concise and factual."""
    else:
        prompt = f"""Analyze this text and provide useful insights:

{text[:1500]}

Provide a clear, helpful analysis."""
    
    payload = {
        "prompt": prompt,
        "max_new_tokens": 500,
        "temperature": 0.7,
        "do_sample": True
    }
    
    try:
        logging.info(f"Calling local Azure ML Gemma endpoint: {azure_ml_endpoint}")
        response = requests.post(azure_ml_endpoint, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            logging.info("✅ Local Azure ML Gemma call successful")
            return {"success": True, "response": result.get("generated_text", "")}
        else:
            return {
                "success": False, 
                "error": f"Azure ML Gemma API Error {response.status_code}: {response.text}",
                "error_type": "api_error",
                "endpoint": azure_ml_endpoint
            }
            
    except Exception as e:
        return {
            "success": False, 
            "error": f"Azure ML Gemma connection failed: {str(e)}",
            "error_type": "connection_error",
            "endpoint": azure_ml_endpoint
        }

# REMOVED: analyze_with_gemma_api function (used HuggingFace API)
# All analysis now uses local Azure ML Gemma model

def analyze_grant_with_gemma(text: str, analysis_type: str = "general") -> Dict[str, Any]:
    """Use local Azure ML Gemma model to analyze grant-related text - NO FALLBACKS"""
    
    # Call local Azure ML Gemma model
    result = call_local_azure_ml_gemma(text, analysis_type)
    
    if not result["success"]:
        return {
            "success": False,
            "error": f"LOCAL_GEMMA_FAILED: {result.get('error')}",
            "error_type": result.get("error_type", "unknown"),
            "possible_causes": [
                "Azure ML compute instance not running",
                "AZURE_ML_GEMMA_ENDPOINT not configured",
                "Network connectivity to Azure ML instance",
                "Gemma model service not available"
            ],
            "model": "gemma-3-270m-it",
            "analysis_type": analysis_type,
            "fallback_used": False,
            "api_error": result.get("error"),
            "required_action": result.get("required_action")
        }
    
    # Local model call was successful
    return {
        "success": True,
        "analysis": result["response"],
        "model": "gemma-3-270m-it",
        "analysis_type": analysis_type,
        "source": "azure_ml_local_instance",
        "tokens": None,  # Not provided by our endpoint
        "token_count": len(text.split()),  # Approximate
        "generated_text": result["response"]
    }

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
            "note": "Simple tokenizer with Mistral 7B analysis capability available"
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
    """Main Azure Function entry point with Gemma 3 270M support"""
    logging.info('TokenizerFunction with Gemma 3 270M processed a request.')
    
    try:
        method = req.method
        
        if method == "GET":
            azure_ml_endpoint = os.environ.get('AZURE_ML_GEMMA_ENDPOINT', 'NOT_CONFIGURED')
            return func.HttpResponse(
                json.dumps({
                    "message": "Local Azure ML Gemma 3 270M-IT TokenizerFunction API",
                    "status": "ENHANCED - Local Gemma 3 270M Instruct for grant analysis",
                    "azure_ml_endpoint": azure_ml_endpoint,
                    "supported_methods": ["GET", "POST"],
                    "models": ["simple", "gemma-3-270m-it"],
                    "analysis_types": ["general", "grant_analysis", "document_analysis"],
                    "configuration_required": "AZURE_ML_GEMMA_ENDPOINT environment variable",
                    "usage": {
                        "POST": "/api/tokenizerfunction",
                        "body": {
                            "text": "Text to analyze (required)",
                            "model": "Model name (simple/gemma-3-270m-it)",
                            "analysis_type": "Type of analysis (optional)"
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
                analysis_type = req_body.get('analysis_type', 'general')
                return_tokens = req_body.get('return_tokens', True)
                return_token_ids = req_body.get('return_token_ids', True)
                
                # Check if Gemma analysis is requested
                if model_name in ['gemma-3-270m-it', 'gemma', 'gemma-2-2b'] or analysis_type != 'general':
                    # Use local Azure ML Gemma 3 270M for analysis - NO FALLBACKS
                    result = analyze_grant_with_gemma(text, analysis_type)
                    
                    # Add tokenization info (simple tokenization since local endpoint doesn't provide tokens)
                    if result.get('success') and (return_tokens or return_token_ids):
                        token_result = simple_tokenize_text(text, model_name, return_tokens, return_token_ids)
                        if token_result.get('success'):
                            result.update({
                                "tokens": token_result.get("tokens") if return_tokens else None,
                                "token_ids": token_result.get("token_ids") if return_token_ids else None,
                                "token_count": token_result.get("token_count"),
                                "tokenizer": "simple-approximation"
                            })
                    
                else:
                    # Standard simple tokenization for all other models
                    result = simple_tokenize_text(text, model_name, return_tokens, return_token_ids)
                    result["gemma_available"] = True
                    result["note"] = "Simple tokenization - Use model='gemma-3-270m-it' for AI analysis via local Azure ML instance"
                
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