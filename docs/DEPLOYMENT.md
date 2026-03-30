# Deployment Guide

This document covers deploying the Data Gateway application using Docker and other deployment methods.

## Overview

The application can be deployed in several ways:
1. **Docker Compose** (Recommended for production)
2. **Docker Container** (Manual deployment)
3. **Bare Metal** (Direct Python execution)
4. **Heroku** (Platform as a Service)

---

## Docker Deployment (Recommended)

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 1.29+
- 2GB RAM minimum
- 10GB disk space for images

### Project Structure

```
data-gateway-app/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Container orchestration
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration (create from env.example)
├── app.py                  # Flask app initialization
├── run.py                  # Application entry point
└── modules/                # Application code
```

---

## Dockerfile Explained

```dockerfile
# Start from Python 3.10 slim image (smaller size)
FROM python:3.10-slim-buster

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY ./requirements.txt /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port 5000 (internal container port)
EXPOSE 5000

# Set entry point
ENTRYPOINT ["python"]

# Default command (can be overridden)
CMD ["run.py"]
```

**Key Points**:
- **Slim base image**: Reduces image size (~150MB vs 900MB)
- **Layer caching**: Dependencies installed before code copy (faster rebuilds)
- **Port 5000**: Internal port (mapped differently externally)

---

## Docker Compose Configuration

`docker-compose.yml` defines the service configuration:

```yaml
version: "3"

services:
  data-gateway:
    # Use pre-built image
    image: data-gateway-app:1
    
    # Port mapping: host:container
    ports:
      - "6969:6969"
    
    # Environment variables
    environment:
      - PRIVATE_KEY_PATH=/app/config/xternanewkey-private-key
      - SERVER_PORT=3999
      - SENTINEL_CLIENT_ID=your-client-id
      - SENTINEL_CLIENT_SECRET=your-client-secret
      - STATIONS_CSV_PATH=/app/config/stations.csv
      - IMAGES_PATH=/app/data/images/
      # ... more variables
    
    # Keep stdin open for interactive debugging
    stdin_open: true
    
    # Mount local directories into container
    volumes:
      - /home/ubuntu/config:/app/config
      - /home/ubuntu/data:/app/data
```

**Volume Mounts Explained**:

```
Local Path              →  Container Path
/home/ubuntu/config     →  /app/config     (Configuration files)
/home/ubuntu/data       →  /app/data       (Data storage)
```

**Why volumes?**
- Persist data outside container
- Share files between host and container
- Easy backup and recovery

---

## Building the Docker Image

### Step 1: Build the Image

```bash
# Build from Dockerfile
docker build -t data-gateway-app:1 .

# Build with no cache (if you have issues)
docker build --no-cache -t data-gateway-app:1 .
```

**Explanation**:
- `-t data-gateway-app:1` - Tag image as "data-gateway-app" version "1"
- `.` - Use Dockerfile in current directory

**Output**:
```
[+] Building 45.3s (10/10) FINISHED
 => [1/5] FROM python:3.10-slim-buster
 => [2/5] WORKDIR /app
 => [3/5] COPY ./requirements.txt /app
 => [4/5] RUN pip install -r requirements.txt
 => [5/5] COPY . .
 => exporting to image
```

### Step 2: Verify Image

```bash
# List Docker images
docker images

# Output:
REPOSITORY            TAG       IMAGE ID       SIZE
data-gateway-app      1         a1b2c3d4e5f6   500MB
```

---

## Running with Docker Compose

### Step 1: Prepare Environment

```bash
# Create data directories
mkdir -p /home/ubuntu/config
mkdir -p /home/ubuntu/data/images
mkdir -p /home/ubuntu/data/entsoe-download
mkdir -p /home/ubuntu/data/entsoe-revised-output
mkdir -p /home/ubuntu/data/entsoe-revised-archive

# Copy configuration files
cp your-private-key /home/ubuntu/config/xternanewkey-private-key
cp stations.csv /home/ubuntu/config/stations.csv

# Set permissions
chmod 600 /home/ubuntu/config/xternanewkey-private-key
chmod 644 /home/ubuntu/config/stations.csv
```

### Step 2: Update Configuration

Edit `docker-compose.yml` with your values:

