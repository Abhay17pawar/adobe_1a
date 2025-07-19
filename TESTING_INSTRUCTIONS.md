# Testing Instructions for Adobe India Hackathon 2025 - Challenge 1a

This guide will help you test the PDF processing solution on your machine with Docker.

## Prerequisites

- **Docker**: Make sure Docker is installed and running on your machine
- **Git**: To clone the repository
- **Test PDF files**: Any PDF files you want to test with

## Quick Start (5 minutes)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Challenge_1a
```

### 2. Add Test PDF Files
```bash
# Create the input directory if it doesn't exist
mkdir -p sample_dataset/pdfs

# Copy your test PDF files to this directory
cp /path/to/your/test.pdf sample_dataset/pdfs/
```

### 3. Run the Automated Test
```bash
# Make the test script executable
chmod +x test.sh

# Run the complete test (builds Docker image and processes PDFs)
./test.sh
```

That's it! The script will:
- ✅ Build the Docker image
- ✅ Process all PDF files in `sample_dataset/pdfs/`
- ✅ Generate JSON outputs in `sample_dataset/outputs/`
- ✅ Show you the results

## Manual Testing (Step by Step)

If you prefer to run commands manually:

### 1. Build the Docker Image
```bash
docker build --platform linux/amd64 -t pdf-processor .
```

### 2. Run the Processing
```bash
docker run --rm \
    -v "$(pwd)/sample_dataset/pdfs:/app/input:ro" \
    -v "$(pwd)/sample_dataset/outputs:/app/output" \
    --network none \
    pdf-processor
```

### 3. Check Results
```bash
# List generated JSON files
ls -la sample_dataset/outputs/

# View a specific output (replace filename as needed)
cat "sample_dataset/outputs/your-pdf-name.json"
```

## Expected Output

When successful, you should see:
```
🚀 Adobe India Hackathon 2025 - Challenge 1a Test Script
==================================================
📦 Building Docker image...
✅ Docker image built successfully
📄 Found X PDF file(s) in sample_dataset/pdfs/
🔄 Running PDF processing container...
✅ Processing completed successfully
📊 Generated X JSON output file(s)
🎉 Test completed!
```

## What Gets Generated

For each `filename.pdf` in the input directory, you'll get a `filename.json` with:

```json
{
  "document_info": {
    "filename": "your-document.pdf",
    "title": "Extracted Document Title",
    "pages": 10,
    "processing_timestamp": "2025-07-19T06:50:31.185775Z"
  },
  "content": {
    "sections": [
      {
        "section_id": 1,
        "title": "Section Title",
        "content": "Section content...",
        "page_number": 1
      }
    ],
    "tables": [
      {
        "table_id": 1,
        "page_number": 2,
        "headers": ["Col1", "Col2"],
        "rows": [["Data1", "Data2"]]
      }
    ]
  },
  "metadata": {
    "extraction_method": "pymupdf",
    "confidence_score": 0.95,
    "language": "en",
    "word_count": 1500,
    "processing_time_ms": 250
  }
}
```

## Performance Testing

To test performance with the hackathon requirements:

### Test Processing Speed
```bash
# Time the processing
time docker run --rm \
    -v "$(pwd)/sample_dataset/pdfs:/app/input:ro" \
    -v "$(pwd)/sample_dataset/outputs:/app/output" \
    --network none \
    pdf-processor
```

**Expected**: Processing should complete in under 10 seconds for 50-page PDFs.

### Test Resource Usage
```bash
# Monitor resource usage during processing
docker stats pdf-processor
```

**Expected**: Memory usage should stay under 16GB.

## Troubleshooting

### Common Issues and Solutions

#### 1. "Docker command not found"
```bash
# Install Docker (Ubuntu/Debian)
sudo apt update && sudo apt install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER
# Log out and log back in
```

#### 2. "Permission denied" errors
```bash
# Make sure test script is executable
chmod +x test.sh

# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
# Log out and log back in
```

#### 3. "No PDF files found"
```bash
# Check if PDFs are in the right location
ls -la sample_dataset/pdfs/
# Files should be directly in this folder, not in subfolders
```

#### 4. Build fails with architecture errors
```bash
# Force AMD64 architecture
docker build --platform linux/amd64 -t pdf-processor .
```

#### 5. Processing returns empty results
- Check if your PDF is text-based (not scanned images)
- Try with a different PDF file
- Check the logs for specific error messages

## Testing Different PDF Types

Test with various PDF types to validate robustness:

1. **Simple text PDFs** - Basic documents with clear text
2. **Academic papers** - With headings, sections, references
3. **Technical documents** - With tables, diagrams, complex layouts
4. **Multi-language PDFs** - Test language detection
5. **Large PDFs** - Test performance with 40-50 page documents

## Validation

### Check Output Quality
1. **Structure**: Verify sections are properly detected
2. **Content**: Ensure text is extracted accurately
3. **Metadata**: Check processing time and confidence scores
4. **Schema**: Validate JSON format matches expected structure

### Performance Validation
- ✅ Processing time < 10 seconds for 50-page PDFs
- ✅ Memory usage < 16GB
- ✅ Works without internet access (`--network none`)
- ✅ Runs on CPU only (AMD64 architecture)

## Local Development Testing

For development and debugging:

```bash
# Test without Docker (requires Python libraries)
python3 test_local.py

# Install dependencies locally (optional)
pip3 install -r requirements.txt
```

## Getting Help

If you encounter issues:

1. **Check logs**: Look at the Docker container output for error messages
2. **Verify setup**: Ensure PDFs are in `sample_dataset/pdfs/`
3. **Test with sample**: Try with a simple PDF first
4. **Check Docker**: Ensure Docker is running and has sufficient resources

## Success Criteria

Your test is successful if:
- ✅ Docker image builds without errors
- ✅ PDF files are processed and JSON outputs are generated
- ✅ Processing completes within time limits
- ✅ Output JSON contains meaningful extracted content
- ✅ No network connectivity errors (runs offline)

---

## Quick Commands Summary

```bash
# Complete automated test
./test.sh

# Manual build and run
docker build --platform linux/amd64 -t pdf-processor .
docker run --rm -v "$(pwd)/sample_dataset/pdfs:/app/input:ro" -v "$(pwd)/sample_dataset/outputs:/app/output" --network none pdf-processor

# Check results
ls sample_dataset/outputs/
cat sample_dataset/outputs/your-file.json
```

Happy testing! 🚀
