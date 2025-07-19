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
    
    # Parse sections from text
    sections = _parse_sections(text_content, extraction_metadata.get("page_texts", []))
    
    # Extract tables if available
    tables = _extract_tables(text_content, extraction_metadata.get("page_texts", []))
    
    # Calculate confidence score based on text quality
    confidence_score = _calculate_confidence_score(text_content, sections)
    
    # Detect language
    language = _detect_language(text_content)
    
    # Calculate word count
    word_count = len(text_content.split()) if text_content else 0
    
    structured_data = {
        "document_info": {
            "filename": pdf_filename,
            "title": title,
            "pages": page_count,
            "processing_timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "content": {
            "sections": sections,
            "tables": tables
        },
        "metadata": {
            "extraction_method": extraction_metadata.get("extraction_method", "unknown"),
            "confidence_score": confidence_score,
            "language": language,
            "word_count": word_count,
            "processing_time_ms": extraction_metadata.get("processing_time_ms", 0)
        }
    }
    
    return structured_data

def _extract_document_title(text_content: str, pdf_filename: str) -> str:
    """Extract document title from text content"""
    if not text_content:
        return f"Document from {Path(pdf_filename).stem}"
    
    lines = text_content.split('\n')
    
    # Look for title patterns in the first few lines
    for line in lines[:10]:
        line = line.strip()
        if line and len(line) > 5 and len(line) < 100:
            # Skip page markers
            if re.match(r'^--- PAGE \d+ ---$', line):
                continue
            # Skip very short lines or lines with mostly special characters
            if len(re.sub(r'[^a-zA-Z0-9\s]', '', line)) > len(line) * 0.5:
                return line
    
    # Fallback to filename-based title
    return f"Document from {Path(pdf_filename).stem}"

def _parse_sections(text_content: str, page_texts: List[str]) -> List[Dict[str, Any]]:
    """Parse sections from text content"""
    sections = []
    
    if not text_content:
        return sections
    
    # Split by page markers and process each page
    page_pattern = r'--- PAGE (\d+) ---'
    page_splits = re.split(page_pattern, text_content)
    
    current_page = 1
    section_id = 1
    
    # Process content that might not have page markers
    if len(page_splits) == 1:
        sections.extend(_extract_sections_from_text(page_splits[0], current_page, section_id))
    else:
        # Process content with page markers
        for i in range(1, len(page_splits), 2):
            if i + 1 < len(page_splits):
                page_num = int(page_splits[i])
                page_content = page_splits[i + 1]
                page_sections = _extract_sections_from_text(page_content, page_num, section_id)
                sections.extend(page_sections)
                section_id += len(page_sections)
    
    return sections

