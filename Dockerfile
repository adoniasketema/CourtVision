# 1. Base Image: Use Python 3.11 slim for a lightweight, production-ready Linux environment
FROM python:3.11-slim

# 2. Set environment variables
# PYTHONUNBUFFERED=1 ensures logs are printed directly to Azure console without buffering
# PYTHONDONTWRITEBYTECODE=1 prevents generating temporary .pyc files inside the container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Install critical OS system dependencies for Computer Vision & OpenCV (libgl1, ffmpeg, codecs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Set container working directory
WORKDIR /app

# 5. Copy Python package requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy backend source code and AI model weights into container
COPY . .

# 7. Expose FastAPI HTTP server port
EXPOSE 8000

# 8. Start FastAPI server using Uvicorn bound to 0.0.0.0 (required for Azure ingress routing)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
