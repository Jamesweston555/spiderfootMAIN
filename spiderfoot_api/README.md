# SpiderFoot API

A REST API wrapper for SpiderFoot, providing a modern interface to interact with SpiderFoot scans programmatically.

## Features

- RESTful API endpoints
- JWT-based authentication
- CORS support
- Async request handling
- Proper error handling
- API documentation (Swagger UI)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spiderfoot-api.git
cd spiderfoot-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

1. Start the API server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation:
```
http://localhost:8000/docs
```

## API Endpoints

### Authentication

- `POST /token` - Get an access token
  - Requires username and password
  - Returns JWT token

### Scans

- `GET /scans` - List all scans
- `POST /scans` - Start a new scan
- `GET /scans/{scan_id}` - Get scan details
- `DELETE /scans/{scan_id}` - Delete a scan
- `GET /scans/{scan_id}/results` - Get scan results

## Example Usage

```python
import requests

# Get an access token
response = requests.post(
    "http://localhost:8000/token",
    data={"username": "admin", "password": "admin"}
)
token = response.json()["access_token"]

# Start a new scan
headers = {"Authorization": f"Bearer {token}"}
scan_data = {
    "name": "My Scan",
    "target": "example.com",
    "modules": ["sfp_dns", "sfp_whois"]
}
response = requests.post(
    "http://localhost:8000/scans",
    json=scan_data,
    headers=headers
)
scan_id = response.json()["id"]

# Get scan results
response = requests.get(
    f"http://localhost:8000/scans/{scan_id}/results",
    headers=headers
)
results = response.json()
```

## Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Rate limiting (to be implemented)
- Input validation

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Run linter:
```bash
flake8
```

## License

MIT License 