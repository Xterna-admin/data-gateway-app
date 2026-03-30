# Maintenance Guide

This guide explains how to safely make changes to the Data Gateway application, test them, and maintain the codebase.

## Overview

As a new engineer working on this codebase, you'll need to understand:
1. How to set up your development environment
2. How the code is organized
3. How to make changes safely
4. How to test your changes
5. How to debug issues

---

## Development Environment Setup

### Prerequisites

Install these tools on your local machine:

```bash
# Python 3.10
python --version  # Should show 3.10.x

# pip (Python package manager)
pip --version

# Git
git --version

# Docker (optional but recommended)
docker --version
docker-compose --version
```

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/Xterna-admin/data-gateway-app.git
cd data-gateway-app

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Why virtual environments?**
- Isolates project dependencies
- Prevents conflicts with system Python
- Easy to recreate clean environment

### Step 3: Configure Environment Variables

```bash
# Copy example configuration
cp env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

**For local development**, you can use test credentials or mock services.

### Step 4: Verify Setup

```bash
# Run the application
python run.py

# In another terminal, test the API
curl http://localhost:6969/api

# Expected: {"message":"Hello from Flask!"}
```

---

## Code Organization

Understanding the project structure:

```
data-gateway-app/
├── app.py                      # Flask app initialization
├── run.py                      # Application entry point
├── requirements.txt            # Python dependencies
│
├── modules/                    # Business logic (where most code lives)
│   ├── __init__.py            # Auto-imports all modules
│   ├── api.py                 # API endpoint definitions
│   ├── config.py              # Configuration management
│   ├── sentinel.py            # Sentinel Hub integration
│   ├── entsoe.py              # ENTSOE integration
│   ├── encordSync.py          # Encord dataset operations
│   ├── encordClassificationsSync.py  # Label management
│   ├── stations.py            # Station data handling
│   └── errors.py              # Error definitions
│
├── docs/                       # Documentation
├── config/                     # Configuration files (stations.csv, keys)
├── templates/                  # HTML templates (if any)
├── Dockerfile                  # Docker image definition
└── docker-compose.yml         # Docker orchestration
```

### Module Responsibilities

| Module | Purpose | When to Edit |
|--------|---------|--------------|
| `api.py` | API endpoints | Adding/modifying endpoints |
| `config.py` | Environment variables | Adding new configuration |
| `sentinel.py` | Satellite imagery | Changing Sentinel logic |
| `entsoe.py` | Energy data | Modifying ENTSOE integration |
| `encordSync.py` | Dataset uploads | Changing upload behavior |
| `stations.py` | Station management | Station data format changes |

---

## Making Changes

### General Workflow

1. **Create a branch** for your changes
2. **Make small, focused changes**
3. **Test locally**
4. **Commit with clear messages**
5. **Push and create pull request**

### Example: Adding a New API Endpoint

Let's add an endpoint to get station count.

#### Step 1: Add the Function

Edit `modules/api.py`:

```python
# Add this import at the top if not present
from modules.stations import loadStationsFromCsv
from modules.config import get_stations_csv_path

