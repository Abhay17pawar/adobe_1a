#!/bin/bash


set -e

echo "🚀 Adobe India Hackathon 2025 - Challenge 1a Test Script"
echo "=================================================="


if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi


echo "📦 Building Docker image..."
docker build --platform linux/amd64 -t pdf-processor .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi


mkdir -p sample_dataset/pdfs
mkdir -p sample_dataset/outputs


pdf_count=$(find sample_dataset/pdfs -name "*.pdf" 2>/dev/null | wc -l)

if [ $pdf_count -eq 0 ]; then
    echo "⚠️  No PDF files found in sample_dataset/pdfs/"
    echo "   Please add some PDF files to test the processing"
    echo "   You can download sample PDFs or create test files"
else
    echo "📄 Found $pdf_count PDF file(s) in sample_dataset/pdfs/"
fi


echo "🔄 Running PDF processing container..."
echo "   Input: $(pwd)/sample_dataset/pdfs (read-only)"
echo "   Output: $(pwd)/sample_dataset/outputs"

docker run --rm \
    -v "$(pwd)/sample_dataset/pdfs:/app/input:ro" \
    -v "$(pwd)/sample_dataset/outputs:/app/output" \
    --network none \
    pdf-processor

if [ $? -eq 0 ]; then
    echo "✅ Processing completed successfully"
    
    output_count=$(find sample_dataset/outputs -name "*.json" 2>/dev/null | wc -l)
    echo "📊 Generated $output_count JSON output file(s)"
    
    if [ $output_count -gt 0 ]; then
        echo "   Output files:"
        find sample_dataset/outputs -name "*.json" -exec basename {} \;
    fi
else
    echo "❌ Processing failed"
    exit 1
fi

echo ""
echo "🎉 Test completed! Check the sample_dataset/outputs/ directory for results."
echo ""
echo "Next steps:"
echo "- Review the generated JSON files"
echo "- Thank you !!"
