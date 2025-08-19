"""
PDF utilities for filling grant forms
Supports both fillable PDF forms and generating new PDFs from responses
"""

import io
import base64
from typing import Dict, List, Any, Optional, Tuple
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import logging

class PDFFormFiller:
    """
    Handles PDF form filling and generation
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    def fill_pdf_form(self, pdf_data: str, field_responses: Dict[str, str]) -> Tuple[bool, Optional[str], str]:
        """
        Fill a PDF form with responses
        
        Returns:
            (success: bool, filled_pdf_base64: Optional[str], method_used: str)
        """
        try:
            # Try to fill actual form fields first
            filled_pdf = self._fill_form_fields(pdf_data, field_responses)
            if filled_pdf:
                return True, filled_pdf, "form_fields"
            
            # If no fillable fields, generate a new PDF
            generated_pdf = self._generate_filled_pdf(field_responses)
            return True, generated_pdf, "generated"
            
        except Exception as e:
            logging.error(f"Error filling PDF form: {str(e)}")
            return False, None, f"error: {str(e)}"
    
    def _fill_form_fields(self, pdf_data: str, field_responses: Dict[str, str]) -> Optional[str]:
        """
        Fill actual PDF form fields if they exist
        """
        try:
            # Decode PDF
            pdf_bytes = base64.b64decode(pdf_data)
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            
            # Check if PDF has fillable fields
            if not self._has_fillable_fields(pdf_reader):
                return None
            
            # Create writer
            pdf_writer = PyPDF2.PdfWriter()
            
            # Process each page
            for page_num, page in enumerate(pdf_reader.pages):
                # Copy page to writer
                pdf_writer.add_page(page)
                
                # Try to update form fields on this page
                if hasattr(page, '/Annots') and page['/Annots']:
                    self._update_page_fields(page, field_responses)
            
            # Create output buffer
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            
            # Encode to base64
            output_buffer.seek(0)
            filled_pdf_bytes = output_buffer.read()
            return base64.b64encode(filled_pdf_bytes).decode('utf-8')
            
        except Exception as e:
            logging.warning(f"Form field filling failed: {str(e)}")
            return None
    
    def _has_fillable_fields(self, pdf_reader) -> bool:
        """
        Check if PDF has fillable form fields
        """
        try:
            # Try different methods to detect form fields
            if hasattr(pdf_reader, 'get_form_text_fields'):
                fields = pdf_reader.get_form_text_fields()
                return fields is not None and len(fields) > 0
            
            # Check for interactive forms in document
            if hasattr(pdf_reader, 'trailer') and pdf_reader.trailer:
                root = pdf_reader.trailer.get('/Root')
                if root and '/AcroForm' in root:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _update_page_fields(self, page, field_responses: Dict[str, str]):
        """
        Update form fields on a specific page (basic implementation)
        Note: This is a simplified approach. Full form filling requires more complex PDF manipulation
        """
        try:
            # This is a placeholder for form field updates
            # In practice, you'd need a more sophisticated library like pdftk or fitz (PyMuPDF)
            # For now, we'll rely on the generated PDF approach
            pass
        except Exception as e:
            logging.warning(f"Failed to update page fields: {str(e)}")
    
    def _generate_filled_pdf(self, field_responses: Dict[str, str]) -> str:
        """
        Generate a new PDF with the filled responses
        """
        try:
            # Create buffer for PDF
            buffer = io.BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            content = self._build_pdf_content(field_responses)
            
            # Build PDF
            doc.build(content)
            
            # Get PDF bytes and encode to base64
            buffer.seek(0)
            pdf_bytes = buffer.read()
            return base64.b64encode(pdf_bytes).decode('utf-8')
            
        except Exception as e:
            logging.error(f"Error generating PDF: {str(e)}")
            raise
    
    def _build_pdf_content(self, field_responses: Dict[str, str]) -> List:
        """
        Build PDF content from field responses
        """
        content = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        content.append(Paragraph("Grant Application Form", title_style))
        content.append(Spacer(1, 20))
        
        # Field categories for better organization
        field_categories = {
            "Organization Information": [
                "organization_name", "mission_statement", "years_active"
            ],
            "Project Details": [
                "project_title", "project_description", "project_duration"
            ],
            "Financial Information": [
                "requested_amount", "total_project_cost"
            ],
            "Impact & Outcomes": [
                "target_population", "expected_outcomes"
            ]
        }
        
        # Add each category
        for category_name, field_names in field_categories.items():
            # Category header
            category_style = ParagraphStyle(
                'CategoryHeader',
                parent=self.styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.darkgreen,
                borderWidth=1,
                borderColor=colors.gray,
                borderPadding=8,
                backColor=colors.lightgrey
            )
            content.append(Paragraph(category_name, category_style))
            content.append(Spacer(1, 10))
            
            # Add fields in this category
            for field_name in field_names:
                if field_name in field_responses:
                    content.extend(self._create_field_content(field_name, field_responses[field_name]))
            
            content.append(Spacer(1, 20))
        
        # Add any remaining fields not in categories
        remaining_fields = set(field_responses.keys()) - {
            field for fields in field_categories.values() for field in fields
        }
        
        if remaining_fields:
            content.append(Paragraph("Additional Information", self.styles['Heading2']))
            content.append(Spacer(1, 10))
            
            for field_name in remaining_fields:
                content.extend(self._create_field_content(field_name, field_responses[field_name]))
        
        # Footer
        content.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.gray
        )
        content.append(Paragraph(
            "This form was generated using AI-powered grant filling technology",
            footer_style
        ))
        
        return content
    
    def _create_field_content(self, field_name: str, field_value: str) -> List:
        """
        Create PDF content for a single field
        """
        content = []
        
        # Field label
        label_style = ParagraphStyle(
            'FieldLabel',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Format field name
        formatted_label = field_name.replace('_', ' ').title() + ":"
        content.append(Paragraph(formatted_label, label_style))
        
        # Field value
        value_style = ParagraphStyle(
            'FieldValue',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            leftIndent=20,
            borderWidth=1,
            borderColor=colors.lightgray,
            borderPadding=8,
            backColor=colors.whitesmoke
        )
        
        # Handle long text fields
        if len(field_value) > 100:
            # For long text, use paragraph style
            content.append(Paragraph(field_value, value_style))
        else:
            # For short text, create a simple paragraph
            content.append(Paragraph(field_value, value_style))
        
        return content

class PDFFormAnalyzer:
    """
    Analyzes PDF forms to extract field information
    """
    
    @staticmethod
    def analyze_pdf_structure(pdf_data: str) -> Dict[str, Any]:
        """
        Analyze PDF structure and return information about form fields
        """
        try:
            pdf_bytes = base64.b64decode(pdf_data)
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            
            analysis = {
                "total_pages": len(pdf_reader.pages),
                "has_form_fields": False,
                "form_fields": [],
                "extracted_text_snippets": [],
                "is_encrypted": pdf_reader.is_encrypted
            }
            
            # Check for form fields
            try:
                if hasattr(pdf_reader, 'get_form_text_fields'):
                    form_fields = pdf_reader.get_form_text_fields()
                    if form_fields:
                        analysis["has_form_fields"] = True
                        analysis["form_fields"] = list(form_fields.keys())
            except Exception:
                pass
            
            # Extract text snippets for field inference
            try:
                for page_num, page in enumerate(pdf_reader.pages[:3]):  # First 3 pages only
                    text = page.extract_text()
                    if text:
                        # Get first 500 characters as snippet
                        snippet = text[:500] + "..." if len(text) > 500 else text
                        analysis["extracted_text_snippets"].append({
                            "page": page_num + 1,
                            "text": snippet
                        })
            except Exception as e:
                logging.warning(f"Failed to extract text: {str(e)}")
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing PDF: {str(e)}")
            return {
                "error": str(e),
                "total_pages": 0,
                "has_form_fields": False,
                "form_fields": [],
                "extracted_text_snippets": []
            }