# Add this new endpoint
@app.route('/sentinel/stations/count')
def sentinel_stations_count():
    """Returns the total number of configured stations."""
    try:
        stations = loadStationsFromCsv(get_stations_csv_path())
        return jsonify({
            "count": len(stations),
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
```

#### Step 2: Test Locally

```bash
# Restart the application
python run.py

# Test the new endpoint
curl http://localhost:6969/sentinel/stations/count

# Expected output:
# {"count": 42, "status": "success"}
```

#### Step 3: Test Error Cases

```bash
# Temporarily rename stations.csv to simulate missing file
mv config/stations.csv config/stations.csv.bak

# Test error handling
curl http://localhost:6969/sentinel/stations/count

# Should return 500 error with message

# Restore file
mv config/stations.csv.bak config/stations.csv
```

#### Step 4: Update Documentation

Update `docs/APIS.md` with the new endpoint:

```markdown
### GET /sentinel/stations/count

Returns the total number of configured stations.

**Example Request**:
curl http://localhost:6969/sentinel/stations/count

**Example Response**:
{
  "count": 42,
  "status": "success"
}
```

#### Step 5: Commit Changes

```bash
# Stage your changes
git add modules/api.py docs/APIS.md

# Commit with descriptive message
git commit -m "Add endpoint to get station count

- Added GET /sentinel/stations/count endpoint
- Returns total number of configured stations
- Includes error handling for missing CSV file
- Updated API documentation"

# Push to your branch
git push origin feature/station-count
```

---

## Testing

### Manual Testing

**Basic API Testing**:

```bash
# Health check
curl http://localhost:6969/api

# List stations
curl http://localhost:6969/sentinel/stations

# Get energy data (requires valid API key)
curl "http://localhost:6969/entsoe?country_code=AT&start=20240101&end=20240102"
```

**Testing with Python**:

Create a test script `test_api.py`:

```python
import requests

BASE_URL = "http://localhost:6969"

def test_health():
    response = requests.get(f"{BASE_URL}/api")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello from Flask!"
    print("✓ Health check passed")

def test_stations():
    response = requests.get(f"{BASE_URL}/sentinel/stations")
    assert response.status_code == 200
    stations = response.json()
    assert isinstance(stations, list)
    assert len(stations) > 0
    print(f"✓ Stations endpoint passed ({len(stations)} stations)")

if __name__ == "__main__":
    test_health()
    test_stations()
    print("All tests passed!")
```

Run it:
```bash
python test_api.py
```

### Integration Testing

**Test Sentinel Hub Integration**:

```python
# test_sentinel.py
from modules.sentinel import get_oauth_token, get_stations_list

def test_oauth():
    try:
        token = get_oauth_token()
        assert token is not None
        assert len(token) > 0
        print("✓ Sentinel OAuth token retrieved")
    except Exception as e:
        print(f"✗ Sentinel OAuth failed: {e}")

def test_stations_load():
    try:
        stations = get_stations_list()
        assert len(stations) > 0
        print(f"✓ Loaded {len(stations)} stations")
    except Exception as e:
        print(f"✗ Failed to load stations: {e}")

if __name__ == "__main__":
    test_oauth()
    test_stations_load()
```

**Test ENTSOE Integration**:

```python
# test_entsoe.py
from modules.entsoe import get_entsoe_data

def test_entsoe():
    try:
        result = get_entsoe_data('AT', '20240101', '20240102')
        assert 'file' in result
        assert 'country' in result
        print(f"✓ ENTSOE data retrieved: {result['file']}")
    except Exception as e:
        print(f"✗ ENTSOE test failed: {e}")

if __name__ == "__main__":
    test_entsoe()
```

### Testing with Docker

```bash
# Build image
docker build -t data-gateway-app:test .

# Run container
docker run -d --name test-gateway \
  -p 6969:6969 \
  -e SENTINEL_CLIENT_ID=test \
  data-gateway-app:test

# Test
curl http://localhost:6969/api

# Clean up
docker stop test-gateway
docker rm test-gateway
```

---

## Debugging

### Common Issues and Solutions

#### 1. Import Errors

**Problem**:
```
ImportError: No module named 'encord'
```

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configuration Errors

**Problem**:
```
Please provide a Sentinel Client ID in .env file.
```

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Verify variable is set
grep SENTINEL_CLIENT_ID .env

# Ensure no extra spaces
SENTINEL_CLIENT_ID=your-id    # Correct
SENTINEL_CLIENT_ID = your-id  # Wrong (spaces around =)
```

#### 3. Port Already in Use

**Problem**:
```
OSError: [Errno 48] Address already in use
```

**Solution**:
```bash
# Find process using port 6969
lsof -i :6969

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=8080 python run.py
```

#### 4. File Not Found Errors

**Problem**:
```
FileNotFoundError: CSV file '/path/to/stations.csv' not found
```

**Solution**:
```bash
# Check if file exists
ls -la /path/to/stations.csv

# Update .env with correct path
STATIONS_CSV_PATH=/actual/path/to/stations.csv

# Or use relative path
STATIONS_CSV_PATH=./config/stations.csv
```

### Python Debugging

**Using Python Debugger (pdb)**:

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# When code hits this line, you'll get interactive debugger
# Commands:
# n - next line
# c - continue
# p variable - print variable
# l - list code
# q - quit
```

**Example**:

```python
@app.route('/sentinel/stations')
def sentinel_stations():
    import pdb; pdb.set_trace()  # Debugger will stop here
    stations = get_stations_list()
    return jsonify(stations)
```

**Using print debugging**:

```python
@app.route('/entsoe')
def entsoe():
    country_code = request.args.get('country_code')
    start = request.args.get('start')
    end = request.args.get('end')
    
    # Add debug prints
    print(f"DEBUG: country_code={country_code}")
    print(f"DEBUG: start={start}, end={end}")
    
    result = get_entsoe_data(country_code, start, end)
    print(f"DEBUG: result={result}")
    
    return result
```

### Logging

**Add logging instead of print**:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/entsoe')
def entsoe():
    logger.info(f"ENTSOE request for country: {country_code}")
    logger.debug(f"Parameters: start={start}, end={end}")
    
    try:
        result = get_entsoe_data(country_code, start, end)
        logger.info(f"Successfully retrieved data: {result['file']}")
        return result
    except Exception as e:
        logger.error(f"Failed to get ENTSOE data: {e}", exc_info=True)
        raise
```

---

## Code Style and Best Practices

### Python Style Guide (PEP 8)

**Naming conventions**:
```python
# Functions and variables: snake_case
def get_station_data():
    station_name = "Andong power station"

# Classes: PascalCase
class StationManager:
    pass

# Constants: UPPER_CASE
MAX_RETRIES = 3
API_TIMEOUT = 30
```

**Function documentation**:
```python
def download_image_for_station(station: Dict, date: str) -> Dict:
    """
    Download satellite image for a specific station and date.
    
    Args:
        station: Dictionary containing station information
        date: Date string in format YYYY-MM-DD
        
    Returns:
        Dictionary with download results including filename and status
        
    Raises:
        ValueError: If station data is invalid
        ConnectionError: If Sentinel Hub API is unreachable
    """
    # Implementation here
```

**Error handling**:
```python
# Bad - catching everything
try:
    result = risky_operation()
except:
    pass

# Good - specific exception handling
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    return {"error": "Service unavailable"}
```

### API Design Best Practices

**RESTful endpoints**:
```python
# Good - RESTful design
GET /stations          # List all
GET /stations/123      # Get specific
POST /stations         # Create
PUT /stations/123      # Update
DELETE /stations/123   # Delete

# Bad - non-RESTful
GET /getStations
POST /createStation
POST /updateStation
```

**Response format consistency**:
```python
# Success response
{
    "status": "success",
    "data": { ... },
    "message": "Operation completed successfully"
}

# Error response
{
    "status": "error",
    "error": "Invalid country code",
    "code": "INVALID_PARAMETER"
}
```

---

## Database Migrations (Future)

If a database is added in the future, use migrations:

```bash
# Install Flask-Migrate
pip install Flask-Migrate

# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Add stations table"

# Apply migration
flask db upgrade

# Rollback
flask db downgrade
```

---

## Performance Monitoring

### Adding Performance Metrics

```python
import time

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.2f}s")
    return response
```

### Monitoring Slow Endpoints

```python
def monitor_performance(threshold=1.0):
    """Decorator to log slow functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            if duration > threshold:
                logger.warning(f"{func.__name__} took {duration:.2f}s")
            
            return result
        return wrapper
    return decorator

@app.route('/slow-endpoint')
@monitor_performance(threshold=2.0)
def slow_endpoint():
    # Implementation
    pass
```

---

## Dependency Management

### Updating Dependencies

```bash
# Show outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Security Scanning

```bash
# Install safety
pip install safety

# Scan for vulnerabilities
safety check

# Scan requirements.txt
safety check -r requirements.txt
```

---

## Git Best Practices

### Commit Messages

**Good commit messages**:
```
Add station count endpoint

- Added GET /sentinel/stations/count
- Returns total number of stations
- Includes error handling
- Updated documentation
```

**Bad commit messages**:
```
Update
Fix stuff
WIP
```

### Branch Naming

```bash
# Features
git checkout -b feature/add-station-count
git checkout -b feature/integrate-weather-api

# Bug fixes
git checkout -b fix/oauth-token-expiry
git checkout -b fix/csv-parsing-error

# Documentation
git checkout -b docs/update-api-guide
```

### Pull Request Checklist

Before submitting a PR:

- [ ] Code runs without errors
- [ ] All existing functionality still works
- [ ] New features are tested
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No sensitive data in commits
- [ ] Code follows style guide

---

## Common Maintenance Tasks

### 1. Adding a New Configuration Variable

**Step 1**: Add to `env.example`:
```bash
NEW_CONFIG_VAR=default-value
```

**Step 2**: Add getter function in `modules/config.py`:
```python
def get_new_config_var():
    if os.getenv('NEW_CONFIG_VAR') is None:
        print("Warning: NEW_CONFIG_VAR not set")
    return os.getenv('NEW_CONFIG_VAR', 'default-value')
```

**Step 3**: Use in your code:
```python
from modules.config import get_new_config_var

value = get_new_config_var()
```

**Step 4**: Update documentation in `docs/CONFIGURATION.md`.

### 2. Adding a New External Integration

**Step 1**: Install client library:
```bash
pip install new-service-sdk
pip freeze > requirements.txt
```

**Step 2**: Create new module `modules/new_service.py`:
```python
from app import app
from modules.config import get_new_service_api_key

def get_client():
    """Get authenticated client for new service."""
    api_key = get_new_service_api_key()
    return NewServiceClient(api_key=api_key)

def fetch_data(params):
    """Fetch data from new service."""
    client = get_client()
    return client.query(params)
```

**Step 3**: Add API endpoints in `modules/api.py`:
```python
from modules.new_service import fetch_data

@app.route('/new-service/data')
def new_service_data():
    params = request.args.to_dict()
    result = fetch_data(params)
    return jsonify(result)
```

**Step 4**: Update documentation:
- Add to `docs/INTEGRATION.md`
- Add endpoints to `docs/APIS.md`

### 3. Modifying Existing Functionality

**Be careful!** Changes to existing features can break things.

**Safe approach**:

1. **Understand current behavior**: Test endpoint before changes
2. **Make changes incrementally**: One small change at a time
3. **Test after each change**: Verify nothing broke
4. **Update tests**: Reflect new behavior

**Example** - Changing image size validation:

```python
# Before (in modules/encordSync.py)
if Path(file).stat().st_size > 25000:
    # Upload file

# After - more lenient validation
MIN_FILE_SIZE = 20000  # 20KB instead of 25KB

if Path(file).stat().st_size > MIN_FILE_SIZE:
    # Upload file
    
# Test both valid and invalid cases
```

---

## Troubleshooting Checklist

When something doesn't work:

1. **Check error messages** - Read the full error output
2. **Verify configuration** - Are all .env variables set?
3. **Check file paths** - Do referenced files exist?
4. **Test API credentials** - Are they valid and not expired?
5. **Check network connectivity** - Can you reach external services?
6. **Review recent changes** - What changed since it last worked?
7. **Check logs** - Look for warnings or errors in console output
8. **Restart the application** - Sometimes a fresh start helps
9. **Ask for help** - Reach out to the team with specific error details

---

## Getting Help

### Internal Resources

- **This documentation** - Start here for most questions
- **Code comments** - Check inline documentation in code
- **Git history** - See how features were implemented: `git log`
- **Team members** - Ask experienced developers

### External Resources

- **Flask docs**: https://flask.palletsprojects.com/
- **Python docs**: https://docs.python.org/3/
- **Sentinel Hub docs**: https://docs.sentinel-hub.com/
- **ENTSOE docs**: https://transparency.entsoe.eu/
- **Encord docs**: https://docs.encord.com/

### Asking Good Questions

When asking for help, include:

1. **What you're trying to do**: "I'm trying to add a new endpoint..."
2. **What you tried**: "I added this code..."
3. **What happened**: "I got this error..."
4. **What you expected**: "I expected it to return..."
5. **Error messages**: "Full error output: ..."
6. **Environment**: "Python 3.10, Docker version..."

---

## Next Steps

Now that you understand maintenance:

- **Read** [QUICKSTART.md](./QUICKSTART.md) to set up your environment
- **Review** [FUNCTIONALITY.md](./FUNCTIONALITY.md) to understand features
- **Study** [APIS.md](./APIS.md) to learn the API
- **Start small** - Make a simple change to build confidence
- **Ask questions** - Don't hesitate to reach out for help

Welcome to the team! 🎉
