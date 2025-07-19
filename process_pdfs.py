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
    """Extract text using PyMuPDF (fitz) with detailed font and layout information"""
    try:
        doc = fitz.open(pdf_path)
        text_content = ""
        page_texts = []
        page_count = doc.page_count
        text_blocks = []  # Store detailed text blocks with font info
        
        # Try to extract PDF outline/bookmarks first
        pdf_outline = _extract_pdf_outline(doc)
        
        for page_num in range(page_count):
            page = doc[page_num]
            
            # Get text with detailed formatting information
            text_dict = page.get_text("dict")
            page_text = page.get_text()
            page_texts.append(page_text)
            text_content += f"\n--- PAGE {page_num + 1} ---\n{page_text}"
            
            # Extract detailed text blocks with font properties
            page_blocks = _extract_text_blocks_with_properties(text_dict, page_num + 1)
            text_blocks.extend(page_blocks)
        
        doc.close()
        
        processing_time = (time.time() - start_time) * 1000
        metadata = {
            "extraction_method": "pymupdf",
            "processing_time_ms": int(processing_time),
            "page_texts": page_texts,
            "text_blocks": text_blocks,  # Add detailed blocks for heading detection
            "pdf_outline": pdf_outline   # Add PDF outline if available
        }
        
        return text_content.strip(), page_count, metadata
        
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {e}")
        # Don't return here, let the main function try other libraries
        raise e

def _extract_pdf_outline(doc) -> List[Dict[str, Any]]:
    """Extract PDF outline/bookmarks if available"""
    outline = []
    try:
        toc = doc.get_toc()  # Get table of contents
        if toc:
            logger.info(f"Found PDF outline with {len(toc)} entries")
            for level, title, page_num in toc:
                if title.strip():  # Only non-empty titles
                    heading_level = f"H{min(level, 3)}"  # Map to H1, H2, H3
                    outline.append({
                        "level": heading_level,
                        "text": title.strip(),
                        "page": page_num
                    })
        else:
            logger.info("No PDF outline found")
    except Exception as e:
        logger.warning(f"Could not extract PDF outline: {e}")
    
    return outline

def _validate_outline_headings(outline: List[Dict[str, Any]], page_texts: List[str]) -> List[Dict[str, Any]]:
    """Validate PDF outline headings against actual text content"""
    validated = []
    
    for heading in outline:
        title = heading["text"].strip()
        page_num = heading["page"]
        
        # Check if the heading text exists in the corresponding page
        if 1 <= page_num <= len(page_texts):
            page_text = page_texts[page_num - 1]
            
            # Look for exact match or close match in the page
            if (title in page_text or 
                any(title.lower() in line.lower() for line in page_text.split('\n')[:20]) or  # Check first 20 lines
                _fuzzy_match_heading(title, page_text)):
                validated.append(heading)
                logger.debug(f"Validated outline heading: {title}")
            else:
                logger.debug(f"Could not validate outline heading: {title}")
    
    logger.info(f"Validated {len(validated)}/{len(outline)} outline headings")
    return validated

def _fuzzy_match_heading(title: str, page_text: str) -> bool:
    """Check for fuzzy match of heading in page text"""
    # Remove common formatting differences
    clean_title = re.sub(r'[^\w\s]', '', title.lower())
    clean_text = page_text.lower()
    
    # Check for partial matches
    words = clean_title.split()
    if len(words) >= 2:
        # Look for most words present
        found_words = sum(1 for word in words if word in clean_text)
        return found_words >= len(words) * 0.7  # 70% word match
    
    return False

