# Backend Dockerfile for Zeabur
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Create downloads directory
RUN mkdir -p /app/downloads

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
