#!/usr/bin/env python3
"""
Test script for PDF form filling functionality
Creates a demo PDF and tests the filling process
"""

import base64
import json
from FillGrantForm.pdf_utils import PDFFormFiller
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def create_demo_grant_form():
    """Create a demo grant application form PDF"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Sample Grant Application Form")
    
    # Form fields (labels only - this creates a non-fillable PDF)
    c.setFont("Helvetica", 12)
    y_pos = 700
    
    fields = [
        "Organization Name: _________________________",
        "Project Title: _____________________________", 
        "Mission Statement:",
        "___________________________________________",
        "___________________________________________",
        "",
        "Project Description:",
        "___________________________________________",
        "___________________________________________", 
        "___________________________________________",
        "",
        "Requested Amount: $ ________________________",
        "Project Duration: __________________________",
        "",
        "Target Population:",
        "___________________________________________",
        "___________________________________________",
        "",
        "Expected Outcomes:",
        "___________________________________________",
        "___________________________________________",
        "___________________________________________"
    ]
    
    for field in fields:
        c.drawString(50, y_pos, field)
        y_pos -= 20
        if y_pos < 50:  # Start new page if needed
            c.showPage()
            y_pos = 750
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

def test_pdf_filling():
    """Test the PDF filling functionality"""
    print("🧪 Testing PDF Form Filling...")
    
    # Create demo PDF
    demo_pdf_bytes = create_demo_grant_form()
    demo_pdf_base64 = base64.b64encode(demo_pdf_bytes).decode('utf-8')
    
    # Sample responses
    field_responses = {
        "organization_name": "Community Development Alliance",
        "project_title": "Digital Literacy Training for Underserved Communities", 
        "mission_statement": "Empowering underserved communities through education, technology access, and capacity building programs that create sustainable positive change and economic opportunities.",
        "project_description": "This 12-month project will establish digital literacy training centers in three underserved neighborhoods, providing computer skills training to 300 adults and seniors. The program includes basic computer operations, internet safety, online job applications, and digital communication skills.",
        "requested_amount": "45000",
        "project_duration": "12 months",
        "target_population": "Low-income adults ages 25-65 in underserved urban neighborhoods who lack basic computer skills and digital literacy, with priority given to unemployed individuals, seniors, and single parents.",
        "expected_outcomes": "1. Train 300 adults in basic digital literacy skills with 85% completion rate. 2. Achieve 70% job application success rate among participants. 3. Establish sustainable partnerships with 5 local employers."
    }
    
    # Test PDF filling
    filler = PDFFormFiller()
    success, filled_pdf_data, method = filler.fill_pdf_form(demo_pdf_base64, field_responses)
    
    print(f"✅ PDF Filling Success: {success}")
    print(f"📄 Method Used: {method}")
    
    if success and filled_pdf_data:
        # Save filled PDF
        filled_pdf_bytes = base64.b64decode(filled_pdf_data)
        with open("demo_filled_grant_form.pdf", "wb") as f:
            f.write(filled_pdf_bytes)
        print(f"💾 Filled PDF saved as: demo_filled_grant_form.pdf")
        print(f"📊 Filled PDF size: {len(filled_pdf_bytes):,} bytes")
    
    return success

if __name__ == "__main__":
    test_pdf_filling()