# Changelog

This document provides a chronological story of the Data Gateway application's evolution.

## Overview

The Data Gateway application was developed to create a centralized hub for collecting and managing energy infrastructure data from multiple sources. It integrates satellite imagery, energy generation data, and machine learning workflows.

---

## Development Timeline

### Phase 1: Foundation (Early 2024)

#### Initial Flask Application Setup

**What was built:**
- Basic Flask application structure with `app.py` and `run.py`
- Modular architecture with `modules/` directory
- Dynamic module loading via `modules/__init__.py`
- Configuration management with environment variables
- Docker containerization support

**Key files created:**
- `app.py` - Flask application initialization
- `run.py` - Application entry point with configurable port
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container image definition
- `docker-compose.yml` - Service orchestration
- `.gitignore` - Version control exclusions

**Technical decisions:**
- Chose Flask for lightweight REST API
- Used environment variables for configuration (12-factor app)
- Modular design for maintainability

---

### Phase 2: Configuration System

#### Environment Variable Management

**What was built:**
- Centralized configuration module (`modules/config.py`)
- Support for `.env` files with `python-dotenv`
- Validation and default values for missing configuration
- Separate functions for each configuration item

**Configuration added:**
- Sentinel Hub OAuth credentials
- ENTSOE API key
- Encord SSH private key path
- File system paths for data storage
- Dataset and project identifiers

**Why it matters:**
- Enables deployment across different environments (dev/staging/prod)
- Keeps secrets out of source code
- Makes configuration errors visible at startup

---

### Phase 3: Sentinel Hub Integration

#### Satellite Imagery Download

**What was built:**
- OAuth2 authentication with Sentinel Hub (`modules/sentinel.py`)
- Token caching to minimize auth requests
- Station management from CSV file (`modules/stations.py`)
- Image download for specific dates and locations
- Batch download with multi-threading (7 workers)

**Key features:**
- `get_oauth_token()` - Cached OAuth token management
- `download_yesterday_image_for_station()` - Single station download
- `download_all_sat_images_between_dates()` - Bulk historical download
- `get_stations_list()` - Load stations from CSV
- Duplicate detection to avoid re-downloading

**API endpoints added:**
- `GET /sentinel/stations` - List configured stations
- `GET /sentinel/stations_images` - Download latest images
- `GET /sentinel/download_station_image_yesterday` - Single station
- `POST /sentinel/download_all_station_images` - Batch download

**Technical highlights:**
- ThreadPoolExecutor for parallel downloads
- Date range iteration for historical backfill
- File naming convention: `{station-name}-{dd-mm-yyyy}.jpg`
- Image validation (size > 25KB)

---

### Phase 4: ENTSOE Integration

#### Energy Generation Data Collection

**What was built:**
- ENTSOE API integration using `entsoe-py` library (`modules/entsoe.py`)
- Support for 33 European countries
- Timezone-aware data handling
- Data transformation and CSV export
- File conversion and archival system

**Data collected:**
- Brown Coal (Fossil Brown coal/Lignite)
- Gas (Fossil Gas)
- Hard Coal (Fossil Hard coal)
- Nuclear

**Key features:**
- `get_entsoe_data()` - Single country query
- `get_entsoe_data_all_countries()` - All countries query
- `transform_to_csv()` - JSON to CSV conversion
- `convert_files_new_format()` - Daily aggregation
- `archive_converted_files()` - Move processed files

**API endpoints added:**
- `GET /entsoe` - Single country data
- `GET /entsoe/all` - All countries data
- `GET /entsoe/convert_files` - Format conversion
- `GET /entsoe/archive_converted_files` - Archive management

**Technical challenges solved:**
- Timezone conversion for each country
- Special case for Kosovo (XK) using Rome timezone
- Hourly to daily aggregation (multiply by 24)
- CSV format standardization

---

### Phase 5: Encord Integration

#### Dataset and Label Management

**What was built:**
- Encord SDK integration for dataset operations (`modules/encordSync.py`)
- SSH key authentication
- Image upload with validation
- Label retrieval and export
- Bridge system for multiple datasets

**Bridge architecture:**
- **Legacy Bridge** - Historical monitoring period
- **Forward Bridge** - Current operational monitoring
- **Catchups Bridge** - Gap filling and corrections
- Each bridge has dedicated dataset and project

