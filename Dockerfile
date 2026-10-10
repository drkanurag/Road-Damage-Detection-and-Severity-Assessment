FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight microservice dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    httpx \
    pydantic \
    python-multipart \
    numpy \
    opencv-python-headless \
    pillow \
    onnxruntime \
    pyyaml

COPY . /app

EXPOSE 8000 8001 8002 8003 8004

CMD ["python", "web_server.py"]
