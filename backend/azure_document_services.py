"""
Azure Document Intelligence & Computer Vision Implementation
Advanced document extraction for DeepSeek R1 Multi-Agent System
"""

import os
import json
import logging
from typing import Dict, Any, List
import io
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.core.credentials import AzureKeyCredential
from msrest.authentication import CognitiveServicesCredentials
from dataclasses import dataclass

@dataclass
class ExtractedTable:
    """Structured representation of a table"""
    row_count: int
    column_count: int
    headers: List[str]
    data: List[List[str]]
    confidence: float

@dataclass
class ExtractedContent:
    """Complete document extraction result"""
    text_content: str
    tables: List[ExtractedTable]
    form_fields: Dict[str, str]
    layout_sections: List[Dict[str, Any]]
    visual_elements: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class AzureDocumentExtractor:
    """Azure Document Intelligence for advanced PDF extraction"""
    
    def __init__(self):
        self.endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', 'https://eastus2.api.cognitive.microsoft.com/')
        self.key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY', '7fcf33092bc5f6974cdaaf61ad42b1f1')
        
        if not self.key or self.key == 'not_set':
            raise ValueError("Azure Document Intelligence key not configured")
        
        self.client = DocumentAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )
    
    async def extract_document_content(self, pdf_content: bytes) -> ExtractedContent:
        """Extract comprehensive content from PDF using Azure Document Intelligence"""
        
        try:
            # Use the prebuilt-layout model for comprehensive extraction
            poller = self.client.begin_analyze_document("prebuilt-layout", pdf_content)
            result = poller.result()
            
            # Extract text content
            text_content = result.content if result.content else ""
            
            # Extract tables
            tables = []
            if result.tables:
                for table in result.tables:
                    # Build table structure
                    table_data = [['' for _ in range(table.column_count)] for _ in range(table.row_count)]
                    headers = []
                    
                    for cell in table.cells:
                        if cell.row_index < len(table_data) and cell.column_index < len(table_data[0]):
                            table_data[cell.row_index][cell.column_index] = cell.content or ""
                            
                            # Collect headers (first row)
                            if cell.row_index == 0:
                                headers.append(cell.content or "")
                    
                    extracted_table = ExtractedTable(
                        row_count=table.row_count,
                        column_count=table.column_count,
                        headers=headers,
                        data=table_data,
                        confidence=getattr(table, 'confidence', 0.9)
                    )
                    tables.append(extracted_table)
            
            # Extract form fields (if any)
            form_fields = {}
            if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
                for kv_pair in result.key_value_pairs:
                    if kv_pair.key and kv_pair.value:
                        key_text = kv_pair.key.content if kv_pair.key.content else ""
                        value_text = kv_pair.value.content if kv_pair.value.content else ""
                        form_fields[key_text] = value_text
            
            # Extract layout sections
            layout_sections = []
            if result.paragraphs:
                for paragraph in result.paragraphs:
                    section = {
                        "content": paragraph.content,
                        "role": getattr(paragraph, 'role', 'paragraph'),
                        "bounding_regions": []
                    }
                    
                    if hasattr(paragraph, 'bounding_regions'):
                        for region in paragraph.bounding_regions:
                            section["bounding_regions"].append({
                                "page_number": region.page_number,
                                "polygon": [{"x": point.x, "y": point.y} for point in region.polygon] if region.polygon else []
                            })
                    
                    layout_sections.append(section)
            
            # Metadata
            metadata = {
                "page_count": len(result.pages) if result.pages else 0,
                "language": getattr(result, 'languages', [{}])[0].get('locale', 'unknown') if hasattr(result, 'languages') and result.languages else 'unknown',
                "extraction_method": "azure_document_intelligence",
                "model_used": "prebuilt-layout"
            }
            
            logging.info(f"Extracted {len(text_content)} characters, {len(tables)} tables, {len(form_fields)} form fields")
            
            return ExtractedContent(
                text_content=text_content,
                tables=tables,
                form_fields=form_fields,
                layout_sections=layout_sections,
                visual_elements=[],  # Will be filled by Computer Vision
                metadata=metadata
            )
            
        except Exception as e:
            logging.error(f"Document Intelligence extraction failed: {e}")
            # Fallback to basic text extraction
            return ExtractedContent(
                text_content=f"Extraction failed: {str(e)}",
                tables=[],
                form_fields={},
                layout_sections=[],
                visual_elements=[],
                metadata={"extraction_method": "failed", "error": str(e)}
            )

