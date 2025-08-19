import azure.functions as func
import json
import logging
import os
from typing import Dict, Any

def load_mistral_tokenizer_only():
    """Load just Mistral's tokenizer for tokenization tasks (lighter than full model)"""
    try:
        from transformers import AutoTokenizer
        
        model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        logging.info("Loading Mistral tokenizer only...")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        logging.info("✅ Mistral tokenizer loaded successfully")
        return tokenizer
        
    except ImportError as e:
        logging.error(f"❌ IMPORT_ERROR: transformers not installed: {e}")
        return None
    except Exception as e:
        logging.error(f"❌ TOKENIZER_LOAD_ERROR: {e}")
        return None

def load_mistral_model():
    """Load Mistral 7B model for grant analysis tasks - with detailed error reporting"""
    try:
        # Import Hugging Face transformers
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        import torch
        
        model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        
        # Check if GPU is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Loading Mistral 7B model on device: {device}")
        
        # Detailed memory check
        if device == "cuda":
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            logging.info(f"GPU memory available: {total_memory:.1f}GB")
            if total_memory < 12:
                logging.warning(f"GPU memory may be insufficient for Mistral 7B (need 12GB+)")
        
        # Load tokenizer and model with detailed logging
        logging.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        logging.info("Loading model (this may take 30-60 seconds)...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
            trust_remote_code=True
        )
        
        logging.info("Creating text generation pipeline...")
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0 if device == "cuda" else -1,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        
        logging.info("✅ Mistral 7B model loaded successfully")
        return generator, tokenizer
        
    except ImportError as e:
        logging.error(f"❌ IMPORT_ERROR: Required packages not installed: {e}")
        logging.error("Install with: pip install torch transformers accelerate sentencepiece")
        return None, None
    except torch.cuda.OutOfMemoryError as e:
        logging.error(f"❌ CUDA_OOM: GPU out of memory: {e}")
        logging.error("Try: reduce model precision or use CPU inference")
        return None, None
    except Exception as e:
        logging.error(f"❌ MODEL_LOAD_ERROR: Error loading Mistral model: {e}")
        logging.error(f"Error type: {type(e).__name__}")
        return None, None

