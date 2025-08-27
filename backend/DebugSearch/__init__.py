import logging
import json
import os
import requests
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Debug function to test Brave Search API directly
    """
    logging.info('DebugSearch function triggered')
    
    try:
        if req.method == 'GET':
            # Test basic connectivity
            api_key = os.getenv('BRAVE_SEARCH_API_KEY')
            
            return func.HttpResponse(
                json.dumps({
                    "service": "Search Debug Tool",
                    "api_key_present": bool(api_key),
                    "api_key_length": len(api_key) if api_key else 0,
                    "api_key_prefix": api_key[:8] + "..." if api_key else None
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        elif req.method == 'POST':
            req_body = req.get_json()
            query = req_body.get('query', 'test search')
            
            # Get API key
            api_key = os.getenv('BRAVE_SEARCH_API_KEY')
            
            if not api_key:
                return func.HttpResponse(
                    json.dumps({"error": "No API key found"}),
                    status_code=400,
                    mimetype="application/json"
                )
            
            # Test different API configurations
            test_results = []
            
            # Test 1: Basic search with minimal params
            try:
                search_url = "https://api.search.brave.com/res/v1/web/search"
                headers = {
                    "Accept": "application/json",
                    "X-Subscription-Token": api_key
                }
                params = {"q": query}
                
                response = requests.get(search_url, headers=headers, params=params, timeout=10)
                
                test_results.append({
                    "test": "Basic search",
                    "status_code": response.status_code,
                    "headers_sent": dict(headers),
                    "params_sent": params,
                    "response_headers": dict(response.headers),
                    "response_text": response.text[:500] if response.text else None,
                    "url_called": response.url
                })
                
            except Exception as e:
                test_results.append({
                    "test": "Basic search",
                    "error": str(e)
                })
            
            # Test 2: With Accept-Encoding
            try:
                headers = {
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": api_key
                }
                params = {"q": query, "count": 3}
                
                response = requests.get(search_url, headers=headers, params=params, timeout=10)
                
                test_results.append({
                    "test": "With Accept-Encoding",
                    "status_code": response.status_code,
                    "response_text": response.text[:500] if response.text else None
                })
                
            except Exception as e:
                test_results.append({
                    "test": "With Accept-Encoding", 
                    "error": str(e)
                })
            
            # Test 3: Check API key format
            test_results.append({
                "test": "API Key Analysis",
                "key_length": len(api_key),
                "key_starts_with": api_key[:3] if len(api_key) > 3 else api_key,
                "key_contains_invalid_chars": any(c in api_key for c in [' ', '\n', '\r', '\t'])
            })
            
            return func.HttpResponse(
                json.dumps({
                    "query_tested": query,
                    "test_results": test_results
                }),
                status_code=200,
                mimetype="application/json"
            )
            
    except Exception as e:
        logging.error(f'DebugSearch error: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "error": f"Debug function error: {str(e)}"
            }),
            status_code=500,
            mimetype="application/json"
        )