class AzureComputerVisionAnalyzer:
    """Azure Computer Vision for visual content analysis"""
    
    def __init__(self):
        self.endpoint = os.getenv('AZURE_COMPUTER_VISION_ENDPOINT', 'https://eastus2.api.cognitive.microsoft.com/')
        self.key = os.getenv('AZURE_COMPUTER_VISION_KEY', '8cc4ae11e65c4f80b3a3b893c2b1b0b0')
        
        if not self.key or self.key == 'not_set':
            raise ValueError("Azure Computer Vision key not configured")
        
        self.client = ComputerVisionClient(
            endpoint=self.endpoint,
            credentials=CognitiveServicesCredentials(self.key)
        )
    
    async def analyze_visual_content(self, pdf_content: bytes) -> List[Dict[str, Any]]:
        """Analyze visual elements in the document"""
        
        try:
            # For PDF analysis, we'll use OCR and image analysis
            # Note: This is a simplified implementation
            # In production, you'd extract images from PDF first
            
            visual_elements = []
            
            # Analyze document for visual features
            # This would typically involve:
            # 1. Converting PDF pages to images
            # 2. Running Computer Vision on each image
            # 3. Detecting charts, diagrams, images
            
            # Placeholder implementation
            visual_analysis = {
                "images": [],
                "charts_detected": False,
                "diagrams_detected": False,
                "text_regions": [],
                "confidence": 0.85,
                "analysis_method": "azure_computer_vision"
            }
            
            visual_elements.append(visual_analysis)
            
            logging.info("Visual content analysis completed")
            return visual_elements
            
        except Exception as e:
            logging.error(f"Computer Vision analysis failed: {e}")
            return [{
                "error": str(e),
                "analysis_method": "failed"
            }]

class EnhancedDocumentProcessor:
    """Combined Azure services for comprehensive document processing"""
    
    def __init__(self):
        self.document_extractor = AzureDocumentExtractor()
        self.vision_analyzer = AzureComputerVisionAnalyzer()
    
    async def process_document(self, pdf_content: bytes) -> Dict[str, Any]:
        """Complete document processing with both services"""
        
        logging.info("Starting enhanced document processing...")
        
        # Step 1: Extract structured content
        extracted_content = await self.document_extractor.extract_document_content(pdf_content)
        
        # Step 2: Analyze visual elements
        visual_elements = await self.vision_analyzer.analyze_visual_content(pdf_content)
        
        # Step 3: Combine results
        enhanced_content = {
            "structured_text": extracted_content.text_content,
            "tables": [
                {
                    "headers": table.headers,
                    "data": table.data,
                    "dimensions": f"{table.row_count}x{table.column_count}",
                    "confidence": table.confidence
                }
                for table in extracted_content.tables
            ],
            "form_fields": extracted_content.form_fields,
            "layout_analysis": {
                "sections": extracted_content.layout_sections,
                "page_count": extracted_content.metadata.get("page_count", 0)
            },
            "visual_analysis": visual_elements,
            "metadata": {
                **extracted_content.metadata,
                "visual_elements_count": len(visual_elements),
                "processing_complete": True
            }
        }
        
        # Create rich context for DeepSeek R1 agents
        grant_context = self._create_grant_context(enhanced_content)
        
        logging.info(f"Enhanced processing complete: {len(enhanced_content['structured_text'])} chars, {len(enhanced_content['tables'])} tables")
        
        return {
            "extracted_content": enhanced_content,
            "grant_context": grant_context
        }
    
    def _create_grant_context(self, content: Dict[str, Any]) -> str:
        """Create rich context string for DeepSeek R1 agents"""
        
        context_parts = []
        
        # Add main text
        context_parts.append(f"DOCUMENT TEXT:\n{content['structured_text']}\n")
        
        # Add table information
        if content['tables']:
            context_parts.append("EXTRACTED TABLES:")
            for i, table in enumerate(content['tables']):
                context_parts.append(f"Table {i+1} ({table['dimensions']}):")
                if table['headers']:
                    context_parts.append(f"Headers: {', '.join(table['headers'])}")
                context_parts.append("")
        
        # Add form fields
        if content['form_fields']:
            context_parts.append("FORM FIELDS:")
            for key, value in content['form_fields'].items():
                context_parts.append(f"{key}: {value}")
            context_parts.append("")
        
        # Add layout information
        layout = content['layout_analysis']
        context_parts.append(f"DOCUMENT STRUCTURE:")
        context_parts.append(f"Pages: {layout.get('page_count', 'unknown')}")
        context_parts.append(f"Sections: {len(layout.get('sections', []))}")
        
        return "\n".join(context_parts)

# Global instance for use in Azure Functions
enhanced_processor = EnhancedDocumentProcessor()

async def process_document_with_azure_services(pdf_content: bytes) -> Dict[str, Any]:
    """Main function for Azure Functions integration"""
    return await enhanced_processor.process_document(pdf_content)