```yaml
environment:
  - PRIVATE_KEY_PATH=/app/config/xternanewkey-private-key
  - SENTINEL_CLIENT_ID=your-actual-client-id
  - SENTINEL_CLIENT_SECRET=your-actual-client-secret
  - ENTSOE_API_KEY=your-actual-api-key
  # ... update all values
```

**Security Note**: Don't commit docker-compose.yml with real credentials!

### Step 3: Start the Application

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f data-gateway

# Stop the application
docker-compose down
```

### Step 4: Verify It's Running

```bash
# Check container status
docker ps

# Test API
curl http://localhost:6969/api

# Expected response:
{"message":"Hello from Flask!"}
```

---

## Running Without Docker Compose

### Manual Docker Run

```bash
docker run -d \
  --name data-gateway \
  -p 6969:6969 \
  -v /home/ubuntu/config:/app/config \
  -v /home/ubuntu/data:/app/data \
  -e PRIVATE_KEY_PATH=/app/config/xternanewkey-private-key \
  -e SENTINEL_CLIENT_ID=your-id \
  -e SENTINEL_CLIENT_SECRET=your-secret \
  -e ENTSOE_API_KEY=your-key \
  -e STATIONS_CSV_PATH=/app/config/stations.csv \
  -e IMAGES_PATH=/app/data/images/ \
  data-gateway-app:1
```

**Parameters**:
- `-d` - Run in detached mode (background)
- `--name` - Container name
- `-p` - Port mapping (host:container)
- `-v` - Volume mount
- `-e` - Environment variable

---

## Bare Metal Deployment

### Prerequisites

- Python 3.10
- pip
- Virtual environment (recommended)

### Step 1: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example configuration
cp env.example .env

# Edit .env with your values
nano .env
```

### Step 3: Run Application

```bash
# Development mode
python run.py

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:6969 app:app
```

**Gunicorn Parameters**:
- `-w 4` - 4 worker processes
- `-b 0.0.0.0:6969` - Bind to all interfaces on port 6969
- `app:app` - Import `app` from `app.py`

---

## Heroku Deployment

The application includes Heroku configuration files.

### Files

**Procfile**:
```
web: gunicorn app:app
```

**runtime.txt**:
```
python-3.10.0
```

### Deployment Steps

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SENTINEL_CLIENT_ID=your-id
heroku config:set SENTINEL_CLIENT_SECRET=your-secret
heroku config:set ENTSOE_API_KEY=your-key
# ... set all required variables

# Deploy
git push heroku main

# Open app
heroku open
```

**Note**: File storage on Heroku is ephemeral. Consider using S3 or similar for persistent storage.

---

## Production Considerations

### 1. Process Management

Use a process manager to keep the application running:

**systemd Service** (Linux):

Create `/etc/systemd/system/data-gateway.service`:

```ini
[Unit]
Description=Data Gateway Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/data-gateway-app
Environment="PATH=/home/ubuntu/data-gateway-app/venv/bin"
EnvironmentFile=/home/ubuntu/data-gateway-app/.env
ExecStart=/home/ubuntu/data-gateway-app/venv/bin/gunicorn -w 4 -b 0.0.0.0:6969 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
sudo systemctl enable data-gateway
sudo systemctl start data-gateway
sudo systemctl status data-gateway
```

### 2. Reverse Proxy (Nginx)

Place Nginx in front of the application:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:6969;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

### 3. SSL/TLS Certificate

Use Let's Encrypt with certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. Logging

**Docker Compose Logging**:

```yaml
services:
  data-gateway:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**View logs**:
```bash
docker-compose logs -f --tail=100 data-gateway
```

**Bare Metal Logging**:

Configure in Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:6969 \
  --access-logfile /var/log/data-gateway/access.log \
  --error-logfile /var/log/data-gateway/error.log \
  app:app
```

### 5. Health Checks

Add health check to Docker Compose:

```yaml
services:
  data-gateway:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6969/api"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 6. Resource Limits

Limit container resources:

```yaml
services:
  data-gateway:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## Backup and Recovery

### Data Backup

```bash
# Backup configuration
tar -czf config-backup-$(date +%Y%m%d).tar.gz /home/ubuntu/config/

