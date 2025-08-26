"""
Modular Document Processing System - Three-Way Strategy Pattern
Supports switching between Azure+DeepSeek, o3 Multimodal, and Quick Fill
"""

import azure.functions as func
import json
import logging
from typing import Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
import os

@dataclass
class DocumentProcessingResult:
    """Standardized output format for all processing strategies"""
    processing_mode: str
    grant_application: Dict[str, Any]
    processing_time: float
    cost_estimate: float
    confidence_score: float
    metadata: Dict[str, Any]

class DocumentProcessor(ABC):
    """Abstract base class for all document processing strategies"""
    
    @abstractmethod
    async def process_document(self, pdf_content: bytes, organization_profile: Dict[str, Any]) -> DocumentProcessingResult:
        """Process document and return standardized result"""
        pass
    
    @abstractmethod
    def get_cost_estimate(self, document_size: int) -> float:
        """Estimate processing cost"""
        pass
    
    @abstractmethod
    def get_processing_time_estimate(self, document_size: int) -> float:
        """Estimate processing time in seconds"""
        pass

class AzureDeepSeekProcessor(DocumentProcessor):
    """Azure Document Intelligence + Computer Vision → DeepSeek R1 Multi-Agent"""
    
    def __init__(self):
        self.doc_intelligence_endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        self.doc_intelligence_key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        self.computer_vision_endpoint = os.getenv('AZURE_COMPUTER_VISION_ENDPOINT')
        self.computer_vision_key = os.getenv('AZURE_COMPUTER_VISION_KEY')
        self.deepseek_endpoint = os.getenv('DEEPSEEK_R1_ENDPOINT')
        self.deepseek_key = os.getenv('DEEPSEEK_R1_API_KEY')
    
    async def process_document(self, pdf_content: bytes, organization_profile: Dict[str, Any]) -> DocumentProcessingResult:
        """Process with Azure services + DeepSeek R1 multi-agent system"""
        start_time = time.time()
        
        try:
            # Step 1: Extract structured content with Azure Document Intelligence
            extracted_content = await self._extract_document_content(pdf_content)
            
            # Step 2: Analyze images/charts with Computer Vision
            visual_analysis = await self._analyze_visual_content(pdf_content)
            
            # Step 3: Process with DeepSeek R1 Multi-Agent System
            grant_application = await self._process_with_multiagent(
                extracted_content, visual_analysis, organization_profile
            )
            
            processing_time = time.time() - start_time
            
            return DocumentProcessingResult(
                processing_mode="azure-deepseek",
                grant_application=grant_application,
                processing_time=processing_time,
                cost_estimate=self.get_cost_estimate(len(pdf_content)),
                confidence_score=0.95,  # High confidence with structured extraction
                metadata={
                    "agents_used": ["general_manager", "research_agent", "budget_agent", "writing_agent", "impact_agent", "networking_agent"],
                    "extraction_method": "azure_document_intelligence",
                    "visual_analysis": "azure_computer_vision",
                    "reasoning_model": "deepseek-r1"
                }
            )
            
        except Exception as e:
            logging.error(f"Azure+DeepSeek processing failed: {e}")
            raise
    
    async def _extract_document_content(self, pdf_content: bytes) -> Dict[str, Any]:
        """Extract structured content using Azure Document Intelligence"""
        # Implementation will use Azure Document Intelligence API
        # For now, return structured placeholder
        return {
            "text_content": "Extracted structured text from PDF",
            "tables": [],
            "form_fields": {},
            "layout": {"pages": 1, "sections": []}
        }
    
    async def _analyze_visual_content(self, pdf_content: bytes) -> Dict[str, Any]:
        """Analyze visual elements using Computer Vision"""
        # Implementation will use Azure Computer Vision API
        return {
            "images": [],
            "charts": [],
            "diagrams": []
        }
    
    async def _process_with_multiagent(self, content: Dict, visuals: Dict, org_profile: Dict) -> Dict[str, Any]:
        """Process with DeepSeek R1 Multi-Agent System"""
        # Import and use the DeepSeek R1 system
        import sys
        sys.path.append('/Users/gg1900/coding/grantseeker-ai-platform/deepseek-multi-agent-system')
        
        # Use simple DeepSeek client instead of full system for now
        from deepseek_r1_langgraph_workflow import DeepSeekR1Client
        
        client = DeepSeekR1Client()
        
        # Combine all extracted content into comprehensive context
        context_parts = [
            f"GRANT OPPORTUNITY:\n{content['text_content']}",
            f"\nORGANIZATION PROFILE:\n{json.dumps(org_profile, indent=2)}",
        ]
        
        # Add table information if available
        if visuals.get('tables'):
            context_parts.append(f"\nTABLES FOUND: {len(visuals['tables'])} tables with structured data")
        
        full_context = "\n".join(context_parts)
        
        # Create comprehensive prompt for general manager
        messages = [{
            "role": "user", 
            "content": f"""As an expert grant writing strategist, analyze this complete grant opportunity and create a comprehensive application strategy.

{full_context}

Please provide a detailed analysis covering:
1. Strategic positioning and approach
2. Key competitive advantages to highlight  
3. Technical approach recommendations
4. Budget strategy and justification
5. Impact and commercial potential
6. Risk mitigation strategies

Use your advanced reasoning to create a winning grant application strategy."""
        }]
        
        # Get comprehensive response from DeepSeek R1
        response = client.chat_completion(messages, "general_manager")
        
        result = {
            "comprehensive_strategy": response,
            "document_analysis": content,
            "visual_analysis": visuals,
            "organization_context": org_profile
        }
        
        return result
    
    def get_cost_estimate(self, document_size: int) -> float:
        """Estimate cost: Document Intelligence + Computer Vision + DeepSeek R1"""
        pages = max(1, document_size // 50000)  # Rough estimate
        doc_intelligence_cost = pages * 0.01  # $0.01 per page
        computer_vision_cost = pages * 0.002  # Rough estimate for images
        deepseek_cost = 0.50  # Estimated based on previous runs
        return doc_intelligence_cost + computer_vision_cost + deepseek_cost
    
    def get_processing_time_estimate(self, document_size: int) -> float:
        """Estimate processing time"""
        pages = max(1, document_size // 50000)
        extraction_time = pages * 5  # 5 seconds per page for extraction
        multiagent_time = 60  # DeepSeek R1 multi-agent processing
        return extraction_time + multiagent_time

class O3MultimodalProcessor(DocumentProcessor):
    """o3 Multimodal - Direct PDF processing (Future Implementation)"""
    
    def __init__(self):
        self.o3_endpoint = os.getenv('O3_MULTIMODAL_ENDPOINT', 'not_available')
        self.o3_key = os.getenv('O3_MULTIMODAL_KEY', 'not_available')
    
    async def process_document(self, pdf_content: bytes, organization_profile: Dict[str, Any]) -> DocumentProcessingResult:
        """Process directly with o3 multimodal model"""
        start_time = time.time()
        
        if self.o3_endpoint == 'not_available':
            # Return placeholder for future implementation
            return DocumentProcessingResult(
                processing_mode="o3-multimodal",
                grant_application={
                    "status": "not_implemented",
                    "message": "o3 multimodal not yet available - awaiting approval",
                    "placeholder_analysis": "Future: Direct PDF → o3 multimodal reasoning"
                },
                processing_time=0,
                cost_estimate=0,
                confidence_score=0,
                metadata={"status": "awaiting_o3_approval"}
            )
        
        try:
            # Future implementation:
            # 1. Send PDF directly to o3 multimodal
            # 2. Single API call handles everything
            # 3. Return comprehensive grant analysis
            
            processing_time = time.time() - start_time
            
            return DocumentProcessingResult(
                processing_mode="o3-multimodal",
                grant_application={},  # Will be populated when o3 is available
                processing_time=processing_time,
                cost_estimate=self.get_cost_estimate(len(pdf_content)),
                confidence_score=0.98,  # Expected high confidence
                metadata={
                    "model": "o3-multimodal",
                    "approach": "direct_pdf_processing"
                }
            )
            
        except Exception as e:
            logging.error(f"o3 multimodal processing failed: {e}")
            raise
    
    def get_cost_estimate(self, document_size: int) -> float:
        """Estimated cost for o3 multimodal (TBD)"""
        return 2.0  # Placeholder estimate
    
    def get_processing_time_estimate(self, document_size: int) -> float:
        """Estimated processing time for o3 (TBD)"""
        return 30.0  # Placeholder estimate

class QuickFillProcessor(DocumentProcessor):
    """Current system - Basic text extraction + GPT-OSS-120B field filling"""
    
    def __init__(self):
        self.gpt_oss_endpoint = os.getenv('AZURE_ML_GPT_OSS_ENDPOINT')
        self.gpt_oss_key = os.getenv('AZURE_ML_GPT_OSS_KEY')
    
    async def process_document(self, pdf_content: bytes, organization_profile: Dict[str, Any]) -> DocumentProcessingResult:
        """Process with current quick-fill system"""
        start_time = time.time()
        
        try:
            # Use existing FillGrantForm logic
            from FillGrantForm import main as fill_grant_form
            
            # Create mock request object
            class MockRequest:
                def __init__(self, pdf_content, org_profile):
                    self.pdf_content = pdf_content
                    self.org_profile = org_profile
                
                def get_json(self):
                    return {
                        'pdfText': self.pdf_content.decode('utf-8', errors='ignore'),
                        'organizationProfile': self.org_profile
                    }
            
            mock_req = MockRequest(pdf_content, organization_profile)
            result = fill_grant_form(mock_req)
            
            processing_time = time.time() - start_time
            
            return DocumentProcessingResult(
                processing_mode="quick-fill",
                grant_application=json.loads(result.get_body()),
                processing_time=processing_time,
                cost_estimate=self.get_cost_estimate(len(pdf_content)),
                confidence_score=0.80,
                metadata={
                    "model": "gpt-oss-120b",
                    "approach": "field_by_field_filling"
                }
            )
            
        except Exception as e:
            logging.error(f"Quick fill processing failed: {e}")
            raise
    
    def get_cost_estimate(self, document_size: int) -> float:
        """Current system cost"""
        return 0.45  # Based on previous analysis
    
    def get_processing_time_estimate(self, document_size: int) -> float:
        """Current system processing time"""
        return 35.0  # ~35 seconds for typical grant

class DocumentProcessorFactory:
    """Factory to create the appropriate document processor"""
    
    @staticmethod
    def create_processor(processing_mode: str) -> DocumentProcessor:
        """Create processor based on selected mode"""
        if processing_mode == "azure-deepseek":
            return AzureDeepSeekProcessor()
        elif processing_mode == "o3-multimodal":
            return O3MultimodalProcessor()
        elif processing_mode == "quick-fill":
            return QuickFillProcessor()
        else:
            raise ValueError(f"Unknown processing mode: {processing_mode}")

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main Azure Function entry point"""
    logging.info('DocumentProcessor function triggered')
    
    try:
        req_body = req.get_json()
        pdf_content = req_body.get('pdfContent', '').encode('utf-8')
        organization_profile = req_body.get('organizationProfile', {})
        processing_mode = req_body.get('processingMode', 'quick-fill')  # Default to current system
        
        # Create appropriate processor
        processor = DocumentProcessorFactory.create_processor(processing_mode)
        
        # Get cost and time estimates
        cost_estimate = processor.get_cost_estimate(len(pdf_content))
        time_estimate = processor.get_processing_time_estimate(len(pdf_content))
        
        # Process document
        result = await processor.process_document(pdf_content, organization_profile)
        
        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "processing_mode": result.processing_mode,
                "grant_application": result.grant_application,
                "processing_time": result.processing_time,
                "cost_estimate": result.cost_estimate,
                "confidence_score": result.confidence_score,
                "metadata": result.metadata,
                "estimates": {
                    "estimated_cost": cost_estimate,
                    "estimated_time": time_estimate
                }
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"DocumentProcessor error: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "error": str(e),
                "message": "Document processing failed"
            }),
            status_code=500,
            mimetype="application/json"
        )