**Key features:**
- `get_dataset()` - Retrieve dataset by bridge name
- `upload_image()` - Single image upload
- `upload_all_images()` - Batch upload from directory
- `list_data_rows()` - List uploaded images
- `pull_labels()` - Retrieve classifications

**API endpoints added:**
- `GET /encord` - List dataset contents
- `GET /encord/upload_image` - Upload single image
- `GET /encord/upload_all_images` - Batch upload
- `GET /encord/labels` - Get labels for date
- `GET /encord/labels/all` - Export all labels

**File management:**
- Valid uploads → moved to `/uploaded/`
- Invalid files → moved to `/unusable/`
- Validation: file size must be > 25KB

---

### Phase 6: Label Export System

#### Classification Data Export

**What was built:**
- Classification synchronization (`modules/encordClassificationsSync.py`)
- Label transformation for reporting
- CSV and JSON export formats
- Date filtering capabilities

**Export formats:**
- **Simple** - Flattened structure with key fields
- **Full** - Complete label objects with metadata

**Key features:**
- `sync_encord_labels()` - Pull labels from date forward
- Export to CSV with unique filenames
- Transform complex label objects to flat structure

**API endpoints added:**
- `GET /encord/labels/all?format=simple&media_type=csv` - CSV export
- `GET /encord/labels/all?format=full&media_type=json` - JSON export

---

### Phase 7: Synchronization Workflows

#### Combined Operations

**What was built:**
- End-to-end synchronization endpoints
- Combined download + upload operations
- Background processing for long-running tasks
- Result tracking and logging

**Workflow: Sentinel to Encord Sync**

```
1. Authenticate with Sentinel Hub
2. Download satellite image
3. Validate image (size check)
4. Authenticate with Encord
5. Upload to dataset
6. Move file to uploaded directory
7. Return metadata (data_hash, file_link)
```

**API endpoints added:**
- `GET /encord/sync_station_image_yesterday` - Download and upload in one call

**Benefits:**
- Reduces manual steps
- Ensures consistency
- Provides audit trail

---

### Phase 8: Utilities and Helpers

#### Supporting Features

**What was built:**
- Image cleanup utilities
- Error handling and logging
- Request logging middleware
- Health check endpoint

**Features:**
- `GET /sentinel/delete_existing_images` - Clean up old files
- Request logging before each API call
- Informative error messages
- Console output for debugging

---

### Phase 9: Docker and Deployment

#### Production-Ready Deployment

**What was built:**
- Multi-stage Docker configuration
- Docker Compose orchestration
- Volume mounts for persistent data
- Environment variable injection
- Port mapping configuration

**Heroku support:**
- `Procfile` for process definition
- `runtime.txt` for Python version
- Gunicorn as WSGI server

**Configuration:**
```yaml
# Port mapping
ports: "6969:6969"

# Volume mounts
volumes:
  - /home/ubuntu/config:/app/config
  - /home/ubuntu/data:/app/data

# Environment variables
environment:
  - PRIVATE_KEY_PATH=/app/config/private-key
  - IMAGES_PATH=/app/data/images/
```

---

### Phase 10: Documentation (February 2024)

#### Comprehensive Documentation Suite

**What was created:**
- `docs/QUICKSTART.md` - Getting started guide
- `docs/CONFIGURATION.md` - Configuration reference
- `docs/FUNCTIONALITY.md` - Feature descriptions
- `docs/APIS.md` - API documentation with examples
- `docs/INTEGRATION.md` - External service integration
- `docs/DEPLOYMENT.md` - Deployment guide
- `docs/MAINTENANCE.md` - Development guide
- `docs/CHANGELOG.md` - This file

**Existing docs updated:**
- `docs/behaviour.md` - Sequence diagrams
- `docs/links.md` - External resources

**Documentation features:**
- Mermaid diagrams for workflows
- Code examples in multiple languages
- Troubleshooting guides
- Security best practices
- Beginner-friendly explanations

---

## Technical Evolution

### Architecture Decisions

**Modular Design:**
- Separation of concerns (API, business logic, integration)
- Easy to extend with new integrations
- Independent module testing

**Configuration Management:**
- Environment-based configuration
- Validation at startup
- Graceful degradation with defaults

**API Design:**
- RESTful endpoints
- Query parameters for filtering
- JSON responses
- Consistent error handling

