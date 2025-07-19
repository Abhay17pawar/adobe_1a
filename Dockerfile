FROM --platform=linux/amd64 python:3.10

WORKDIR /app

# Copy requirements and install dependencies first (for better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the processing script
COPY process_pdfs.py .

# Run the processing script
CMD ["python", "process_pdfs.py"]
