# Configuration Guide

This document explains all configuration options for the Data Gateway application. Configuration is done through environment variables, which can be set in a `.env` file or directly in your environment.

## Overview

The application uses environment variables to:
- Connect to external services (Sentinel, ENTSOE, Encord)
- Define file paths for data storage
- Specify which datasets and projects to use

## Configuration File

Copy `env.example` to `.env` in the project root:

```bash
cp env.example .env
```

Then edit `.env` with your specific values.

## Required Configuration

These variables **must** be set for the application to work:

### Encord Configuration

Encord is a platform for managing and labeling image datasets.

```bash
# Path to your Encord SSH private key file
PRIVATE_KEY_PATH=/path/to/encord-private-key
```

**What it's for**: Authenticates with Encord to upload and manage images.

**How to get it**: 
1. Log in to your Encord account
2. Navigate to Settings → API Keys
3. Generate an SSH key pair and download the private key

---

### Sentinel Hub Configuration

Sentinel Hub provides satellite imagery APIs.

```bash
# Your Sentinel Hub OAuth2 client ID
SENTINEL_CLIENT_ID=your-client-id-here

# Your Sentinel Hub OAuth2 client secret
SENTINEL_CLIENT_SECRET=your-client-secret-here
```

**What it's for**: Downloads satellite images of power stations.

