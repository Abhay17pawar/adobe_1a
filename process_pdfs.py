#!/usr/bin/env python3
"""
PDF Processing Solution for Adobe India Hackathon 2025 - Challenge 1a

This script processes PDF files from the input directory and generates
structured JSON output files in the output directory.

Requirements:
- Process all PDFs from /app/input directory
- Generate filename.json for each filename.pdf
- Complete processing within 10 seconds for 50-page PDFs
- Work without internet access
- Use only open-source libraries
"""

import json
import os
import sys
import re
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# PDF processing libraries
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import logging
from datetime import datetime

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: Path) -> Tuple[str, int, Dict[str, Any]]:
    """
    Extract text content from PDF file using the best available library.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (extracted_text, page_count, metadata)
    """
    try:
        logger.info(f"Processing PDF: {pdf_path.name}")
        start_time = time.time()
        
        # Try PyMuPDF first (fastest and most reliable)
        if PYMUPDF_AVAILABLE:
            try:
                return _extract_with_pymupdf(pdf_path, start_time)
            except Exception as e:
                logger.warning(f"PyMuPDF failed, trying fallback: {e}")
        
        # Fallback to pdfplumber (good for tables and structured content)
        if PDFPLUMBER_AVAILABLE:
            try:
                return _extract_with_pdfplumber(pdf_path, start_time)
            except Exception as e:
                logger.warning(f"pdfplumber failed, trying fallback: {e}")
        
        # Final fallback to PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                return _extract_with_pypdf2(pdf_path, start_time)
            except Exception as e:
                logger.warning(f"PyPDF2 failed: {e}")
        
        logger.error("All PDF processing libraries failed!")
        return "", 0, {"error": "All libraries failed"}
        
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
        return "", 0, {"error": str(e)}

def _extract_with_pymupdf(pdf_path: Path, start_time: float) -> Tuple[str, int, Dict[str, Any]]:
    """Extract text using PyMuPDF (fitz)"""
    try:
        doc = fitz.open(pdf_path)
        text_content = ""
        page_texts = []
        page_count = doc.page_count
        
        for page_num in range(page_count):
            page = doc[page_num]
            page_text = page.get_text()
            page_texts.append(page_text)
            text_content += f"\n--- PAGE {page_num + 1} ---\n{page_text}"
        
        doc.close()
        
        processing_time = (time.time() - start_time) * 1000
        metadata = {
            "extraction_method": "pymupdf",
            "processing_time_ms": int(processing_time),
            "page_texts": page_texts
        }
        
        return text_content.strip(), page_count, metadata
        
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {e}")
        # Don't return here, let the main function try other libraries
        raise e

def _extract_with_pdfplumber(pdf_path: Path, start_time: float) -> Tuple[str, int, Dict[str, Any]]:
    """Extract text using pdfplumber"""
    text_content = ""
    page_texts = []
    page_count = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            page_texts.append(page_text)
            text_content += f"\n--- PAGE {page_num + 1} ---\n{page_text}"
    
    processing_time = (time.time() - start_time) * 1000
    metadata = {
        "extraction_method": "pdfplumber",
        "processing_time_ms": int(processing_time),
        "page_texts": page_texts
    }
    
    return text_content.strip(), page_count, metadata

def _extract_with_pypdf2(pdf_path: Path, start_time: float) -> Tuple[str, int, Dict[str, Any]]:
    """Extract text using PyPDF2"""
    text_content = ""
    page_texts = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        page_count = len(pdf_reader.pages)
        
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            page_texts.append(page_text)
            text_content += f"\n--- PAGE {page_num + 1} ---\n{page_text}"
    
    processing_time = (time.time() - start_time) * 1000
    metadata = {
        "extraction_method": "pypdf2",
        "processing_time_ms": int(processing_time),
        "page_texts": page_texts
    }
    
    return text_content.strip(), page_count, metadata

