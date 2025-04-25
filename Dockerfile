FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY app.py /app/main.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install FastAPI dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy FastAPI application
COPY spiderfoot_api /app/spiderfoot_api

# Expose port
EXPOSE 8000

# Start the application
CMD uvicorn spiderfoot_api.app.main:app --host 0.0.0.0 --port 8000 