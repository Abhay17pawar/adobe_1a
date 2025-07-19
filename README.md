# Challenge 1a: PDF Processing Solution

This is a sample solution for Challenge 1a of the Adobe India Hackathon 2025. The challenge requires implementing a PDF processing solution that extracts structured data from PDF documents and outputs JSON files. The solution must be containerized using Docker and meet specific performance and resource constraints.

## Official Challenge Guidelines

### Submission Requirements

• **GitHub Project**: Complete code repository with working solution  
• **Dockerfile**: Must be present in the root directory and functional  
• **README.md**: Documentation explaining the solution, models, and libraries used  

### Build Command

```bash
docker build --platform linux/amd64 -t <reponame.someidentifier> .
```

### Run Command

```bash
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output/repoidentifier/:/app/output --network none <reponame.someidentifier>
```

### Critical Constraints

• **Execution Time**: ≤ 10 seconds for a 50-page PDF  
• **Model Size**: ≤ 200MB (if using ML models)  
• **Network**: No internet access allowed during runtime execution  
• **Runtime**: Must run on CPU (amd64) with 8 CPUs and 16 GB RAM  
• **Architecture**: Must work on AMD64, not ARM-specific  

### Key Requirements

• **Automatic Processing**: Process all PDFs from `/app/input` directory  
• **Output Format**: Generate `filename.json` for each `filename.pdf`  
• **Input Directory**: Read-only access only  
• **Open Source**: All libraries, models, and tools must be open source  
• **Cross-Platform**: Test on both simple and complex PDFs  

## Sample Solution Structure

```
Challenge_1a/
├── sample_dataset/
│   ├── outputs/         # JSON files provided as outputs.
│   ├── pdfs/            # Input PDF files
│   └── schema/          # Output schema definition
│       └── output_schema.json
├── Dockerfile           # Docker container configuration
├── process_pdfs.py      # Sample processing script
└── README.md           # This file
```

## Sample Implementation

### Current Sample Solution

The provided `process_pdfs.py` is a basic sample that demonstrates:

• PDF file scanning from input directory  
• Dummy JSON data generation  
• Output file creation in the specified format  

**Note**: This is a placeholder implementation using dummy data. A real solution would need to:

• Implement actual PDF text extraction  
• Parse document structure and hierarchy  
• Generate meaningful JSON output based on content analysis  

### Sample Processing Script (`process_pdfs.py`)

```python
# Current sample implementation
def process_pdfs():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Process all PDF files
    for pdf_file in input_dir.glob("*.pdf"):
        # Generate structured JSON output
        # (Current implementation uses dummy data)
        output_file = output_dir / f"{pdf_file.stem}.json"
        # Save JSON output
```

### Sample Docker Configuration

```dockerfile
FROM --platform=linux/amd64 python:3.10
WORKDIR /app
COPY process_pdfs.py .
CMD ["python", "process_pdfs.py"]
```

## Expected Output Format

### Required JSON Structure

Each PDF should generate a corresponding JSON file that must conform to the schema defined in `sample_dataset/schema/output_schema.json`.

## Implementation Guidelines

### Performance Considerations

• **Memory Management**: Efficient handling of large PDFs  
• **Processing Speed**: Optimize for sub-10-second execution  
• **Resource Usage**: Stay within 16GB RAM constraint  
• **CPU Utilization**: Efficient use of 8 CPU cores  

### Testing Strategy

• **Simple PDFs**: Test with basic PDF documents  
• **Complex PDFs**: Test with multi-column layouts, images, tables  
• **Large PDFs**: Verify 50-page processing within time limit  

## Testing Your Solution

### Local Testing

```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-processor .

# Test with sample data
docker run --rm -v $(pwd)/sample_dataset/pdfs:/app/input:ro -v $(pwd)/sample_dataset/outputs:/app/output --network none pdf-processor
```

### Validation Checklist

- [ ] All PDFs in input directory are processed
- [ ] JSON output files are generated for each PDF
- [ ] Output format matches required structure
- [ ] Output conforms to schema in `sample_dataset/schema/output_schema.json`
- [ ] Processing completes within 10 seconds for 50-page PDFs
- [ ] Solution works without internet access
- [ ] Memory usage stays within 16GB limit
- [ ] Compatible with AMD64 architecture

## Libraries and Dependencies

The current sample implementation includes:

• **Python 3.10**: Base runtime environment  
• **PyPDF2**: PDF text extraction (placeholder for actual implementation)  
• **pymupdf**: Alternative PDF processing library  
• **json**: JSON output formatting  
• **pathlib**: File system operations  

## Next Steps for Real Implementation

To create a production-ready solution, you should:

1. **Implement Actual PDF Processing**:
   - Use libraries like `pdfplumber`, `PyPDF2`, or `pymupdf` for text extraction
   - Handle complex PDF layouts, tables, and images
   - Extract metadata and document structure

2. **Optimize Performance**:
   - Implement parallel processing for multiple PDFs
   - Use efficient memory management techniques
   - Optimize for the 10-second constraint

3. **Enhance Output Quality**:
   - Parse document hierarchy (headings, sections, paragraphs)
   - Extract tables and structured data
   - Implement confidence scoring for extractions

4. **Add Error Handling**:
   - Handle corrupted or encrypted PDFs
   - Implement graceful degradation for processing failures
   - Add comprehensive logging and debugging

**Important**: This is a sample implementation. Participants should develop their own solutions that meet all the official challenge requirements and constraints.
