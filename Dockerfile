# Use Python 3.11 image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port (optional for HTTP servers)
EXPOSE 8000

# Run the script (or use your start command)
CMD ["python", "repo_extractor_llm.py"]
