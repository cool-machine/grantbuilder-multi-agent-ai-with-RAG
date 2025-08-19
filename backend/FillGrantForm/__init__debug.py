import logging
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Debug version to test imports one by one
    """
    logging.info('Debug FillGrantForm function called')
    
    try:
        # Test basic imports first
        import os
        import tempfile
        from typing import Dict, List, Any, Optional
        import io
        import base64
        from datetime import datetime
        
        result = {"status": "basic_imports_ok"}
        
        # Test Azure imports
        try:
            from azure.storage.blob import BlobServiceClient
            from azure.cosmos import CosmosClient
            result["azure_imports"] = "ok"
        except Exception as e:
            result["azure_imports"] = f"failed: {str(e)}"
        
        # Test PyPDF2
        try:
            import PyPDF2
            result["pypdf2_import"] = "ok"
        except Exception as e:
            result["pypdf2_import"] = f"failed: {str(e)}"
        
        # Test OpenAI
        try:
            from openai import AzureOpenAI
            result["openai_import"] = "ok"
        except Exception as e:
            result["openai_import"] = f"failed: {str(e)}"
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Debug function error: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e), "type": type(e).__name__}),
            status_code=500,
            mimetype="application/json"
        )