**Performance Optimizations:**
- Token caching (reduces auth overhead)
- Parallel downloads (ThreadPoolExecutor)
- Background processing (threading)
- Duplicate detection (skip existing files)

### Dependencies

**Core Framework:**
- Flask - Web framework
- Gunicorn - Production WSGI server

**External Integrations:**
- `encord` - Dataset management SDK
- `entsoe-py` - Energy data API wrapper
- `sentinelhub` - Satellite imagery SDK

**Data Processing:**
- `pandas` - Data manipulation
- `pytz` - Timezone handling

**Authentication:**
- `oauthlib` - OAuth2 implementation
- `requests_oauthlib` - OAuth for requests

**Configuration:**
- `python-dotenv` - Environment variable loading

---

## Feature Timeline Summary

| Date | Feature | Module |
|------|---------|--------|
| Q1 2024 | Flask application foundation | app.py, run.py |
| Q1 2024 | Configuration system | modules/config.py |
| Q1 2024 | Station management | modules/stations.py |
| Q1 2024 | Sentinel Hub integration | modules/sentinel.py |
| Q1 2024 | ENTSOE integration | modules/entsoe.py |
| Q1 2024 | Encord dataset operations | modules/encordSync.py |
| Q1 2024 | Label export system | modules/encordClassificationsSync.py |
| Q1 2024 | API endpoints | modules/api.py |
| Q1 2024 | Docker deployment | Dockerfile, docker-compose.yml |
| Q1 2024 | Error handling | modules/errors.py |
| Apr 2024 | Sentinel-Encord sync feature | PR #8 merged |
| Feb 2026 | Documentation suite | docs/*.md |

---

## Known Limitations and Future Work

### Current Limitations

1. **No Database**: All state is file-based
   - Labels exported to CSV
   - Image metadata in JSON files
   - No query capabilities

2. **No Authentication**: API endpoints are open
   - Anyone with access can call endpoints
   - No user management
   - No audit logging

3. **No Rate Limiting**: Can overwhelm external APIs
   - No throttling mechanism
   - Relies on external service limits

4. **Limited Error Recovery**: 
   - Failed downloads are logged but not retried
   - Manual intervention needed for failures

5. **No Monitoring**: 
   - No metrics collection
   - No alerting
   - Basic logging only

### Potential Future Enhancements

**Database Integration:**
- Store station metadata
- Track upload history
- Query label data

**Authentication & Authorization:**
- API key authentication
- Role-based access control
- User management

**Enhanced Monitoring:**
- Prometheus metrics
- Health check endpoints
- Error tracking (Sentry)

**Improved Resilience:**
- Retry logic with exponential backoff
- Circuit breaker pattern
- Queue-based processing

**Additional Integrations:**
- More satellite data sources
- Weather data APIs
- Additional energy data providers

**User Interface:**
- Web dashboard for monitoring
- Image gallery
- Label review interface

---

## Lessons Learned

### What Worked Well

1. **Modular Architecture**: Easy to add new integrations
2. **Environment-Based Config**: Smooth deployment across environments
3. **Docker Deployment**: Consistent runtime environment
4. **Parallel Processing**: Efficient bulk operations
5. **Token Caching**: Reduced auth overhead

### What Could Be Improved

1. **Error Handling**: More robust retry logic needed
2. **Testing**: Limited test coverage
3. **Documentation**: Could have been written earlier
4. **Monitoring**: Need better visibility into operations
5. **Database**: File-based storage doesn't scale well

---

## Contributors

- Development team at Xterna
- Integration with external APIs: Sentinel Hub, ENTSOE, Encord
- Documentation by GitHub Copilot

---

## Version History

### v1.0 (April 2024)
- Initial release with full feature set
- Sentinel Hub, ENTSOE, and Encord integrations
- Docker deployment support
- REST API with 15+ endpoints

### v1.1 (February 2026)
- Comprehensive documentation added
- 8 detailed guides for developers
- Improved onboarding for new engineers

---

## References

For more details on specific features, see:
- [FUNCTIONALITY.md](./FUNCTIONALITY.md) - Detailed feature descriptions
- [APIS.md](./APIS.md) - API endpoint documentation
- [INTEGRATION.md](./INTEGRATION.md) - External service details
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment instructions