# Backup data directory
tar -czf data-backup-$(date +%Y%m%d).tar.gz /home/ubuntu/data/

# Backup to S3 (if using AWS)
aws s3 cp config-backup-*.tar.gz s3://your-bucket/backups/
aws s3 cp data-backup-*.tar.gz s3://your-bucket/backups/
```

### Database/State Backup

If you add a database (PostgreSQL, etc.):

```bash
# Backup PostgreSQL
pg_dump -U postgres data_gateway > backup.sql

# Restore
psql -U postgres data_gateway < backup.sql
```

### Docker Image Backup

```bash
# Save image
docker save data-gateway-app:1 | gzip > data-gateway-app-1.tar.gz

# Load image
docker load < data-gateway-app-1.tar.gz
```

---

## Monitoring

### Docker Stats

```bash
# View resource usage
docker stats data-gateway

# Output:
CONTAINER      CPU %     MEM USAGE / LIMIT     NET I/O           BLOCK I/O
data-gateway   0.50%     150MB / 2GB           1.2MB / 856KB     10MB / 2MB
```

### Application Metrics

Add monitoring endpoints to `modules/api.py`:

```python
import psutil
import os

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "uptime": time.time() - start_time,
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    })
```

### External Monitoring

Integrate with monitoring services:
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Datadog** - Full observability
- **Sentry** - Error tracking

---

## Security Best Practices

### 1. Secrets Management

**Don't**:
- Commit credentials to git
- Put credentials in docker-compose.yml

**Do**:
```bash
# Use Docker secrets
echo "your-api-key" | docker secret create entsoe_api_key -

# Use in compose file
services:
  data-gateway:
    secrets:
      - entsoe_api_key

secrets:
  entsoe_api_key:
    external: true
```

### 2. Network Security

```yaml
# Restrict network access
services:
  data-gateway:
    networks:
      - internal

networks:
  internal:
    internal: true
```

### 3. User Permissions

Don't run as root:

```dockerfile
# Add to Dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### 4. Regular Updates

```bash
# Update base image
docker pull python:3.10-slim-buster

# Rebuild
docker build -t data-gateway-app:1 .

# Update dependencies
pip install --upgrade -r requirements.txt
```

---

## Troubleshooting Deployment

### Container Won't Start

```bash
# Check logs
docker logs data-gateway

# Check if port is in use
sudo lsof -i :6969

# Check file permissions
ls -la /home/ubuntu/config/
```

### Out of Memory

```bash
# Increase Docker memory limit
# Edit /etc/docker/daemon.json
{
  "default-address-pools": [
    {"base": "172.17.0.0/16", "size": 24}
  ],
  "memory": "2g"
}

# Restart Docker
sudo systemctl restart docker
```

### Volume Mount Issues

```bash
# Check if directory exists
ls -la /home/ubuntu/config/

# Check SELinux (if applicable)
sudo chcon -Rt svirt_sandbox_file_t /home/ubuntu/config/

# Or add :z to volume mount
volumes:
  - /home/ubuntu/config:/app/config:z
```

---

## Scaling

### Horizontal Scaling

Run multiple instances behind a load balancer:

```yaml
services:
  data-gateway:
    deploy:
      replicas: 3
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

**nginx.conf**:
```nginx
upstream data_gateway {
    server data-gateway-1:6969;
    server data-gateway-2:6969;
    server data-gateway-3:6969;
}

server {
    listen 80;
    location / {
        proxy_pass http://data_gateway;
    }
}
```

### Kubernetes Deployment

For larger deployments, use Kubernetes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: data-gateway
  template:
    metadata:
      labels:
        app: data-gateway
    spec:
      containers:
      - name: data-gateway
        image: data-gateway-app:1
        ports:
        - containerPort: 6969
        env:
        - name: SENTINEL_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: data-gateway-secrets
              key: sentinel-client-id
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All environment variables configured
- [ ] Credentials stored securely (not in git)
- [ ] SSL/TLS certificate configured
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Health checks working
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Rollback plan prepared

---

## Next Steps

- Review [CONFIGURATION.md](./CONFIGURATION.md) for environment setup
- Check [MAINTENANCE.md](./MAINTENANCE.md) for ongoing operations
- Read [APIS.md](./APIS.md) to understand endpoints
