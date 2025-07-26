# Testing Guide

> **Adobe India Hackathon 2025 - Challenge 1a**  
> Comprehensive testing guide for the PDF processing Docker solution

## ⚙️ Option 1 : Automated Tests 🚀 Quick Start 

### Step 1: Add Your PDF Files

```bash
# Place your test PDF files in the input directory
cp your-document.pdf sample_dataset/pdfs/
```

### Step 2: Run Automated Test

```bash
# Execute the complete test suite
./test.sh
```

### Step 3: View Results

```bash
# Check generated JSON outputs
ls sample_dataset/outputs/
```

---



### ⚙️ Option 2: Manual Docker Testing

For detailed control and debugging:

#### 🔨 Build Phase

```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-processor .
```

#### 🏃 Execution Phase

```bash
# Run the PDF processing container
docker run --rm \
    -v "$(pwd)/sample_dataset/pdfs:/app/input:ro" \
    -v "$(pwd)/sample_dataset/outputs:/app/output" \
    --network none \
    pdf-processor
```

#### 📊 Results Phase

```bash
# List all generated JSON files
ls -la sample_dataset/outputs/

# View specific output file
cat "sample_dataset/outputs/filename.json"

# Pretty-print JSON for better readability
python -m json.tool "sample_dataset/outputs/filename.json"
```

---


## ✅ Expected Output

### Console Output

```
🚀 Adobe India Hackathon 2025 - Challenge 1a Test Script
==================================================
📦 Building Docker image...
✅ Docker image built successfully
📄 Found 3 PDF file(s) in sample_dataset/pdfs/
🔄 Running PDF processing container...
✅ Processing completed successfully
📊 Generated 3 JSON output file(s)
   Processing times: document1.pdf (45ms), document2.pdf (120ms), document3.pdf (89ms)
🎉 Test completed!
```

### File Output

For each `filename.pdf`, you'll get a corresponding `filename.json`:

```json
{
  "document_info": {
    "filename": "document.pdf",
    "title": "Extracted Document Title",
    "page_count": 5,
    "processing_time_ms": 87
  },
  "sections": [...],
  "tables": [...],
  "metadata": {...}
}
```

---

### 📄 PDF Test Cases

Test with diverse document types:

| PDF Type             | Purpose            | Expected Result                 |
| -------------------- | ------------------ | ------------------------------- |
| 📝 Simple Text       | Basic extraction   | Clean text extraction           |
| 📊 With Tables       | Table detection    | Structured table data           |
| 📑 Multi-section     | Heading detection  | Hierarchical sections           |
| 📖 Large (40+ pages) | Performance test   | < 10 seconds processing         |
| 🌍 Multi-language    | Language detection | Correct language identification |

---

### ⚡ Performance Validation

```bash
# Time the processing
time ./test.sh

# Monitor resource usage
docker stats pdf-processor
```



