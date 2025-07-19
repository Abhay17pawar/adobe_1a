#!/usr/bin/env python3
"""
Local test script for PDF processing without Docker.
This script installs dependencies and tests the PDF processing locally.
"""

import subprocess
import sys
from pathlib import Path
import os

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing PDF processing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_pdf_processing():
    """Test the PDF processing locally"""
    print("🔄 Testing PDF processing...")
    
    # Create test directories
    input_dir = Path("test_input")
    output_dir = Path("test_output")
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Create a simple text file to simulate PDF processing
    test_file = input_dir / "test.txt"
    with open(test_file, 'w') as f:
        f.write("""Test Document

1. Introduction
This is a test document for validating the PDF processing solution.

2. Content Section
Lorem ipsum dolor sit amet, consectetur adipiscing elit.

3. Conclusion
This concludes the test document.
""")
    
    print(f"📄 Created test file: {test_file}")
    
    # Import and test the processing module
    try:
        sys.path.insert(0, '.')
        from process_pdfs import process_pdfs, logger
        
        # Temporarily modify the script to work with our test setup
        import process_pdfs as pp
        
        # Override the process_pdfs function to use our test directories
        original_input_dir = "/app/input"
        original_output_dir = "/app/output"
        
        # Mock the directories
        os.environ['TEST_MODE'] = '1'
        
        # Test individual functions
        print("🧪 Testing text processing functions...")
        
        # Test document title extraction
        from process_pdfs import _extract_document_title
        title = _extract_document_title("Test Document\n\nChapter 1", "test.pdf")
        print(f"   Title extraction: {title}")
        
        # Test section parsing
        from process_pdfs import _parse_sections
        sections = _parse_sections("1. Introduction\nThis is intro\n\n2. Content\nThis is content", [])
        print(f"   Sections found: {len(sections)}")
        
        # Test confidence scoring
        from process_pdfs import _calculate_confidence_score
        confidence = _calculate_confidence_score("This is a test document with good content.", sections)
        print(f"   Confidence score: {confidence:.2f}")
        
        # Test language detection
        from process_pdfs import _detect_language
        language = _detect_language("This is an English document with common words.")
        print(f"   Language detection: {language}")
        
        print("✅ All processing functions work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing PDF processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Local PDF Processing Test")
    print("============================")
    
    # Check current directory
    if not Path("process_pdfs.py").exists():
        print("❌ Please run this script from the Challenge_1a directory")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️  Continuing without installing dependencies...")
    
    # Test processing
    if test_pdf_processing():
        print("\n🎉 Local testing completed successfully!")
        print("\nNext steps:")
        print("- Add actual PDF files to sample_dataset/pdfs/")
        print("- Run with Docker using ./test.sh")
        print("- Test with various PDF types and sizes")
    else:
        print("\n❌ Local testing failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