**How to get it**:
1. Create an account at [Sentinel Hub](https://www.sentinel-hub.com/)
2. Go to Dashboard → OAuth clients
3. Create a new OAuth client and copy the credentials

---

### ENTSOE Configuration

ENTSOE provides European electricity network data.

```bash
# Your ENTSOE API key
ENTSOE_API_KEY=your-api-key-here
```

**What it's for**: Fetches energy generation data by country and fuel type.

**How to get it**:
1. Register at [ENTSOE Transparency Platform](https://transparency.entsoe.eu/)
2. Go to Account Settings → API Access
3. Request an API key (may take a few days to approve)

---

## Path Configuration

These define where files are stored and loaded:

### Station Data

```bash
# Path to CSV file containing power station locations
STATIONS_CSV_PATH=/path/to/stations.csv
```

**Format of stations.csv**:
```csv
Name,L1,L2,L3,L4,Collection ID
Andong power station,128.545254,36.599082,128.537342,36.59273,34170c46-7edb-491d-8a5e-69e7bfd4a741
```

- **Name**: Station name
- **L1, L2, L3, L4**: Bounding box coordinates (longitude and latitude)
- **Collection ID**: Sentinel Hub data collection identifier

---

### Image Storage

```bash
# Directory to store downloaded satellite images
IMAGES_PATH=/path/to/images/

# Directory for ENTSOE CSV downloads
ENTSOE_CSV_PATH=/path/to/entsoe-download/

# Directory for converted ENTSOE files
ENTSOE_OUTPUT_DIR=/path/to/entsoe-revised-output/

# Directory to archive processed ENTSOE files
ENTSOE_ARCHIVE_DIR=/path/to/entsoe-revised-archive/

# Directory for Encord label exports
ENCORD_CSV_PATH=/path/to/encord-download/
```

**Important**: Make sure these directories exist and are writable!

```bash
# Create all required directories
mkdir -p /path/to/images/
mkdir -p /path/to/entsoe-download/
mkdir -p /path/to/entsoe-revised-output/
mkdir -p /path/to/entsoe-revised-archive/
mkdir -p /path/to/encord-download/
```

---

## Encord Dataset Configuration

Encord organizes data into "datasets" (storage) and "projects" (labeling workflows).

### Dataset IDs

```bash
# Test dataset for experimentation
ENCORD_TEST_DATASET=d5e93353-9aaf-437d-948e-7cdbf37ed80c

# Legacy bridge dataset
ENCORD_LEGACY_BRIDGE_DATASET=85bf029e-7acb-4d4a-b8e2-f09835e4f747

# Forward bridge dataset
ENCORD_FORWARD_BRIDGE_DATASET=227ab75e-e12d-4f85-b468-71ea39c145ce

# Catchups dataset
ENCORD_CATCHUPS_DATASET=b74c498f-7439-49c9-8aba-d84625735c63
```

**What are "bridges"?** These are different monitoring periods or regions for the power infrastructure.

### Project IDs

```bash
# Legacy bridge project for labeling
ENCORD_LEGACY_BRIDGE_PROJECT=dd63e4d3-4334-48d7-8b7e-493e751f2e40

# Forward bridge project
ENCORD_FORWARD_BRIDGE_PROJECT=a42b4944-7b2b-489b-b606-e8328475effc

# Catchups project (optional)
ENCORD_CATCHUPS_PROJECT=your-catchups-project-id
```

**How to get these IDs**:
1. Log in to Encord
2. Navigate to your dataset/project
3. The ID is in the URL: `https://app.encord.com/projects/PROJECT_ID`

---

## Optional Configuration

### Server Configuration

```bash
# Port the Flask server listens on (default: 6969)
PORT=6969
```

### Data Tracking

```bash
# JSON file to track all bridge data hashes
ALL_BRIDGES_DATAHASHES=/path/to/all_bridges_data_hashes.json
```

This file is used to avoid re-downloading images that already exist in Encord.

---

## Docker Configuration

When running with Docker, configuration is set in `docker-compose.yml`:

```yaml
environment:
  - PRIVATE_KEY_PATH=/app/config/xternanewkey-private-key
  - SERVER_PORT=3999
  - SENTINEL_CLIENT_ID=your-id
  - SENTINEL_CLIENT_SECRET=your-secret
  # ... other variables
```

**Volume Mounts**:
```yaml
volumes:
  - /home/ubuntu/config:/app/config
  - /home/ubuntu/data:/app/data
```

This maps local directories to container paths:
- `/home/ubuntu/config` → `/app/config` (configuration files)
- `/home/ubuntu/data` → `/app/data` (data storage)

---

## Configuration in Code

Configuration is loaded in `modules/config.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

def get_sentinel_clientId():
    return os.getenv('SENTINEL_CLIENT_ID', None)
```

**How it works**:
1. `load_dotenv()` reads `.env` file
2. `os.getenv()` retrieves variable values
3. Second parameter is the default if variable is not set

---

## Validation

The application will print warnings for missing configuration:

```
Please provide a Sentinel Client ID in .env file.
Please provide an Entsoe API Key in .env file.
```

Check the console output when starting the app to ensure all required variables are set.

---

## Environment-Specific Configuration

### Development

```bash
# Use test datasets
ENCORD_TEST_DATASET=d5e93353-9aaf-437d-948e-7cdbf37ed80c

# Store images locally
IMAGES_PATH=/tmp/images/
```

### Production

```bash
# Use production datasets
ENCORD_FORWARD_BRIDGE_DATASET=227ab75e-e12d-4f85-b468-71ea39c145ce

# Store on mounted volume
IMAGES_PATH=/app/data/images/
```

---

## Security Best Practices

1. **Never commit `.env` files** - They contain secrets!
2. **Use environment-specific files** - `.env.development`, `.env.production`
3. **Rotate API keys regularly** - Update credentials periodically
4. **Restrict file permissions** - `chmod 600 .env`
5. **Use secrets management** - Consider using AWS Secrets Manager or similar for production

---

## Troubleshooting

### "Please provide X in .env file"

**Problem**: Required environment variable is missing.

**Solution**: 
1. Check `.env` file exists in project root
2. Verify variable is spelled correctly (case-sensitive)
3. Ensure no extra spaces around `=`

### "FileNotFoundError: CSV file not found"

**Problem**: Path to stations.csv is incorrect.

**Solution**:
```bash
# Use absolute paths
STATIONS_CSV_PATH=/full/path/to/stations.csv

# Or relative to project root
STATIONS_CSV_PATH=./config/stations.csv
```

### Images Not Saving

**Problem**: Directory doesn't exist or lacks write permissions.

**Solution**:
```bash
# Create directory
mkdir -p /path/to/images/

# Set permissions
chmod 755 /path/to/images/
```

---

## Configuration Reference

Quick reference table:

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| PRIVATE_KEY_PATH | ✅ | None | Encord authentication |
| SENTINEL_CLIENT_ID | ✅ | None | Sentinel OAuth ID |
| SENTINEL_CLIENT_SECRET | ✅ | None | Sentinel OAuth secret |
| ENTSOE_API_KEY | ✅ | None | ENTSOE API access |
| STATIONS_CSV_PATH | ✅ | None | Station locations |
| IMAGES_PATH | ⚠️ | /tmp | Image storage |
| ENTSOE_CSV_PATH | ⚠️ | None | ENTSOE downloads |
| ENTSOE_OUTPUT_DIR | ⚠️ | None | ENTSOE processed |
| ENTSOE_ARCHIVE_DIR | ⚠️ | None | ENTSOE archive |
| ENCORD_CSV_PATH | ⚠️ | None | Encord exports |
| PORT | ❌ | 6969 | Server port |

✅ = Required | ⚠️ = Recommended | ❌ = Optional

---

## Next Steps

- See [QUICKSTART.md](./QUICKSTART.md) for setup instructions
- Read [APIS.md](./APIS.md) to understand API endpoints
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
