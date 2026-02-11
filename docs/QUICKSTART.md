# Quickstart Guide

Welcome! This guide will help you get the Data Gateway application running on your local machine.

## What is the Data Gateway App?

The Data Gateway is a Python web application that acts as a central hub for collecting, processing, and distributing energy infrastructure data. It integrates with:

- **Sentinel Hub** - Downloads satellite images of power stations
- **ENTSOE** - Retrieves European energy generation data
- **Encord** - Uploads and manages image datasets for analysis

Think of it as a "data highway" that connects these services together.

## Prerequisites

Before you start, you'll need to install:

1. **Docker** - A tool that packages applications with their dependencies
   - [Install Docker](https://docs.docker.com/get-docker/)
   - After installing, verify by running: `docker --version`

2. **Python 3.10** (if running without Docker)
   - [Install Python](https://www.python.org/downloads/)
   - Verify: `python --version`

3. **Git** - Version control system
   - [Install Git](https://git-scm.com/downloads/)
   - Verify: `git --version`

## Quick Setup (5 minutes)

### Step 1: Clone the Repository

```bash
# Clone the code to your computer
git clone https://github.com/Xterna-admin/data-gateway-app.git

# Navigate into the project folder
cd data-gateway-app
```

### Step 2: Configure Environment Variables

The app needs credentials to connect to external services. Copy the example configuration:

```bash
# Copy the example configuration file
cp env.example .env
```

Now open `.env` in a text editor and fill in the required values:

```bash
# Essential configuration
PRIVATE_KEY_PATH=/path/to/your/encord-private-key
SENTINEL_CLIENT_ID=your-sentinel-client-id
SENTINEL_CLIENT_SECRET=your-sentinel-client-secret
ENTSOE_API_KEY=your-entsoe-api-key
STATIONS_CSV_PATH=/path/to/stations.csv
IMAGES_PATH=/path/to/images/
```

> **Note**: Contact your team lead to get the actual API keys and credentials.

### Step 3: Run with Docker (Recommended)

```bash
# Build the Docker image
docker build -t data-gateway-app:1 .

# Run the application
docker-compose up
```

The application will start on `http://localhost:6969`

### Step 4: Verify It's Working

Open your browser and visit:
- `http://localhost:6969/api` - You should see: `{"message":"Hello from Flask!"}`

Congratulations! Your app is running! 🎉

## Alternative: Run Without Docker

If you prefer to run directly with Python:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export PRIVATE_KEY_PATH=/path/to/your/key
export SENTINEL_CLIENT_ID=your-id
# ... set other variables from .env

# Run the application
python run.py
```

The app will start on `http://localhost:6969`

## Project Structure

```
data-gateway-app/
├── app.py                  # Main Flask application setup
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container configuration
├── docker-compose.yml     # Docker orchestration
├── modules/               # Application logic
│   ├── api.py            # API endpoints
│   ├── sentinel.py       # Sentinel Hub integration
│   ├── entsoe.py         # ENTSOE data integration
│   ├── encordSync.py     # Encord dataset management
│   └── config.py         # Configuration helpers
├── docs/                  # Documentation
└── config/               # Configuration files
```

## What Can I Do Now?

Now that your app is running, you can:

1. **View Available Stations**
   ```bash
   curl http://localhost:6969/sentinel/stations
   ```

2. **Fetch Energy Data**
   ```bash
   curl "http://localhost:6969/entsoe?country_code=AT&start=20240101&end=20240102"
   ```

3. **List Encord Datasets**
   ```bash
   curl http://localhost:6969/encord?bridge=forward
   ```

See [APIS.md](./APIS.md) for complete API documentation.

## Common Issues

### Port Already in Use

If port 6969 is already taken, you can change it:

```bash
# Edit docker-compose.yml and change the port mapping
ports:
  - "8080:6969"  # Changes local port to 8080
```

### Missing Environment Variables

If you see errors about missing variables:
1. Check your `.env` file is in the project root
2. Verify all required variables are set
3. Restart the application

### Docker Build Fails

Try cleaning Docker's cache:
```bash
docker system prune -a
docker build --no-cache -t data-gateway-app:1 .
```

## Next Steps

- Read [CONFIGURATION.md](./CONFIGURATION.md) to understand all configuration options
- Check [FUNCTIONALITY.md](./FUNCTIONALITY.md) to learn what the app does
- Review [APIS.md](./APIS.md) for detailed API documentation
- See [MAINTENANCE.md](./MAINTENANCE.md) for making changes

## Getting Help

- Check existing documentation in the `docs/` folder
- Review the [links.md](./links.md) file for external resources
- Contact the development team for credentials and access
