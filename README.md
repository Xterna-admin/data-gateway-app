# Data Gateway Application

A Python Flask application that integrates satellite imagery, energy generation data, and machine learning workflows for monitoring power infrastructure.

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# Clone the repository
git clone https://github.com/Xterna-admin/data-gateway-app.git
cd data-gateway-app

# Build and run with Docker
docker build -t data-gateway-app:1 .
docker-compose up

# Verify it's working
curl http://localhost:6969/api
```

**👉 [Full Quick Start Guide](./docs/QUICKSTART.md)**

## 📖 Documentation

Comprehensive documentation for all skill levels:

### Getting Started
- **[Quick Start Guide](./docs/QUICKSTART.md)** - Get running in 5 minutes
- **[Configuration Guide](./docs/CONFIGURATION.md)** - Environment setup and config options

### Using the Application
- **[Functionality Guide](./docs/FUNCTIONALITY.md)** - What the application does
- **[API Documentation](./docs/APIS.md)** - Complete API reference with examples

### Integration & Deployment
- **[Integration Guide](./docs/INTEGRATION.md)** - External services (Sentinel, ENTSOE, Encord)
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Docker and production deployment

### Development
- **[Maintenance Guide](./docs/MAINTENANCE.md)** - Development workflow and testing
- **[Changelog](./docs/CHANGELOG.md)** - Project history and evolution

**📚 [Complete Documentation Index](./docs/README.md)**

## 🎯 What Does It Do?

The Data Gateway integrates three key services:

```
┌─────────────────────────────────────────────┐
│         Data Gateway Application            │
│                                             │
│  Sentinel Hub  →  ENTSOE  →  Encord        │
│  (Satellites)     (Energy)    (ML)          │
└─────────────────────────────────────────────┘
```

1. **Satellite Imagery** - Downloads images of power stations from Sentinel Hub
2. **Energy Data** - Retrieves electricity generation data from ENTSOE
3. **ML Workflows** - Manages datasets and labels in Encord

## 🔧 Technology Stack

- **Framework:** Flask (Python 3.10)
- **Server:** Gunicorn
- **Deployment:** Docker / Docker Compose
- **Integrations:** Sentinel Hub, ENTSOE, Encord APIs
- **Data Processing:** Pandas, Python-dotenv

## 🌐 API Endpoints

The application provides REST APIs for:

- `/sentinel/*` - Satellite image operations
- `/entsoe/*` - Energy generation data
- `/encord/*` - Dataset and label management

**👉 [Complete API Documentation](./docs/APIS.md)**

## 🚀 Deployment

### Docker (Recommended)

```bash
docker build -t data-gateway-app:1 .
docker-compose up -d
```

### Python

```bash
pip install -r requirements.txt
python run.py
```

**👉 [Full Deployment Guide](./docs/DEPLOYMENT.md)**

## ⚙️ Configuration

Essential environment variables:

```bash
SENTINEL_CLIENT_ID=your-client-id
SENTINEL_CLIENT_SECRET=your-client-secret
ENTSOE_API_KEY=your-api-key
PRIVATE_KEY_PATH=/path/to/encord-key
STATIONS_CSV_PATH=/path/to/stations.csv
```

**👉 [Complete Configuration Guide](./docs/CONFIGURATION.md)**

## 🧪 Development

```bash
# Set up development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run locally
python run.py

# Test API
curl http://localhost:6969/api
```

**👉 [Full Maintenance Guide](./docs/MAINTENANCE.md)**

## 📊 Project Status

- **Version:** 1.1
- **Status:** Production
- **Last Updated:** February 2026
- **Python Version:** 3.10

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

**👉 [Development Guidelines](./docs/MAINTENANCE.md)**

## 📝 License

[Add your license information here]

## 🙏 Acknowledgments

- Sentinel Hub for satellite imagery APIs
- ENTSOE for energy transparency data
- Encord for ML dataset management

## 📧 Support

For questions or issues:
- Check the [documentation](./docs/README.md)
- Review existing issues
- Contact the development team

---

**Built with ❤️ by the Xterna team**
