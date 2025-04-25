FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone SpiderFoot
RUN git clone https://github.com/Jamesweston555/spiderfootMAIN.git /spiderfoot

# Set working directory
WORKDIR /spiderfoot

# Install SpiderFoot dependencies
RUN pip install -r requirements.txt

# Create API wrapper directory
WORKDIR /spiderfoot_api

# Copy API wrapper files
COPY spiderfoot_api/requirements.txt .
COPY spiderfoot_api/app ./app
COPY spiderfoot_api/services ./services
COPY spiderfoot_api/.env.example .env

# Install API dependencies
RUN pip install -r requirements.txt

# Create SpiderFoot config
RUN echo "api_listen_port=5001" > /spiderfoot/spiderfoot.cfg
RUN echo "api_enabled=1" >> /spiderfoot/spiderfoot.cfg
RUN echo "api_cors_origins=*" >> /spiderfoot/spiderfoot.cfg
RUN echo "api_key=spiderfoot123" >> /spiderfoot/spiderfoot.cfg
RUN echo "api_local_cert=" >> /spiderfoot/spiderfoot.cfg
RUN echo "api_timeout=120" >> /spiderfoot/spiderfoot.cfg

# Expose ports
EXPOSE 5000 5001 8000

# Start both services
CMD python /spiderfoot/sf.py -l 0.0.0.0:5000 & \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 