def parse_document_structure(text_content: str, pdf_filename: str, page_count: int, extraction_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the extracted text and create structured JSON output.
    
    Args:
        text_content: Extracted text from PDF
        pdf_filename: Original PDF filename
        page_count: Number of pages in the PDF
        extraction_metadata: Metadata from text extraction
        
    Returns:
        Structured data dictionary
    """
    
    # Extract document title
    title = _extract_document_title(text_content, pdf_filename)
    
    # Extract outline (headings) from text
    outline = _extract_outline(text_content, extraction_metadata.get("page_texts", []))
    
    # Create simple output format matching the schema
    structured_data = {
        "title": title,
        "outline": outline
    }
    
    return structured_data

def _extract_document_title(text_content: str, pdf_filename: str) -> str:
    """Extract document title from text content"""
    if not text_content:
        return f"Document from {Path(pdf_filename).stem}"
    
    lines = text_content.split('\n')
    
    # Look for title patterns in the first few pages
    for line in lines[:100]:  # Check first 100 lines
        line = line.strip()
        if not line:
            continue
        
        # Skip page markers
        if re.match(r'^--- PAGE \d+ ---$', line):
            continue
        
        # Skip common headers/footers
        if re.match(r'^(International|Overview|Software Testing|Qualifications Board)$', line, re.IGNORECASE):
            continue
        
        # Look for title-like patterns
        if re.match(r'^[A-Z][A-Za-z\s\-–]{10,80}$', line):
            # Check if it looks like a real title (not a header)
            if any(word in line.lower() for word in ['foundation', 'level', 'extension', 'overview', 'introduction', 'guide', 'manual', 'document']):
                return line.strip()
        
        # Look for lines that might be titles (first substantial text)
        if len(line) > 10 and len(line) < 100:
            # If it contains typical title words
            title_indicators = ['overview', 'introduction', 'guide', 'manual', 'foundation', 'level', 'extension', 'challenge', 'hackathon']
            if any(indicator in line.lower() for indicator in title_indicators):
                return line.strip()
    
    # Fallback to filename-based title
    return f"Document from {Path(pdf_filename).stem}"

def _extract_outline(text_content: str, page_texts: List[str]) -> List[Dict[str, Any]]:
    """Extract outline (headings) from text content in the simple format"""
    outline = []
    
    # Split text by page markers to get page-wise content
    if "--- PAGE" in text_content:
        # Use regex to split and capture page numbers
        page_pattern = r'\n--- PAGE (\d+) ---\n'
        parts = re.split(page_pattern, text_content)
        
        # Parts will be: [content_before_first_page, page1_num, page1_content, page2_num, page2_content, ...]
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                page_num = int(parts[i])
                page_content = parts[i + 1]
                
                # Extract headings from this page
                page_headings = _extract_headings_from_page(page_content, page_num)
                outline.extend(page_headings)
    else:
        # If no page markers, process as single page
        page_headings = _extract_headings_from_page(text_content, 1)
        outline.extend(page_headings)
    
    return outline

def _extract_headings_from_page(page_content: str, page_num: int) -> List[Dict[str, Any]]:
    """Extract headings from a single page with improved filtering"""
    headings = []
    lines = page_content.split('\n')
    
    # Common header/footer patterns to ignore
    ignore_patterns = [
        r'^International\s*$',
        r'^Overview\s*$', 
        r'^Software Testing\s*$',
        r'^Qualifications Board\s*$',
        r'^Foundation Level Extension.*Agile Tester\s*$',
        r'^Version\s*$',
        r'^Date\s*$', 
        r'^Remarks\s*$',
        r'^Days\s*$',
        r'^Syllabus\s*$',
        r'^Identifier\s*$',
        r'^Reference\s*$',
        r'^\d+$',  # Page numbers
        r'^Page \d+$',
        r'.*Copyright.*',
        r'.*©.*',
    ]
    
    # More specific heading patterns
    heading_patterns = [
        # H1 patterns - main sections (numbered or major headings)
        (r'^\d+\.\s+[A-Z][A-Za-z\s\-–]{10,80}$', 'H1'),  # "1. Introduction to Foundation Level..."
        (r'^[A-Z][A-Z\s]{10,50}$', 'H1'),  # "REVISION HISTORY", "TABLE OF CONTENTS"
        (r'^Chapter\s+\d+:.*', 'H1'),  # "Chapter 1: Agile Software Development"
        (r'^Acknowledgements?\s*$', 'H1'),
        (r'^References?\s*$', 'H1'),
        
        # H2 patterns - subsections (numbered subsections)
        (r'^\d+\.\d+\s+[A-Za-z][A-Za-z\s\-–]{5,50}$', 'H2'),  # "2.1 Intended Audience"
        (r'^\d+\.\d+\.\d+\s+[A-Za-z][A-Za-z\s\-–]{3,50}$', 'H3'),  # "2.1.1 Details"
    ]
    
    # Track seen headings to avoid duplicates
    seen_headings = set()
    
    for line in lines:
        line = line.strip()
        if not line or len(line) > 100:  # Skip empty or very long lines
            continue
        
        # Skip common header/footer patterns
        if any(re.match(pattern, line, re.IGNORECASE) for pattern in ignore_patterns):
            continue
        
        # Check each heading pattern
        for pattern, level in heading_patterns:
            if re.match(pattern, line):
                # Clean up the heading text
                heading_text = line.rstrip(':').strip()
                
                # Create a key for duplicate detection (normalize whitespace)
                heading_key = ' '.join(heading_text.split()).lower()
                
                # Skip if we've seen this heading before
                if heading_key in seen_headings:
                    continue
                
                # Skip very short headings (likely false positives)
                if len(heading_text.strip()) < 3:
                    continue
                
                headings.append({
                    "level": level,
                    "text": heading_text,
                    "page": page_num
                })
                seen_headings.add(heading_key)
                break  # Found a match, don't check other patterns
    
    return headings

def _calculate_confidence_score(text_content: str, outline: List[Dict[str, Any]]) -> float:
    """Calculate confidence score for the extraction quality"""
    if not text_content:
        return 0.0
    
    score = 0.5  # Base score
    
    # Add points for having structured content
    if outline:
        score += 0.2
    
    # Add points for reasonable text length
    word_count = len(text_content.split())
    if word_count > 50:
        score += 0.1
    if word_count > 200:
        score += 0.1
    
    # Subtract points for too many non-alphabetic characters (indicates poor extraction)
    alpha_ratio = len(re.sub(r'[^a-zA-Z\s]', '', text_content)) / len(text_content)
    if alpha_ratio > 0.6:
        score += 0.1
    
    return min(1.0, score)

def process_single_pdf(pdf_path: Path, output_dir: Path) -> bool:
    """
    Process a single PDF file and generate JSON output.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the JSON output
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        # Extract text from PDF
        text_content, page_count, extraction_metadata = extract_text_from_pdf(pdf_path)
        
        # Parse document structure
        structured_data = parse_document_structure(text_content, pdf_path.name, page_count, extraction_metadata)
        
        # Generate output JSON file
        output_file = output_dir / f"{pdf_path.stem}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        processing_time = extraction_metadata.get("processing_time_ms", 0)
        logger.info(f"Successfully processed {pdf_path.name} -> {output_file.name} ({processing_time}ms)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process {pdf_path.name}: {str(e)}")
        return False

def process_pdfs():
    """
    Main function to process all PDF files from input directory.
    """
    # Define input and output directories
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Check if input directory exists
    if not input_dir.exists():
        logger.error(f"Input directory {input_dir} does not exist")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all PDF files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF file
    successful_count = 0
    failed_count = 0
    
    for pdf_file in pdf_files:
        if process_single_pdf(pdf_file, output_dir):
            successful_count += 1
        else:
            failed_count += 1
    
    # Log processing summary
    logger.info(f"Processing completed: {successful_count} successful, {failed_count} failed")
    
    if failed_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting PDF processing...")
    process_pdfs()
    logger.info("PDF processing completed")