def _extract_sections_from_text(text: str, page_num: int, start_section_id: int) -> List[Dict[str, Any]]:
    """Extract sections from a piece of text"""
    sections = []
    
    # Look for heading patterns (lines that might be headings)
    lines = text.split('\n')
    current_section = None
    content_buffer = []
    section_id = start_section_id
    
    heading_patterns = [
        r'^[A-Z][A-Z\s\d\.\-]{5,50}$',  # ALL CAPS headings
        r'^\d+\.\s+[A-Z][A-Za-z\s]{5,50}$',  # Numbered headings
        r'^Chapter\s+\d+',  # Chapter headings
        r'^Section\s+\d+',  # Section headings
        r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*:?$',  # Title Case headings
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this line looks like a heading
        is_heading = any(re.match(pattern, line) for pattern in heading_patterns)
        
        if is_heading and len(line) < 100:
            # Save previous section if exists
            if current_section and content_buffer:
                current_section["content"] = ' '.join(content_buffer).strip()
                if current_section["content"]:
                    sections.append(current_section)
            
            # Start new section
            current_section = {
                "section_id": section_id,
                "title": line.rstrip(':'),
                "content": "",
                "page_number": page_num
            }
            content_buffer = []
            section_id += 1
        else:
            # Add to content buffer
            content_buffer.append(line)
    
    # Add the last section
    if current_section and content_buffer:
        current_section["content"] = ' '.join(content_buffer).strip()
        if current_section["content"]:
            sections.append(current_section)
    
    # If no clear sections found, create a general content section
    if not sections and text.strip():
        sections.append({
            "section_id": section_id,
            "title": "Content",
            "content": ' '.join(text.split()),
            "page_number": page_num
        })
    
    return sections

def _extract_tables(text_content: str, page_texts: List[str]) -> List[Dict[str, Any]]:
    """Extract tables from text content"""
    tables = []
    
    # Simple table detection based on text patterns
    # Look for lines with multiple columns separated by spaces or tabs
    table_patterns = [
        r'^.*\t.*\t.*$',  # Tab-separated
        r'^.*\s{3,}.*\s{3,}.*$',  # Multiple spaces
        r'^\|.*\|.*\|.*\|$',  # Pipe-separated
    ]
    
    page_num = 1
    table_id = 1
    
    for page_text in page_texts or [text_content]:
        lines = page_text.split('\n') if page_text else []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line matches table patterns
            if any(re.match(pattern, line) for pattern in table_patterns):
                # Try to extract a table starting from this line
                table = _extract_table_from_lines(lines[i:], table_id, page_num)
                if table:
                    tables.append(table)
                    table_id += 1
                    i += len(table.get("rows", [])) + 1  # Skip processed lines
                else:
                    i += 1
            else:
                i += 1
        
        page_num += 1
    
    return tables

def _extract_table_from_lines(lines: List[str], table_id: int, page_num: int) -> Optional[Dict[str, Any]]:
    """Extract a table from a list of lines"""
    if not lines:
        return None
    
    # Simple table extraction - look for consistent patterns
    table_lines = []
    
    for line in lines[:10]:  # Check up to 10 lines
        line = line.strip()
        if not line:
            break
        
        # Check if line has table-like structure
        if '\t' in line:
            table_lines.append(line.split('\t'))
        elif re.search(r'\s{3,}', line):
            table_lines.append(re.split(r'\s{3,}', line))
        elif line.count('|') >= 2:
            table_lines.append([cell.strip() for cell in line.split('|') if cell.strip()])
        else:
            break
    
    if len(table_lines) < 2:  # Need at least header and one row
        return None
    
    # Assume first line is header
    headers = [cell.strip() for cell in table_lines[0]]
    rows = []
    
    for row_data in table_lines[1:]:
        if len(row_data) == len(headers):
            rows.append([cell.strip() for cell in row_data])
    
    if not rows:
        return None
    
    return {
        "table_id": table_id,
        "page_number": page_num,
        "headers": headers,
        "rows": rows
    }

def _calculate_confidence_score(text_content: str, sections: List[Dict[str, Any]]) -> float:
    """Calculate confidence score for the extraction quality"""
    if not text_content:
        return 0.0
    
    score = 0.5  # Base score
    
    # Add points for having structured content
    if sections:
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

def _detect_language(text_content: str) -> str:
    """Simple language detection"""
    if not text_content:
        return "unknown"
    
    # Simple English detection based on common words
    english_words = {'the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that', 'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more', 'very', 'after', 'words', 'first', 'where', 'much', 'before', 'right', 'too', 'any', 'same', 'tell', 'boy', 'follow', 'came', 'want', 'show', 'also', 'around', 'form', 'three', 'small', 'set', 'put', 'end', 'why', 'again', 'turn', 'here', 'off', 'went', 'old', 'number', 'great', 'tell', 'men', 'say', 'small', 'every', 'found', 'still', 'between', 'name', 'should', 'home', 'big', 'give', 'air', 'line', 'set', 'own', 'under', 'read', 'last', 'never', 'us', 'left', 'end', 'along', 'while', 'might', 'next', 'sound', 'below', 'saw', 'something', 'thought', 'both', 'few', 'those', 'always', 'show', 'large', 'often', 'together', 'asked', 'house', 'don', 'world', 'going', 'want', 'school', 'important', 'until', 'form', 'food', 'keep', 'children', 'feet', 'land', 'side', 'without', 'boy', 'once', 'animal', 'life', 'enough', 'took', 'sometimes', 'four', 'head', 'above', 'kind', 'began', 'almost', 'live', 'page', 'got', 'earth', 'need', 'far', 'hand', 'high', 'year', 'mother', 'light', 'country', 'father', 'let', 'night', 'picture', 'being', 'study', 'second', 'soon', 'story', 'since', 'white', 'ever', 'paper', 'hard', 'near', 'sentence', 'better', 'best', 'across', 'during', 'today', 'however', 'sure', 'knew', 'it', 'try', 'told', 'young', 'sun', 'thing', 'whole', 'hear', 'example', 'heard', 'several', 'change', 'answer', 'room', 'sea', 'against', 'top', 'turned', 'learn', 'point', 'city', 'play', 'toward', 'five', 'himself', 'usually', 'money', 'seen', 'didn', 'car', 'morning', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
    
    words = re.findall(r'\b\w+\b', text_content.lower())
    if not words:
        return "unknown"
    
    english_count = sum(1 for word in words if word in english_words)
    english_ratio = english_count / len(words)
    
    if english_ratio > 0.1:  # If more than 10% are common English words
        return "en"
    else:
        return "unknown"

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
