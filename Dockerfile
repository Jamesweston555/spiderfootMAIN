FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone SpiderFoot
RUN git clone https://github.com/Jamesweston555/spiderfootMAIN.git /spiderfoot

# Set working directory
WORKDIR /spiderfoot

# Install Python dependencies
RUN pip install -r requirements.txt

# Create SpiderFoot configuration
RUN echo "api_listen_port=5001\napi_enabled=1\napi_cors_origins=*\napi_key=spiderfoot123\napi_local_cert=\napi_timeout=120" > /spiderfoot/spiderfoot.conf

# Install FastAPI wrapper dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy FastAPI application
COPY spiderfoot_api /app/spiderfoot_api

# Expose port
EXPOSE 8000

# Start both services
CMD python /spiderfoot/sf.py -l 127.0.0.1:5001 -q & \
    uvicorn spiderfoot_api.app.main:app --host 0.0.0.0 --port 8000 