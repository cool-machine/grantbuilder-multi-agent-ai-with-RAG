#!/usr/bin/env python3
"""
Test script for FillGrantForm function to debug 500 errors
"""

import json
import requests

# Test data based on frontend defaults
test_data = {
    "pdf_data": "JVBERi0xLjQKJcfsj6IKNSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgNCAwIFI+PgplbmRvYmoKNCAwIG9iago8PC9UeXBlL1BhZ2VzL0tpZHMgWzMgMCBSXS9Db3VudCAxPj4KZW5kb2JqCjMgMCBvYmoKPDwvVHlwZS9QYWdlL01lZGlhQm94IFswIDAgNjEyIDc5Ml0vUGFyZW50IDQgMCBSL1Jlc291cmNlczw8L0ZvbnQgPDwvRjEgMSAwIFI+Pj4+L0NvbnRlbnRzIDIgMCBSPj4KZW5kb2JqCjEgMCBvYmoKPDwvVHlwZS9Gb250L1N1YnR5cGUvVHlwZTEvQmFzZUZvbnQvSGVsdmV0aWNhPj4KZW5kb2JqCjIgMCBvYmoKPDwvTGVuZ3RoIDQ0Pj4Kc3RyZWFtCkJUCi9GMSA0OCBUZgo3MiA3MjAgVGQKKFRlc3QgUERGKSBUagpFVApzdHJlYW0KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDI1NiAwMDAwMCBuIAowMDAwMDAwMzEzIDAwMDAwIG4gCjAwMDAwMDAwOTMgMDAwMDAgbiAKMDAwMDAwMDAzOSAwMDAwMCBuIAowMDAwMDAwMDEwIDAwMDAwIG4gCnRyYWlsZXIKPDwvU2l6ZSA2L1Jvb3QgNSAwIFI+PgpzdGFydHhyZWYKNDA0CiUlRU9G",  # Simple test PDF in base64
    "ngo_profile": {
        "organization_name": "Teach for America Appalachia",
        "contact_email": "info@teachforamerica.org", 
        "phone": "(212) 279-2080",
        "mission": "Find, develop, and support equity-oriented leaders to transform education and expand opportunity for all children",
        "years_active": 35,
        "focus_areas": ["education", "teacher training", "rural education", "equity"],
        "annual_budget": 245000000,
        "recent_projects": "Strengthening teacher pipelines in rural Appalachian communities"
    },
    "grant_context": {
        "funder_name": "Appalachian Regional Commission",
        "focus_area": "rural education and teacher training", 
        "max_amount": 500000,
        "requirements": "Must serve rural Appalachian communities with measurable teacher placement outcomes"
    },
    "data_sources": {
        "has_profile_pdf": False,
        "has_website": True,
        "website_url": "https://www.teachforamerica.org/"
    }
}

def test_fillgrantform():
    """Test the fillgrantform endpoint"""
    url = "https://ocp10-grant-functions.azurewebsites.net/api/fillgrantform"
    
    print("Testing FillGrantForm endpoint...")
    print(f"URL: {url}")
    print(f"Data size: {len(json.dumps(test_data))} bytes")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutes
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Result keys: {list(result.keys())}")
            if 'processing_summary' in result:
                print(f"Processing Summary: {result['processing_summary']}")
        else:
            print("❌ Error!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_fillgrantform()