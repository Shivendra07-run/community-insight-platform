# Use an official lightweight Python runtime
FROM python:3.11-slim

# Set environment variables to keep Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies if required, clear apt cache to keep image size small
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app/

# Create a non-privileged user and switch to it for better security posture
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 8080 for Google Cloud Run
EXPOSE 8080

# Configure health check for Streamlit
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Command to run Streamlit on container startup
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.headless=true"]
