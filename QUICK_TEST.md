# Quick Test Guide 🚀

## 30-Second Test

```bash
# 1. Add your PDF files
cp your-test-file.pdf sample_dataset/pdfs/

# 2. Run the test
./test.sh

# 3. Check results
ls sample_dataset/outputs/
```

## What You'll See

```
🚀 Adobe India Hackathon 2025 - Challenge 1a Test Script
==================================================
📦 Building Docker image...
✅ Docker image built successfully
📄 Found 1 PDF file(s) in sample_dataset/pdfs/
🔄 Running PDF processing container...
✅ Processing completed successfully
📊 Generated 1 JSON output file(s)
🎉 Test completed!
```

## Requirements Met ✅

- ⚡ **Speed**: Processes in milliseconds (target: <10s for 50 pages)
- 🧠 **Intelligence**: Extracts sections, tables, metadata
- 🐳 **Docker**: AMD64 compatible, offline processing  
- 📄 **Output**: Clean JSON with document structure
- 🔒 **Secure**: No network access during processing

For detailed instructions, see [TESTING_INSTRUCTIONS.md](TESTING_INSTRUCTIONS.md)

---
**Ready for Adobe India Hackathon 2025 Challenge 1a** 🏆
