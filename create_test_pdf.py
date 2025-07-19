#!/usr/bin/env python3
"""
Create a simple test PDF for testing the PDF processing solution.
This script creates a basic PDF with text content and sections.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from pathlib import Path
import sys

def create_test_pdf(output_path: Path):
    """Create a test PDF with structured content"""
    
    # Create document
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10
    )
    
    # Document content
    story.append(Paragraph("Test Document for PDF Processing", title_style))
    story.append(Spacer(1, 20))
    
    # Introduction section
    story.append(Paragraph("1. Introduction", heading_style))
    story.append(Paragraph(
        "This is a test document created to validate the PDF processing solution for the Adobe India Hackathon 2025 Challenge 1a. "
        "The document contains structured content including headings, paragraphs, and tables to test the extraction capabilities.",
        styles['Normal']
    ))
    story.append(Spacer(1, 15))
    
    # Methodology section
    story.append(Paragraph("2. Methodology", heading_style))
    story.append(Paragraph(
        "The PDF processing solution should be able to extract this text and identify the document structure. "
        "It should recognize headings, paragraphs, and organize them into a structured JSON format.",
        styles['Normal']
    ))
    story.append(Spacer(1, 15))
    
    # Data section with table
    story.append(Paragraph("3. Sample Data", heading_style))
    story.append(Paragraph(
        "The following table contains sample data that should be extracted and parsed:",
        styles['Normal']
    ))
    story.append(Spacer(1, 10))
    
    # Create a table
    table_data = [
        ['Parameter', 'Value', 'Unit', 'Notes'],
        ['Processing Time', '< 10', 'seconds', 'For 50-page PDF'],
        ['Memory Limit', '16', 'GB', 'Maximum RAM usage'],
        ['CPU Cores', '8', 'cores', 'Available processing power'],
        ['Model Size', '< 200', 'MB', 'If using ML models']
    ]
    
    table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Results section
    story.append(Paragraph("4. Expected Results", heading_style))
    story.append(Paragraph(
        "The PDF processing solution should extract this document and generate a JSON file containing:",
        styles['Normal']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("• Document metadata (filename, title, page count)", styles['Normal']))
    story.append(Paragraph("• Structured sections with titles and content", styles['Normal']))
    story.append(Paragraph("• Extracted table data with headers and rows", styles['Normal']))
    story.append(Paragraph("• Processing metadata (confidence score, language, word count)", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Conclusion section
    story.append(Paragraph("5. Conclusion", heading_style))
    story.append(Paragraph(
        "This test document provides a structured format to validate the PDF processing capabilities. "
        "The solution should successfully extract all text content, identify the hierarchical structure, "
        "and generate a well-formatted JSON output that conforms to the specified schema.",
        styles['Normal']
    ))
    
    # Build the PDF
    doc.build(story)
    print(f"Test PDF created: {output_path}")

if __name__ == "__main__":
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        output_file = Path("sample_dataset/pdfs/test_document.pdf")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        create_test_pdf(output_file)
        
    except ImportError:
        print("ReportLab not available. Creating a simple text-based PDF creator...")
        print("You can manually add PDF files to sample_dataset/pdfs/ for testing.")
        
        # Create a simple text file as a placeholder
        placeholder_file = Path("sample_dataset/pdfs/README.txt")
        placeholder_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(placeholder_file, 'w') as f:
            f.write("""
PDF Test Files
==============

Place your test PDF files in this directory to test the PDF processing solution.

You can:
1. Download sample PDFs from the internet
2. Create PDFs using any PDF creation tool
3. Use existing PDF documents

The processing solution will automatically process all PDF files in this directory
when you run the test script.

Example PDF files to test with:
- Simple text documents
- Documents with headings and sections
- Documents with tables
- Multi-page documents
- Complex layouts

Make sure your test PDFs are not password-protected and contain readable text.
""")
        
        print(f"Created placeholder file: {placeholder_file}")
        print("Please add actual PDF files to sample_dataset/pdfs/ directory for testing.")