def _merge_outline_and_font_headings(outline_headings: List[Dict[str, Any]], 
                                   font_headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge PDF outline and font-detected headings, avoiding duplicates"""
    merged = outline_headings[:]  # Start with outline headings
    
    for font_heading in font_headings:
        # Check if this heading is already covered by outline
        is_duplicate = False
        for outline_heading in outline_headings:
            if (_similar_text(font_heading["text"], outline_heading["text"]) and
                abs(font_heading["page"] - outline_heading["page"]) <= 1):
                is_duplicate = True
                break
        
        if not is_duplicate:
            merged.append(font_heading)
    
    # Sort by page and position
    merged.sort(key=lambda x: (x["page"], x.get("position", 0)))
    logger.info(f"Merged {len(outline_headings)} outline + {len(font_headings)} font headings = {len(merged)} total")
    
    return merged

def _similar_text(text1: str, text2: str) -> bool:
    """Check if two text strings are similar enough to be considered the same heading"""
    # Simple similarity check
    clean1 = re.sub(r'[^\w\s]', '', text1.lower()).strip()
    clean2 = re.sub(r'[^\w\s]', '', text2.lower()).strip()
    
    if clean1 == clean2:
        return True
    
    # Check if one is substring of other
    if clean1 in clean2 or clean2 in clean1:
        return True
    
    # Check word overlap
    words1 = set(clean1.split())
    words2 = set(clean2.split())
    if words1 and words2:
        overlap = len(words1 & words2) / len(words1 | words2)
        return overlap > 0.6
    
    return False

def _extract_text_blocks_with_properties(text_dict: Dict, page_num: int) -> List[Dict[str, Any]]:
    """Extract text blocks with font and layout properties"""
    blocks = []
    
    for block in text_dict.get("blocks", []):
        if block.get("type") == 0:  # Text block
            for line in block.get("lines", []):
                line_text = ""
                line_fonts = []
                line_sizes = []
                line_flags = []
                line_colors = []
                
                # Extract properties from each span
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        line_text += text + " "
                        line_fonts.append(span.get("font", ""))
                        line_sizes.append(span.get("size", 0))
                        line_flags.append(span.get("flags", 0))
                        line_colors.append(span.get("color", 0))
                
                line_text = line_text.strip()
                if line_text:
                    # Calculate average properties for the line
                    avg_size = sum(line_sizes) / len(line_sizes) if line_sizes else 0
                    dominant_font = max(set(line_fonts), key=line_fonts.count) if line_fonts else ""
                    
                    # Check if line is bold (flag & 16) or italic (flag & 2)
                    is_bold = any(flag & 16 for flag in line_flags)
                    is_italic = any(flag & 2 for flag in line_flags)
                    
                    blocks.append({
                        "text": line_text,
                        "page": page_num,
                        "bbox": line.get("bbox", [0, 0, 0, 0]),  # [x0, y0, x1, y1]
                        "font": dominant_font,
                        "size": avg_size,
                        "is_bold": is_bold,
                        "is_italic": is_italic,
                        "color": line_colors[0] if line_colors else 0
                    })
    
    return blocks

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
    
    # Extract outline (headings) from text - pass metadata for advanced detection
    _extract_outline._metadata = extraction_metadata  # Store metadata for access
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
    """Extract outline (headings) from text content using advanced detection"""
    outline = []
    
    # Try to get detailed text blocks and PDF outline from metadata
    if hasattr(_extract_outline, '_metadata'):
        metadata = _extract_outline._metadata
        
        # First, try to use PDF outline if available
        pdf_outline = metadata.get('pdf_outline', [])
        if pdf_outline:
            logger.info(f"Found PDF outline with {len(pdf_outline)} headings - using as primary source")
            # Validate outline headings against text content
            validated_outline = _validate_outline_headings(pdf_outline, page_texts)
            if validated_outline:
                outline.extend(validated_outline)
        
        # If no outline or insufficient headings, use font-based detection
        if len(outline) < 10:  # Threshold for sufficient headings
            logger.info(f"Current outline has {len(outline)} headings, supplementing with font-based detection")
            text_blocks = metadata.get('text_blocks', [])
            if text_blocks:
                font_headings = _detect_headings_from_blocks(text_blocks)
                
                # Merge and deduplicate if we have outline headings
                if outline:
                    outline = _merge_outline_and_font_headings(outline, font_headings)
                else:
                    outline = font_headings
            else:
                # Fallback to regex-based detection
                logger.info("No text blocks available, using regex fallback")
                outline = _extract_outline_regex_fallback(text_content)
    else:
        # Fallback to regex-based detection
        logger.warning("No metadata available, using regex fallback")
        outline = _extract_outline_regex_fallback(text_content)
    
    return outline

def _detect_headings_from_blocks(text_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect headings using font properties, layout, and content analysis"""
    if not text_blocks:
        return []
    
    logger.info(f"Analyzing {len(text_blocks)} text blocks for heading detection")
    
    # Step 1: Calculate document statistics
    font_stats = _calculate_font_statistics(text_blocks)
    
    # Step 2: Score each block for heading likelihood
    scored_blocks = []
    for block in text_blocks:
        score = _calculate_heading_score(block, font_stats)
        if score > 0.3:  # Threshold for potential headings
            scored_blocks.append({
                'block': block,
                'score': score
            })
    
    # Step 3: Apply structural and content filters
    headings = _filter_and_classify_headings(scored_blocks)
    
    logger.info(f"Detected {len(headings)} potential headings")
    
    return headings

def _calculate_font_statistics(text_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate document-wide font statistics for comparison"""
    sizes = [block['size'] for block in text_blocks if block['size'] > 0]
    fonts = [block['font'] for block in text_blocks if block['font']]
    
    if not sizes:
        return {'avg_size': 12, 'max_size': 12, 'min_size': 12, 'common_fonts': []}
    
    avg_size = sum(sizes) / len(sizes)
    max_size = max(sizes)
    min_size = min(sizes)
    
    # Find most common fonts
    font_counts = {}
    for font in fonts:
        font_counts[font] = font_counts.get(font, 0) + 1
    common_fonts = sorted(font_counts.keys(), key=lambda x: font_counts[x], reverse=True)[:3]
    
    stats = {
        'avg_size': avg_size,
        'max_size': max_size,
        'min_size': min_size,
        'common_fonts': common_fonts,
        'size_std': _calculate_std_deviation(sizes),
        'total_blocks': len(text_blocks)
    }
    
    logger.info(f"Font stats - Avg size: {avg_size:.1f}, Max: {max_size:.1f}, Common fonts: {common_fonts[:2]}")
    
    return stats

def _calculate_std_deviation(values: List[float]) -> float:
    """Calculate standard deviation of values"""
    if len(values) < 2:
        return 0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5

def _calculate_heading_score(block: Dict[str, Any], font_stats: Dict[str, Any]) -> float:
    """Calculate likelihood score that a text block is a heading"""
    score = 0.0
    text = block['text'].strip()
    
    if not text or len(text) < 2:
        return 0.0
    
    # 1. Font Size Analysis (25% weight)
    size_ratio = block['size'] / font_stats['avg_size'] if font_stats['avg_size'] > 0 else 1
    if size_ratio > 1.3:  # Significantly larger than average
        score += 0.25 * min(size_ratio / 2, 1.0)
    
    # 2. Font Weight (Bold) (20% weight)
    if block['is_bold']:
        score += 0.2
    
    # 3. Layout and Positioning Analysis (20% weight)
    layout_score = _analyze_layout_properties(block, font_stats)
    score += 0.2 * layout_score
    
    # 4. Line Length and Structure (15% weight)
    word_count = len(text.split())
    if 1 <= word_count <= 10:  # Typical heading length
        score += 0.15
    elif word_count > 20:  # Too long for typical heading
        score -= 0.1
    
    # 5. Numbering Patterns (12% weight)
    numbering_score = _check_numbering_patterns(text)
    score += 0.12 * numbering_score
    
    # 6. Capitalization (8% weight)
    if text.isupper() and len(text) > 3:  # All caps
        score += 0.08
    elif text.istitle():  # Title case
        score += 0.04
    
    # Penalties for likely non-headings
    if len(text) > 100:  # Very long text
        score -= 0.2
    if text.endswith('.') and word_count > 5:  # Sentence-like
        score -= 0.1
    
    return min(score, 1.0)

def _analyze_layout_properties(block: Dict[str, Any], font_stats: Dict[str, Any]) -> float:
    """Analyze layout and positioning properties for heading detection"""
    layout_score = 0.0
    bbox = block.get('bbox', [0, 0, 0, 0])
    x0, y0, x1, y1 = bbox
    text = block['text'].strip()
    
    # 1. Line Length Analysis (30% of layout score)
    line_width = x1 - x0
    if line_width > 0:
        # Shorter lines are more likely to be headings
        if line_width < 200:  # Relatively short line
            layout_score += 0.3
        elif line_width > 400:  # Very long line (likely body text)
            layout_score -= 0.2
    
    # 2. Vertical Spacing Analysis (25% of layout score)
    # This would require comparing with adjacent blocks, simplified for now
    # Headings typically have more space above/below them
    
    # 3. Alignment Analysis (25% of layout score)
    # Left margin analysis - headings often start at consistent positions
    if x0 < 100:  # Left-aligned or near left margin
        layout_score += 0.25
    
    # 4. Position on Page (20% of layout score)
    # Headings often appear in upper portions of content areas
    if y0 < 200:  # Near top of page (relative)
        layout_score += 0.1
    
    # Penalty for very wide text blocks (likely paragraphs)
    if line_width > 500:
        layout_score -= 0.3
    
    return max(0.0, min(layout_score, 1.0))

def _check_numbering_patterns(text: str) -> float:
    """Check for numbering patterns that indicate headings"""
    patterns = [
        (r'^\d+\.\s+', 1.0),           # "1. Introduction"
        (r'^\d+\.\d+\s+', 0.8),        # "2.1 Overview"  
        (r'^\d+\.\d+\.\d+\s+', 0.6),   # "2.1.1 Details"
        (r'^Chapter\s+\d+', 0.9),       # "Chapter 1"
        (r'^Section\s+\d+', 0.8),       # "Section 2"
        (r'^[A-Z]\.\s+', 0.7),          # "A. First Point"
        (r'^[IVX]+\.\s+', 0.7),         # Roman numerals
    ]
    
    for pattern, weight in patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return weight
    
    return 0.0

def _filter_and_classify_headings(scored_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter scored blocks and classify into heading levels with improved consistency"""
    if not scored_blocks:
        return []
    
    # Sort by score descending
    scored_blocks.sort(key=lambda x: x['score'], reverse=True)
    
    # Apply dynamic threshold based on score distribution
    scores = [item['score'] for item in scored_blocks]
    threshold = _calculate_dynamic_threshold(scores)
    
    logger.info(f"Using dynamic threshold: {threshold:.2f} for {len(scored_blocks)} candidates")
    
    headings = []
    seen_texts = set()  # Prevent duplicates
    page_heading_counts = {}  # Track headings per page for consistency
    
    for item in scored_blocks:
        block = item['block']
        score = item['score']
        text = block['text'].strip()
        page = block['page']
        
        # Apply threshold filter
        if score < threshold:
            continue
        
        # Skip duplicates
        text_key = text.lower().strip()
        if text_key in seen_texts:
            continue
        seen_texts.add(text_key)
        
        # Skip common headers/footers with improved detection
        if _is_header_footer_advanced(text, block):
            continue
        
        # Skip if too many headings on one page (likely false positives)
        page_count = page_heading_counts.get(page, 0)
        if page_count > 8:  # Max headings per page
            continue
        
        # Determine heading level with improved logic
        level = _determine_heading_level_advanced(text, block)
        
        headings.append({
            "level": level,
            "text": text,
            "page": page
        })
        
        page_heading_counts[page] = page_count + 1
    
    # Post-process for consistency and hierarchy
    headings = _apply_hierarchy_consistency(headings)
    
    return headings

def _calculate_dynamic_threshold(scores: List[float]) -> float:
    """Calculate dynamic threshold based on score distribution"""
    if not scores:
        return 0.5
    
    scores_sorted = sorted(scores, reverse=True)
    
    # If we have clear high-scoring items, use a higher threshold
    if len(scores_sorted) > 5:
        # Use 75th percentile or 0.5, whichever is higher
        percentile_75 = scores_sorted[len(scores_sorted) // 4]
        return max(0.5, min(0.7, percentile_75))
    else:
        # For fewer candidates, use a lower threshold
        return max(0.3, scores_sorted[0] * 0.6 if scores_sorted else 0.3)

def _is_header_footer_advanced(text: str, block: Dict[str, Any]) -> bool:
    """Advanced header/footer detection using text and layout"""
    text_lower = text.lower().strip()
    bbox = block.get('bbox', [0, 0, 0, 0])
    x0, y0, x1, y1 = bbox
    
    # Common header/footer patterns (expanded)
    ignore_patterns = [
        'international', 'overview', 'software testing', 'qualifications board',
        'foundation level extension', 'agile tester', 'page', 'copyright', '©',
        'confidential', 'draft', 'version', 'date', 'document', 'title'
    ]
    
    # Exact matches
    if text_lower in ignore_patterns:
        return True
    
    # Very short text
    if len(text) < 3:
        return True
    
    # Just numbers (page numbers)
    if re.match(r'^\d+$', text_lower):
        return True
    
    # Headers that appear in very top or bottom positions
    if y0 < 50 or y0 > 700:  # Likely in header/footer area
        if len(text.split()) <= 3:  # Short text in header/footer area
            return True
    
    # Repetitive short phrases
    if len(text.split()) <= 2 and not re.match(r'^\d+\.', text):
        return True
    
    return False

def _determine_heading_level_advanced(text: str, block: Dict[str, Any]) -> str:
    """Advanced heading level determination using multiple factors"""
    font_size = block.get('size', 12)
    is_bold = block.get('is_bold', False)
    
    # H1 patterns (main sections) - highest priority
    h1_patterns = [
        r'^\d+\.\s+[A-Z]',              # "1. Introduction"
        r'^[A-Z][A-Z\s]{8,}$',          # "REVISION HISTORY" 
        r'^Chapter\s+\d+',               # "Chapter 1"
        r'^(Acknowledgements?|References?|Table\s+of\s+Contents)$',  # Special sections
    ]
    
    # H2 patterns (subsections)
    h2_patterns = [
        r'^\d+\.\d+\s+',                # "2.1 Overview"
        r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*:?$',  # Title case phrases
    ]
    
    # H3 patterns (sub-subsections)
    h3_patterns = [
        r'^\d+\.\d+\.\d+\s+',           # "2.1.1 Details"
        r'^[a-z]+\)',                   # "a) First point"
    ]
    
    # Check patterns in order of specificity
    for pattern in h3_patterns:
        if re.match(pattern, text):
            return "H3"
    
    for pattern in h2_patterns:
        if re.match(pattern, text):
            return "H2"
    
    for pattern in h1_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return "H1"
    
    # Font-based classification as fallback
    if font_size > 16 or (font_size > 14 and is_bold):
        return "H1"
    elif font_size > 12 or is_bold:
        return "H2"
    else:
        return "H3"

def _apply_hierarchy_consistency(headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply hierarchy consistency rules to the detected headings"""
    if not headings:
        return headings
    
    # Sort by page and position (rough ordering)
    headings.sort(key=lambda x: (x['page'], x['text']))
    
    # Ensure we don't have orphaned H3s without H2s, etc.
    consistent_headings = []
    last_level = "H1"
    
    for heading in headings:
        level = heading['level']
        
        # Don't allow jumping more than one level down
        if level == "H3" and last_level == "H1":
            heading['level'] = "H2"  # Promote H3 to H2
        
        consistent_headings.append(heading)
        last_level = heading['level']
    
    return consistent_headings

def _is_header_footer(text: str) -> bool:
    """Check if text is likely a header or footer"""
    text_lower = text.lower().strip()
    
    # Common header/footer patterns
    ignore_patterns = [
        'international', 'overview', 'software testing', 'qualifications board',
        'foundation level extension', 'agile tester', 'page', 'copyright', '©'
    ]
    
    # Exact matches
    if text_lower in ignore_patterns:
        return True
    
    # Pattern matches
    if re.match(r'^\d+$', text_lower):  # Just page numbers
        return True
    
    if len(text) < 3:  # Very short text
        return True
        
    return False

def _determine_heading_level(text: str, font_size: float) -> str:
    """Determine H1, H2, H3 level based on text patterns and font size"""
    
    # H1 patterns (main sections)
    h1_patterns = [
        r'^\d+\.\s+[A-Z]',              # "1. Introduction"
        r'^[A-Z][A-Z\s]{8,}$',          # "REVISION HISTORY"
        r'^Chapter\s+\d+',               # "Chapter 1"
        r'^(Acknowledgements?|References?)$',  # Special sections
    ]
    
    # H2 patterns (subsections)  
    h2_patterns = [
        r'^\d+\.\d+\s+',                # "2.1 Overview"
        r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*:?$',  # Title case
    ]
    
    # H3 patterns (sub-subsections)
    h3_patterns = [
        r'^\d+\.\d+\.\d+\s+',           # "2.1.1 Details"
    ]
    
    # Check patterns in order of specificity
    for pattern in h3_patterns:
        if re.match(pattern, text):
            return "H3"
    
    for pattern in h2_patterns:
        if re.match(pattern, text):
            return "H2"
    
    for pattern in h1_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return "H1"
    
    # Default based on characteristics
    if font_size > 14 or text.isupper():
        return "H1"
    else:
        return "H2"

def _extract_outline_regex_fallback(text_content: str) -> List[Dict[str, Any]]:
    """Fallback regex-based outline extraction for when font info isn't available"""
    outline = []
    
    # Split text by page markers to get page-wise content
    if "--- PAGE" in text_content:
        page_pattern = r'\n--- PAGE (\d+) ---\n'
        parts = re.split(page_pattern, text_content)
        
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
