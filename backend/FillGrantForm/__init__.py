import logging
import json
import os
import tempfile
from typing import Dict, List, Any, Optional
import azure.functions as func
# Remove problematic Azure imports that cause GLIBC issues
# from azure.storage.blob import BlobServiceClient  
# from azure.cosmos import CosmosClient
import PyPDF2
import io
import base64
from datetime import datetime

# For LLM integration - using free Hugging Face API
import requests

def call_local_gemma_model(prompt: str, processing_mode: str = 'azure-deepseek') -> dict:
    """Call AI Foundry Agent Service - Multi-Agent Intelligence"""
    
    # Connect to AI Foundry Agent Orchestrator for intelligent multi-agent processing
    import requests
    import os
    
    # Use the new AgentOrchestrator for superior multi-agent grant writing
    # This provides General Manager + Specialist agents instead of single GPT
    
    payload = {
        "prompt": prompt,
        "max_new_tokens": 300,
        "temperature": 0.7,
        "debug": True,  # Enable agent dialogue visualization for debugging
        "context": {
            "field_name": prompt.split("for the field")[1].split("'")[1] if "for the field" in prompt else "unknown",
            "processing_mode": "enhanced_multiagent"
        }
    }
    
    try:
        import time
        import random
        
        # Connect to appropriate orchestrator based on processing mode
        if processing_mode == 'azure-deepseek':
            proxy_url = 'https://ocp10-grant-functions.azurewebsites.net/api/EnhancedAgentOrchestrator'
        elif processing_mode == 'o3-multimodal':
            proxy_url = 'https://ocp10-grant-functions.azurewebsites.net/api/O3MultimodalProcessor'  # Future implementation
        else:  # quick-fill or default
            proxy_url = 'https://ocp10-grant-functions.azurewebsites.net/api/ModelProxy'
        
        # Implement retry logic for rate limiting (HTTP 429)
        max_retries = 3
        base_delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Calling AgentOrchestrator for AI Foundry multi-agent system (attempt {attempt + 1}/{max_retries}): {proxy_url}")
                response = requests.post(proxy_url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 🐛 DEBUG: Log enhanced system response
                    logging.info(f"🤖 ENHANCED AGENT RESPONSE: {json.dumps(result, indent=2)}")
                    
                    # Extract and log agent dialogue if available
                    if result.get("debug_info", {}).get("agent_dialogue"):
                        logging.info(f"🗨️ AGENT DIALOGUE:")
                        for dialogue in result["debug_info"]["agent_dialogue"]:
                            logging.info(f"   {dialogue.get('agent', 'Unknown')}: {dialogue.get('message', 'No message')[:200]}...")
                    
                    # Extract and log decision tree if available
                    if result.get("debug_info", {}).get("decision_tree"):
                        logging.info(f"🌳 DECISION TREE: {json.dumps(result['debug_info']['decision_tree'], indent=2)}")
                    
                    return {"success": True, "text": result.get("generated_text", ""), "debug_info": result.get("debug_info")}
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    if attempt < max_retries - 1:  # Don't sleep on last attempt
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                        logging.warning(f"Rate limited (429), waiting {delay:.2f}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        # Last attempt failed with 429
                        return {
                            "success": False, 
                            "error": f"AI Foundry Agent Service rate limit exceeded after {max_retries} attempts. Please try again in a few minutes.",
                            "error_type": "rate_limit_error",
                            "endpoint": proxy_url,
                            "status_code": response.status_code,
                            "retry_after": "60 seconds"
                        }
                else:
                    # Other error - don't retry
                    return {
                        "success": False, 
                        "error": f"AI Foundry Agent Service Error {response.status_code}: {response.text}",
                        "error_type": "api_error",
                        "endpoint": proxy_url,
                        "status_code": response.status_code
                    }
            except requests.exceptions.RequestException as req_error:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logging.warning(f"Request error on attempt {attempt + 1}, retrying in {delay}s: {str(req_error)}")
                    time.sleep(delay)
                    continue
                else:
                    raise req_error
            
    except Exception as e:
        return {
            "success": False, 
            "error": f"AI Foundry Agent Service connection failed: {str(e)}",
            "error_type": "connection_error",
            "endpoint": proxy_url
        }

# PDF utilities
# Lazy imports to prevent startup failures if dependencies are missing
# from .pdf_utils import PDFFormFiller, PDFFormAnalyzer

def enhance_ngo_profile(base_profile: Dict, data_sources: Dict, ngo_profile_pdf: str = None) -> Dict:
    """
    Enhance NGO profile with data from multiple sources
    """
    enhanced_profile = base_profile.copy()
    
    # Add source tracking
    enhanced_profile['data_sources_used'] = []
    
    # Process NGO profile PDF if provided
    if data_sources.get('has_profile_pdf') and ngo_profile_pdf:
        try:
            pdf_extracted_data = extract_ngo_data_from_pdf(ngo_profile_pdf)
            if pdf_extracted_data:
                # Merge PDF data into profile
                for key, value in pdf_extracted_data.items():
                    if value and (not enhanced_profile.get(key) or len(str(value)) > len(str(enhanced_profile.get(key, '')))):
                        enhanced_profile[key] = value
                enhanced_profile['data_sources_used'].append('profile_pdf')
                logging.info("Enhanced NGO profile with PDF data")
        except Exception as e:
            logging.warning(f"Failed to extract data from NGO profile PDF: {str(e)}")
    
    # Process website data if provided
    if data_sources.get('has_website') and data_sources.get('website_url'):
        try:
            website_data = extract_ngo_data_from_website(data_sources['website_url'])
            if website_data:
                # Merge website data (lower priority than PDF)
                for key, value in website_data.items():
                    if value and not enhanced_profile.get(key):
                        enhanced_profile[key] = value
                enhanced_profile['data_sources_used'].append('website')
                logging.info("Enhanced NGO profile with website data")
        except Exception as e:
            logging.warning(f"Failed to extract data from website: {str(e)}")
    
    # Add manual entry source if no other sources
    if not enhanced_profile.get('data_sources_used'):
        enhanced_profile['data_sources_used'].append('manual_entry')
    
    return enhanced_profile

def create_simple_pdf_response(filled_responses: Dict[str, str]) -> str:
    """
    Create a valid minimal PDF using basic PDF structure (not base64 text!)
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        # Create a proper PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Add title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 100, "FILLED GRANT APPLICATION")
        
        # Add content
        p.setFont("Helvetica", 12)
        y_position = height - 150
        
        for field, response in filled_responses.items():
            # Field name
            p.setFont("Helvetica-Bold", 12)
            field_name = field.replace('_', ' ').title() + ":"
            p.drawString(100, y_position, field_name)
            y_position -= 20
            
            # Field value (wrap long text)
            p.setFont("Helvetica", 10)
            words = response.split()
            line = ""
            for word in words:
                if len(line + word) < 80:  # Rough character limit per line
                    line += word + " "
                else:
                    p.drawString(120, y_position, line)
                    y_position -= 15
                    line = word + " "
                    if y_position < 100:  # Start new page if needed
                        p.showPage()
                        y_position = height - 100
                        p.setFont("Helvetica", 10)
            
            if line:  # Draw remaining text
                p.drawString(120, y_position, line)
                y_position -= 30
                
            if y_position < 100:  # Start new page if needed
                p.showPage()
                y_position = height - 100
        
        p.save()
        
        # Get PDF bytes and encode to base64
        buffer.seek(0)
        pdf_bytes = buffer.read()
        return base64.b64encode(pdf_bytes).decode('utf-8')
        
    except Exception as e:
        logging.error(f"Failed to create simple PDF with reportlab: {str(e)}")
        # NO FALLBACKS - let PDF creation fail explicitly
        raise Exception(f"PDF creation with reportlab failed: {str(e)}")

# REMOVED: create_minimal_pdf_fallback function
# PDF generation must succeed with reportlab or fail explicitly

def analyze_pdf_simple(pdf_data: str) -> Dict:
    """
    Simple PDF analysis without complex dependencies - NO FALLBACKS
    """
    pdf_bytes = base64.b64decode(pdf_data)
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    
    return {
        "total_pages": len(pdf_reader.pages),
        "has_form_fields": False,  # Simplified - not checking form fields
        "form_fields": [],
        "analysis_method": "simple"
    }

def extract_ngo_data_from_pdf(pdf_data: str) -> Dict:
    """
    Extract NGO information from uploaded profile PDF
    """
    try:
        # Decode base64 PDF
        pdf_bytes = base64.b64decode(pdf_data)
        
        # Extract text using PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text_content = ""
        
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        # Use local Gemma model to extract structured data from text - NO FALLBACKS
        result = extract_structured_data_with_gemma(text_content, "ngo_profile")
        if not result:
            raise Exception("Failed to extract structured data from PDF using Gemma model")
        return result
            
    except Exception as e:
        logging.error(f"Error extracting data from NGO profile PDF: {str(e)}")
        return {}

def extract_ngo_data_from_website(website_url: str) -> Dict:
    """
    Extract NGO information from website (placeholder for web scraping)
    """
    try:
        # Note: In production, you'd use requests + BeautifulSoup or similar
        # For now, return empty dict as web scraping needs additional dependencies
        logging.info(f"Website data extraction from {website_url} - not implemented yet")
        return {}
    except Exception as e:
        logging.error(f"Error extracting data from website {website_url}: {str(e)}")
        return {}

def extract_structured_data_with_gemma(text_content: str, data_type: str) -> Dict:
    """
    Use free Gemma API to extract structured data from unstructured text
    """
    try:
        if data_type == "ngo_profile":
            prompt = f"""Extract information from this NGO document and return JSON format:

Text: {text_content[:2000]}

Extract these fields as JSON:
- mission: Organization's mission statement
- years_active: Number of years active
- focus_areas: Array of focus areas
- annual_budget: Annual budget (number only)
- recent_projects: Recent projects description
- target_population: Who they serve
- geographic_scope: Areas of operation
- key_achievements: Notable accomplishments

Return only valid JSON."""
            
            result = call_local_gemma_model(prompt, 'azure-deepseek')  # Use enhanced system for data extraction
            
            if not result["success"]:
                raise Exception(f"Local Gemma model failed: {result.get('error')} (Type: {result.get('error_type')})")
            
            # Parse JSON from Gemma response - NO FALLBACKS
            response_text = result["text"].strip()
            if "{" not in response_text or "}" not in response_text:
                raise Exception(f"Gemma response contains no JSON: {response_text[:200]}")
            
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_text = response_text[start:end]
            
            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                raise Exception(f"Gemma response was not valid JSON: {json_text[:200]} - Error: {str(e)}")
                
    except Exception as e:
        logging.error(f"Error extracting structured data with Gemma: {str(e)}")
        return {}

def extract_data_with_keywords(text_content: str) -> Dict:
    """
    Fallback: Extract data using simple keyword matching
    """
    extracted = {}
    text_lower = text_content.lower()
    
    # Look for mission statement
    if 'mission' in text_lower:
        # Simple extraction - find text around 'mission' keyword
        lines = text_content.split('\n')
        for i, line in enumerate(lines):
            if 'mission' in line.lower():
                # Take next few lines as mission
                mission_lines = lines[i:i+3]
                extracted['mission'] = ' '.join(mission_lines).strip()[:500]
                break
    
    # Look for budget information
    import re
    budget_matches = re.findall(r'\$[\d,]+', text_content)
    if budget_matches:
        # Try to extract largest dollar amount
        amounts = [int(match.replace('$', '').replace(',', '')) for match in budget_matches]
        extracted['annual_budget'] = max(amounts)
    
    return extracted

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to fill grant forms using LLM
    
    Expected input:
    {
        "pdf_data": "base64_encoded_pdf_content",
        "ngo_profile": {
            "organization_name": "Example NGO",
            "mission": "Helping communities",
            "years_active": 5,
            "focus_areas": ["education", "health"],
            "annual_budget": 500000,
            "contact_email": "info@ngo.org",
            "phone": "+1-555-0123",
            "recent_projects": "Community center construction"
        },
        "grant_context": {
            "funder_name": "Example Foundation",
            "focus_area": "education",
            "max_amount": 50000,
            "requirements": "Must serve underserved communities"
        },
        "data_sources": {
            "has_profile_pdf": true,
            "has_website": false,
            "website_url": null
        },
        "ngo_profile_pdf": "base64_encoded_pdf_content",  # Optional
        "extracted_data": {}  # Optional - from PDF/website processing
    }
    """
    logging.info('Grant form filling request received')
    
    try:
        # Parse request
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
        processing_mode = req_body.get('processing_mode', 'azure-deepseek')  # Default to enhanced system
        data_sources = req_body.get('data_sources', {})
        ngo_profile_pdf = req_body.get('ngo_profile_pdf')
        
        if not pdf_data:
            return func.HttpResponse(
                json.dumps({"error": "pdf_data is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Enhance NGO profile with additional data sources - NO FALLBACKS
        logging.info(f"Enhancing NGO profile with data sources: {data_sources}")
        enhanced_ngo_profile = enhance_ngo_profile(ngo_profile, data_sources, ngo_profile_pdf)
        logging.info("NGO profile enhancement completed")
        
        # Process the grant form filling with selected processing mode
        result = process_grant_form(pdf_data, enhanced_ngo_profile, grant_context, processing_mode)
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in grant form filling: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}", "type": type(e).__name__}),
            status_code=500,
            mimetype="application/json"
        )

def process_grant_form(pdf_data: str, enhanced_ngo_profile: Dict, grant_context: Dict, processing_mode: str = 'azure-deepseek') -> Dict:
    """
    Process grant form filling workflow
    """
    try:
        # Step 1: Parse PDF form fields
        form_fields = parse_pdf_form_fields(pdf_data)
        logging.info(f"Parsed {len(form_fields)} form fields from PDF")
        
        # Step 2: Classify and analyze fields
        classified_fields = classify_form_fields(form_fields)
        logging.info(f"Classified fields: {classified_fields}")
        
        # Step 3: Generate responses using LLM with selected processing mode
        # Generate responses using selected orchestrator - NO FALLBACKS for debugging
        filled_responses = generate_field_responses(classified_fields, enhanced_ngo_profile, grant_context, processing_mode)
        logging.info(f"Generated responses: {filled_responses}")
        
        # Step 4: Generate filled PDF using proper PDF generation
        try:
            logging.info("Attempting to import and use PDFFormFiller...")
            try:
                from .pdf_utils import PDFFormFiller
                pdf_filler = PDFFormFiller()
                logging.info("PDFFormFiller created successfully")
            except ImportError as e:
                logging.error(f"Failed to import PDFFormFiller (reportlab dependency issue): {str(e)}")
                raise Exception(f"PDF utilities not available due to missing dependencies: {str(e)}")
            pdf_success, filled_pdf_data, fill_method = pdf_filler.fill_pdf_form(pdf_data, filled_responses)
            logging.info(f"PDF generation result: success={pdf_success}, method={fill_method}")
            
            if not pdf_success:
                logging.warning(f"PDF generation failed: {fill_method}")
                # NO FALLBACKS - let PDF generation fail explicitly
                raise Exception(f"PDF generation failed: {fill_method}")
                
        except Exception as e:
            logging.error(f"Error generating PDF: {str(e)}")
            # NO FALLBACKS - let PDF generation fail explicitly
            logging.error(f"PDF generation failed completely: {str(e)}")
            pdf_success = False
            filled_pdf_data = None
            fill_method = f"PDF_GENERATION_ERROR: {str(e)}"
        
        # Step 5: Analyze original PDF structure
        # PDF analysis with explicit error handling - NO FALLBACKS
        try:
            try:
                from .pdf_utils import PDFFormAnalyzer
            except ImportError as e:
                logging.error(f"Failed to import PDFFormAnalyzer: {str(e)}")
                raise Exception(f"PDF analysis not available due to missing dependencies: {str(e)}")
            pdf_analysis = PDFFormAnalyzer.analyze_pdf_structure(pdf_data)
        except Exception as e:
            logging.error(f"PDF analysis failed: {str(e)}")
            # Try simple analysis as last resort but don't hide errors
            try:
                pdf_analysis = analyze_pdf_simple(pdf_data)
                pdf_analysis["analysis_method"] = "simple_fallback"
                pdf_analysis["original_error"] = str(e)
            except Exception as simple_error:
                raise Exception(f"All PDF analysis methods failed. Original: {str(e)}, Simple: {str(simple_error)}")
        
        # Step 6: Create response structure
        filled_form_data = create_filled_form_structure(filled_responses)
        
        result = {
            "success": True,
            "original_fields": form_fields,
            "classified_fields": classified_fields,
            "filled_responses": filled_responses,
            "filled_form_structure": filled_form_data,
            "pdf_analysis": pdf_analysis,
            "timestamp": datetime.utcnow().isoformat(),
            "processing_summary": {
                "total_fields": sum(len(fields) for fields in classified_fields.values()) if classified_fields else len(filled_responses),  # Count all fields across categories
                "filled_fields": len(filled_responses),
                "fill_rate": round((len(filled_responses) / max(sum(len(fields) for fields in classified_fields.values()) if classified_fields else len(filled_responses), 1)) * 100, 1),
                "pdf_generation": {
                    "success": pdf_success,
                    "method": fill_method
                }
            }
        }
        
        # Add filled PDF if successful
        if pdf_success and filled_pdf_data:
            result["filled_pdf"] = {
                "data": filled_pdf_data,
                "filename": "filled_grant_application.pdf",
                "content_type": "application/pdf",
                "encoding": "base64"
            }
        
        return result
        
    except Exception as e:
        logging.error(f"Error processing grant form: {str(e)}")
        raise

def parse_pdf_form_fields(pdf_data: str) -> List[Dict]:
    """
    Extract form fields from PDF using PyPDF2
    """
    try:
        # Decode base64 PDF data
        try:
            pdf_bytes = base64.b64decode(pdf_data)
            logging.info(f"Decoded PDF data: {len(pdf_bytes)} bytes")
        except Exception as e:
            raise Exception(f"Failed to decode base64 PDF data: {str(e)}")
        
        # Create PDF reader with better error handling
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            logging.info(f"PDF loaded successfully: {len(pdf_reader.pages)} pages")
        except Exception as e:
            raise Exception(f"Failed to read PDF with PyPDF2 (possibly corrupted PDF): {str(e)}")
        
        form_fields = []
        
        # Check if PDF has form fields
        if pdf_reader.is_encrypted:
            logging.warning("PDF is encrypted, cannot extract form fields")
            return []
        
        # Try to get form fields
        try:
            if hasattr(pdf_reader, 'get_form_text_fields'):
                text_fields = pdf_reader.get_form_text_fields() or {}
                for field_name, field_value in text_fields.items():
                    form_fields.append({
                        "name": field_name,
                        "type": "text",
                        "current_value": field_value or "",
                        "required": True  # Assume required for demo
                    })
        except Exception as e:
            logging.warning(f"Could not extract form fields with PyPDF2: {str(e)}")
        
        # If no form fields found, extract text and infer fields
        if not form_fields:
            form_fields = infer_fields_from_text(pdf_reader)
        
        return form_fields
        
    except Exception as e:
        logging.error(f"Error parsing PDF form fields: {str(e)}")
        # NO FALLBACKS - raise error if parsing fails
        raise Exception(f"PDF form field parsing failed: {str(e)}")

def infer_fields_from_text(pdf_reader) -> List[Dict]:
    """
    Infer form fields from PDF text content when no form fields are present
    """
    try:
        # Extract all text from PDF
        full_text = ""
        try:
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                full_text += page_text + "\n"
                logging.debug(f"Page {page_num + 1} text length: {len(page_text)}")
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF pages: {str(e)}")
        
        # 🐛 DEBUG: Log extracted PDF text for debugging
        logging.info(f"🐛 DEBUG - EXTRACTED PDF TEXT (first 1000 chars):")
        logging.info(f"🐛 {full_text[:1000]}")
        logging.info(f"🐛 DEBUG - FULL PDF TEXT LENGTH: {len(full_text)} characters")
        
        # Common grant form field patterns - expanded for better matching
        field_patterns = [
            {"pattern": r"organization|applicant|entity|agency|nonprofit|ngo|name", "name": "organization_name", "type": "text"},
            {"pattern": r"project|program|initiative|proposal|title|subject", "name": "project_title", "type": "text"},
            {"pattern": r"mission|purpose|vision|statement|about|overview", "name": "mission_statement", "type": "textarea"},
            {"pattern": r"description|summary|details|narrative|background|abstract", "name": "project_description", "type": "textarea"},
            {"pattern": r"budget|amount|cost|funding|financial|money|dollar|\$|expense", "name": "requested_amount", "type": "number"},
            {"pattern": r"duration|timeline|period|timeframe|length|term|months|years", "name": "project_duration", "type": "text"},
            {"pattern": r"target|beneficiary|population|audience|community|served|impact", "name": "target_population", "type": "textarea"},
            {"pattern": r"outcomes|results|goals|objectives|impact|deliverables|achievements", "name": "expected_outcomes", "type": "textarea"},
            {"pattern": r"contact|phone|email|address|location|director|coordinator", "name": "contact_information", "type": "text"},
            {"pattern": r"experience|history|background|qualifications|expertise|track", "name": "organization_background", "type": "textarea"},
        ]
        
        inferred_fields = []
        import re
        
        for pattern_info in field_patterns:
            if re.search(pattern_info["pattern"], full_text, re.IGNORECASE):
                inferred_fields.append({
                    "name": pattern_info["name"],
                    "type": pattern_info["type"],
                    "current_value": "",
                    "required": True,
                    "inferred": True
                })
        
        # Enhanced error reporting if no fields inferred
        if not inferred_fields:
            text_sample = full_text[:500].strip() if full_text.strip() else "NO TEXT EXTRACTED"
            logging.error(f"Failed to infer fields. PDF text sample: {text_sample}")
            raise Exception(f"No form fields could be inferred from PDF text content. Text sample: {text_sample}")
        
        logging.info(f"Inferred {len(inferred_fields)} fields from PDF text")
        return inferred_fields
        
    except Exception as e:
        logging.error(f"Error inferring fields from text: {str(e)}")
        raise Exception(f"Failed to infer fields from PDF text: {str(e)}")

# REMOVED: get_demo_grant_fields fallback function
# All form fields must be extracted from actual PDF content

def classify_form_fields(form_fields: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Classify form fields into categories for better LLM prompting
    """
    categories = {
        "organizational": [],
        "project": [],
        "financial": [],
        "impact": [],
        "other": []
    }
    
    # Classification rules
    org_keywords = ["organization", "org", "ngo", "entity", "mission", "history", "registration"]
    project_keywords = ["project", "program", "initiative", "activity", "description", "title"]
    financial_keywords = ["budget", "cost", "amount", "funding", "financial", "expense"]
    impact_keywords = ["outcome", "impact", "result", "benefit", "target", "population", "beneficiary"]
    
    for field in form_fields:
        field_name_lower = field["name"].lower()
        
        if any(keyword in field_name_lower for keyword in org_keywords):
            categories["organizational"].append(field)
        elif any(keyword in field_name_lower for keyword in project_keywords):
            categories["project"].append(field)
        elif any(keyword in field_name_lower for keyword in financial_keywords):
            categories["financial"].append(field)
        elif any(keyword in field_name_lower for keyword in impact_keywords):
            categories["impact"].append(field)
        else:
            categories["other"].append(field)
    
    return categories

def generate_field_responses(classified_fields: Dict, enhanced_ngo_profile: Dict, grant_context: Dict, processing_mode: str = 'azure-deepseek') -> Dict[str, str]:
    """
    Generate appropriate responses for each field using LLM with sequential processing to avoid rate limits
    """
    import time
    responses = {}
    
    try:
        # Use GPT-OSS-120B API with sequential processing to respect rate limits
        logging.info("Using GPT-OSS-120B API for grant form filling with sequential processing")
        
        # Count total fields for progress tracking
        total_fields = sum(len(fields) for fields in classified_fields.values())
        current_field = 0
        
        # Process each category sequentially
        for category, fields in classified_fields.items():
            for field in fields:
                current_field += 1
                field_name = field["name"]
                field_type = field["type"]
                
                logging.info(f"Processing field {current_field}/{total_fields}: {field_name} (category: {category})")
                
                # Generate contextual prompt
                prompt = create_field_prompt(field_name, field_type, category, enhanced_ngo_profile, grant_context)
                
                # Get GPT-OSS-120B API response
                try:
                    # Create more directive prompt that forces specific content generation
                    full_prompt = f"""You are an expert grant writer. Generate ONLY the specific content requested, not instructions or placeholders.

{prompt}

IMPORTANT: Provide only the actual content for this field. Do not include the field name, do not say "Please provide...", do not give instructions. Just write the specific content that would go in this field."""
                    
                    # 🐛 DEBUG: Log the full prompt being sent to the model
                    logging.info(f"🐛 DEBUG - PROMPT FOR FIELD '{field_name}' (first 500 chars):")
                    logging.info(f"🐛 {full_prompt[:500]}...")
                    
                    result = call_local_gemma_model(full_prompt, processing_mode)
                    
                    if not result["success"]:
                        raise Exception(f"Local Gemma model failed for field {field_name}: {result.get('error')} (Type: {result.get('error_type')})")
                    
                    # 🐛 DEBUG: Log the raw model response
                    raw_response = result["text"].strip()
                    logging.info(f"🐛 DEBUG - RAW RESPONSE FOR FIELD '{field_name}' (first 500 chars):")
                    logging.info(f"🐛 {raw_response[:500]}...")
                    logging.info(f"🐛 DEBUG - RAW RESPONSE LENGTH: {len(raw_response)} characters")
                    
                    # Log enhanced system debug info if available
                    if result.get("debug_info"):
                        logging.info(f"🔍 ENHANCED DEBUG INFO FOR FIELD '{field_name}':")
                        if result["debug_info"].get("agent_dialogue"):
                            logging.info(f"   🗨️ Agent dialogue captured: {len(result['debug_info']['agent_dialogue'])} messages")
                        if result["debug_info"].get("web_crawling_results"):
                            logging.info(f"   🕷️ Web crawling results: {len(result['debug_info']['web_crawling_results'])} results")
                        if result["debug_info"].get("research_intelligence"):
                            logging.info(f"   🧠 Research intelligence: {result['debug_info']['research_intelligence'].get('analysis_summary', 'No summary')[:100]}...")
                    
                    responses[field_name] = raw_response
                    logging.info(f"✅ Generated response for {field_name}: {len(raw_response)} characters")
                    
                    # Add delay between API calls to respect rate limits (10 requests/minute for GlobalStandard capacity=10)
                    # Wait 7 seconds between calls (10 req/min = 6s per request + 1s buffer)
                    if current_field < total_fields:  # Don't wait after the last field
                        logging.info(f"⏰ Waiting 7 seconds before next field to respect rate limits...")
                        time.sleep(7)
                    
                except Exception as e:
                    logging.error(f"Field response generation failed for {field_name}: {str(e)}")
                    # NO FALLBACKS - surface all errors explicitly
                    responses[field_name] = f"FIELD_GENERATION_ERROR: {str(e)}"
                    
                    # Still wait before next field even on error to avoid cascading rate limit issues
                    if current_field < total_fields:
                        logging.info(f"⏰ Waiting 7 seconds before next field (even after error) to respect rate limits...")
                        time.sleep(7)
        
        logging.info(f"✅ Completed processing all {total_fields} fields sequentially")
        return responses
        
    except Exception as e:
        logging.error(f"Error generating field responses: {str(e)}")
        # NO FALLBACKS - raise error for explicit debugging
        raise Exception(f"Field response generation completely failed: {str(e)}")

def create_field_prompt(field_name: str, field_type: str, category: str, enhanced_ngo_profile: Dict, grant_context: Dict) -> str:
    """
    Create contextual prompt for each field type using enhanced NGO profile
    """
    # Build comprehensive NGO context
    ngo_context = f"""
    NGO Profile:
    - Organization: {enhanced_ngo_profile.get('organization_name', 'Example NGO')}
    - Mission: {enhanced_ngo_profile.get('mission', 'Helping communities')}
    - Years Active: {enhanced_ngo_profile.get('years_active', 5)}
    - Focus Areas: {', '.join(enhanced_ngo_profile.get('focus_areas', ['community development']))}
    - Annual Budget: ${enhanced_ngo_profile.get('annual_budget', 500000):,}"""
    
    # Add contact information if available
    if enhanced_ngo_profile.get('contact_email'):
        ngo_context += f"\n    - Contact: {enhanced_ngo_profile.get('contact_email')}"
    if enhanced_ngo_profile.get('phone'):
        ngo_context += f" | {enhanced_ngo_profile.get('phone')}"
    
    # Add recent projects if available
    if enhanced_ngo_profile.get('recent_projects'):
        ngo_context += f"\n    - Recent Projects: {enhanced_ngo_profile.get('recent_projects')}"
    
    # Add target population if available
    if enhanced_ngo_profile.get('target_population'):
        ngo_context += f"\n    - Target Population: {enhanced_ngo_profile.get('target_population')}"
    
    # Add key achievements if available
    if enhanced_ngo_profile.get('key_achievements'):
        ngo_context += f"\n    - Key Achievements: {enhanced_ngo_profile.get('key_achievements')}"
    
    # Add geographic scope if available
    if enhanced_ngo_profile.get('geographic_scope'):
        ngo_context += f"\n    - Geographic Scope: {enhanced_ngo_profile.get('geographic_scope')}"
    
    # Add data sources used for transparency
    if enhanced_ngo_profile.get('data_sources_used'):
        ngo_context += f"\n    - Data Sources: {', '.join(enhanced_ngo_profile.get('data_sources_used'))}"
    
    base_context = f"""
    {ngo_context}
    
    Grant Context:
    - Funder: {grant_context.get('funder_name', 'Foundation')}
    - Focus Area: {grant_context.get('focus_area', 'community development')}
    - Max Amount: ${grant_context.get('max_amount', 50000):,}
    - Requirements: {grant_context.get('requirements', 'N/A')}
    """
    
    # Field-specific prompts
    field_prompts = {
        "organization_name": f"{base_context}\nProvide the exact legal name of the organization.",
        
        "project_title": f"{base_context}\nCreate a compelling project title (8-12 words) that aligns with both the NGO's mission and the funder's focus area. Make it specific and action-oriented.",
        
        "mission_statement": f"{base_context}\nWrite a concise mission statement (under 200 words) that clearly describes the organization's core purpose and demonstrates alignment with the grant focus area.",
        
        "project_description": f"{base_context}\nWrite a detailed project description (300-500 words) that includes:\n1. The problem being addressed\n2. Your proposed solution\n3. Specific activities and methodology\n4. Timeline and milestones\n5. How it aligns with funder priorities",
        
        "requested_amount": f"{base_context}\nDetermine an appropriate funding request amount considering:\n1. The maximum grant amount\n2. Project scope and needs\n3. Organizational capacity\nProvide only the dollar amount (no $ symbol).",
        
        "project_duration": f"{base_context}\nSpecify an appropriate project duration (e.g., '12 months', '18 months') based on the project scope and typical grant periods.",
        
        "target_population": f"{base_context}\nDescribe the target population this project will serve, including demographics, size, and why they need this intervention.",
        
        "expected_outcomes": f"{base_context}\nList 3-5 specific, measurable outcomes this project will achieve, including quantitative targets where possible."
    }
    
    return field_prompts.get(field_name, f"{base_context}\nProvide an appropriate response for the field '{field_name}' ({field_type}).")

# REMOVED: generate_demo_responses and generate_fallback_response functions
# All responses must be generated by local Gemma model

def create_filled_form_structure(responses: Dict[str, str]) -> Dict:
    """
    Create structured representation of filled form
    """
    return {
        "form_type": "grant_application",
        "filled_fields": responses,
        "completion_status": "completed",
        "fill_timestamp": datetime.utcnow().isoformat(),
        "total_fields": len(responses),
        "metadata": {
            "processing_method": "llm_assisted",
            "field_classification": "automated"
        }
    }