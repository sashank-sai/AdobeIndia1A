# Use Python 3.10 slim image for smaller size
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main processing script
COPY process_pdfs.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Ensure the script is executable
RUN chmod +x process_pdfs.py

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the PDF processor
CMD ["python", "process_pdfs.py"]