def analyze_grant_with_mistral(text: str, analysis_type: str = "general") -> Dict[str, Any]:
    """Use Mistral 7B to analyze grant-related text"""
    
    generator, tokenizer = load_mistral_model()
    
    if generator is None:
        # EXPLICIT FAILURE - No fallback, clear error reporting
        return {
            "success": False,
            "error": "MISTRAL_MODEL_LOAD_FAILED: Model could not be loaded",
            "error_type": "model_loading_failure",
            "possible_causes": [
                "Insufficient memory (need 16GB+)",
                "Missing dependencies (transformers, torch)",
                "CUDA/GPU issues",
                "Model download timeout",
                "Azure Function resource limits"
            ],
            "model": "mistral-7b-instruct",
            "analysis_type": analysis_type,
            "fallback_used": False
        }
    
    try:
        # Create prompt based on analysis type
        if analysis_type == "grant_analysis":
            prompt = f"""<s>[INST] You are a grant writing expert. Analyze this grant opportunity and provide structured insights.

Grant Description: {text[:1500]}

Please provide:
1. Key eligibility requirements
2. Competitiveness level (low/medium/high)
3. Success factors
4. Recommended applicant profile

Format your response as clear, actionable insights. [/INST]"""

        elif analysis_type == "document_analysis":
            prompt = f"""<s>[INST] You are a document analyzer. Analyze this document and determine its type and key information.

Document Content: {text[:1500]}

Please provide:
1. Document type (grant application, grant opportunity, research paper, etc.)
2. Key entities and organizations mentioned
3. Whether this is grant-related (yes/no)
4. Brief summary

Be concise and factual. [/INST]"""

        else:
            prompt = f"""<s>[INST] Analyze this text and provide useful insights:

{text[:1500]}

Provide a clear, helpful analysis. [/INST]"""

        # Generate response
        response = generator(
            prompt,
            max_new_tokens=500,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        # Extract the generated text
        generated_text = response[0]["generated_text"]
        # Remove the prompt part
        analysis_text = generated_text.split("[/INST]")[-1].strip()
        
        return {
            "success": True,
            "analysis": analysis_text,
            "model": "mistral-7b-instruct",
            "analysis_type": analysis_type,
            "input_length": len(text),
            "tokens_used": len(tokenizer.encode(prompt + analysis_text))
        }
        
    except Exception as e:
        logging.error(f"Mistral analysis failed: {e}")
        return {
            "success": False,
            "error": f"MISTRAL_GENERATION_FAILED: {str(e)}",
            "error_type": "generation_failure",
            "possible_causes": [
                "Out of memory during inference",
                "CUDA out of memory",
                "Input text too long",
                "Model inference timeout",
                "Token generation error"
            ],
            "model": "mistral-7b-instruct",
            "analysis_type": analysis_type,
            "input_length": len(text),
            "fallback_used": False
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
    """Main Azure Function entry point with Mistral 7B support"""
    logging.info('TokenizerFunction with Mistral 7B processed a request.')
    
    try:
        method = req.method
        
        if method == "GET":
            default_model = os.environ.get('DEFAULT_MODEL', 'mistral-7b')
            return func.HttpResponse(
                json.dumps({
                    "message": "Mistral 7B TokenizerFunction API is running",
                    "status": "ENHANCED - Mistral 7B available for grant analysis",
                    "default_model": default_model,
                    "supported_methods": ["GET", "POST"],
                    "models": ["simple", "mistral-7b-instruct"],
                    "analysis_types": ["general", "grant_analysis", "document_analysis"],
                    "usage": {
                        "POST": "/api/tokenizerfunction",
                        "body": {
                            "text": "Text to analyze (required)",
                            "model": "Model name (simple/mistral-7b-instruct)",
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
                
                # Check if Mistral analysis is requested
                if model_name in ['mistral-7b', 'mistral-7b-instruct', 'mistral'] or analysis_type != 'general':
                    # Use Mistral 7B for analysis - NO FALLBACK
                    result = analyze_grant_with_mistral(text, analysis_type)
                    
                    # Add tokenization info using Mistral's own tokenizer (if succeeded AND tokens requested)
                    if result.get('success') and (return_tokens or return_token_ids):
                        try:
                            # Use Mistral's tokenizer for accurate token info
                            generator, tokenizer = load_mistral_model()
                            if tokenizer is not None:
                                encoded = tokenizer.encode(text)
                                tokens = tokenizer.convert_ids_to_tokens(encoded) if return_tokens else None
                                
                                result.update({
                                    "tokens": tokens,
                                    "token_ids": encoded if return_token_ids else None,
                                    "token_count": len(encoded),
                                    "tokenizer": "mistral-sentencepiece",
                                    "vocab_size": tokenizer.vocab_size
                                })
                            else:
                                # Fallback to simple tokenization only for token info
                                token_result = simple_tokenize_text(text, model_name, return_tokens, return_token_ids)
                                if token_result.get('success'):
                                    result.update({
                                        "tokens": token_result.get("tokens") if return_tokens else None,
                                        "token_ids": token_result.get("token_ids") if return_token_ids else None,
                                        "token_count": token_result.get("token_count"),
                                        "tokenizer": "simple-fallback"
                                    })
                        except Exception as e:
                            logging.warning(f"Mistral tokenization failed, using simple: {e}")
                            # Use simple tokenization as last resort for token info only
                            token_result = simple_tokenize_text(text, model_name, return_tokens, return_token_ids)
                            if token_result.get('success'):
                                result.update({
                                    "tokens": token_result.get("tokens") if return_tokens else None,
                                    "token_ids": token_result.get("token_ids") if return_token_ids else None,
                                    "token_count": token_result.get("token_count"),
                                    "tokenizer": "simple-fallback"
                                })
                    
                    # If Mistral failed, do NOT fallback to simple tokenization
                    # Return the Mistral error with clear diagnostics
                    
                else:
                    # Explicitly requested simple tokenization - but offer Mistral tokenizer option
                    if model_name == "mistral-tokenizer-only":
                        # Use just Mistral's tokenizer without the full model
                        try:
                            tokenizer = load_mistral_tokenizer_only()
                            if tokenizer is not None:
                                encoded = tokenizer.encode(text)
                                tokens = tokenizer.convert_ids_to_tokens(encoded) if return_tokens else None
                                
                                result = {
                                    "success": True,
                                    "model": "mistral-tokenizer-only",
                                    "text": text,
                                    "tokens": tokens,
                                    "token_ids": encoded if return_token_ids else None,
                                    "token_count": len(encoded),
                                    "tokenizer": "mistral-sentencepiece",
                                    "vocab_size": tokenizer.vocab_size,
                                    "note": "Mistral tokenizer only - no analysis. Use model='mistral-7b-instruct' for full analysis"
                                }
                            else:
                                result = simple_tokenize_text(text, model_name, return_tokens, return_token_ids)
                                result["error"] = "Mistral tokenizer failed to load"
                        except Exception as e:
                            result = simple_tokenize_text(text, model_name, return_tokens, return_token_ids)
                            result["error"] = f"Mistral tokenizer error: {str(e)}"
                    else:
                        # Standard simple tokenization
                        result = simple_tokenize_text(text, model_name, return_tokens, return_token_ids)
                        result["mistral_available"] = True
                        result["note"] = "Simple tokenization - Mistral options: model='mistral-7b-instruct' (full analysis) or model='mistral-tokenizer-only' (tokenization)"
                
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