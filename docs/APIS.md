# API Documentation

This document provides complete documentation for all REST API endpoints in the Data Gateway application.

## Base URL

```
http://localhost:6969
```

When deployed, replace with your production URL.

## API Overview

The API is organized into three main sections:

1. **Sentinel APIs** - Satellite image operations
2. **ENTSOE APIs** - Energy generation data
3. **Encord APIs** - Dataset and label management

---

## Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api` | GET | Health check |
| `/sentinel/stations` | GET | List all stations |
| `/sentinel/stations_images` | GET | Download latest images |
| `/sentinel/download_station_image_yesterday` | GET | Download single station image |
| `/sentinel/download_all_station_images` | POST | Batch download date range |
| `/sentinel/delete_existing_images` | GET | Clean up image directory |
| `/entsoe` | GET | Get energy data (single country) |
| `/entsoe/all` | GET | Get energy data (all countries) |
| `/entsoe/convert_files` | GET | Convert CSV files to new format |
| `/entsoe/archive_converted_files` | GET | Archive processed files |
| `/encord` | GET | List dataset images |
| `/encord/upload_image` | GET | Upload single image |
| `/encord/upload_all_images` | GET | Upload all images from directory |
| `/encord/labels` | GET | Get labels for date |
| `/encord/labels/all` | GET | Export all labels |
| `/encord/sync_station_image_yesterday` | GET | Download + upload single image |

---

## Health Check

### GET /api

Simple health check endpoint to verify the service is running.

**Example Request**:
```bash
curl http://localhost:6969/api
```

**Example Response**:
```json
{
  "message": "Hello from Flask!"
}
```

---

## Sentinel Hub APIs

### GET /sentinel/stations

Returns a list of all power stations configured in the stations.csv file.

**Example Request**:
```bash
curl http://localhost:6969/sentinel/stations
```

**Example Response**:
```json
[
  {
    "station": "Andong power station",
    "l1": 128.545254,
    "l2": 36.599082,
    "l3": 128.537342,
    "l4": 36.59273,
    "collectionID": "34170c46-7edb-491d-8a5e-69e7bfd4a741"
  },
  {
    "station": "Ansan power station",
    "l1": 126.123456,
    "l2": 37.234567,
    "l3": 126.112233,
    "l4": 37.223344,
    "collectionID": "34170c46-7edb-491d-8a5e-69e7bfd4a741"
  }
]
```

**Response Fields**:
- `station` - Power station name
- `l1, l2, l3, l4` - Bounding box coordinates (longitude/latitude)
- `collectionID` - Sentinel Hub collection identifier

---

### GET /sentinel/stations_images

Downloads the latest (yesterday's) satellite image for all configured stations.

**Example Request**:
```bash
curl http://localhost:6969/sentinel/stations_images
```

**Example Response**:
```json
[
  {
    "station": "Andong power station",
    "date": "2024-01-15",
    "image_filename": "/path/to/images/Andong-power-station-15-01-2024.jpg",
    "file_size": 125678
  },
  {
    "station": "Ansan power station",
    "date": "2024-01-15",
    "image_filename": "/path/to/images/Ansan-power-station-15-01-2024.jpg",
    "file_size": 132456
  }
]
```

**Notes**:
- Only downloads for stations with a `collectionID`
- Skips stations if image already exists
- Images saved to configured `IMAGES_PATH`

---

### GET /sentinel/download_station_image_yesterday

Downloads yesterday's satellite image for a specific station.

**Query Parameters**:
- `station` (required) - Station name (e.g., "Andong power station")
- `l1` (required) - Bounding box coordinate 1
- `l2` (required) - Bounding box coordinate 2
- `l3` (required) - Bounding box coordinate 3
- `l4` (required) - Bounding box coordinate 4
- `collectionID` (required) - Sentinel Hub collection ID

**Example Request**:
```bash
curl "http://localhost:6969/sentinel/download_station_image_yesterday?\
station=Andong%20power%20station&\
l1=128.545254&\
l2=36.599082&\
l3=128.537342&\
l4=36.59273&\
collectionID=34170c46-7edb-491d-8a5e-69e7bfd4a741"
```

**Example Response**:
```json
{
  "station": "Andong power station",
  "date": "2024-01-15",
  "image_filename": "/path/to/images/Andong-power-station-15-01-2024.jpg",
  "file_size": 125678,
  "status": "success"
}
```

---

### POST /sentinel/download_all_station_images

Batch download satellite images for all stations across a date range. This runs in a background thread and returns immediately.

**Query Parameters**:
- `start_date` (required) - Start date in format YYYY-MM-DD
- `end_date` (optional) - End date in format YYYY-MM-DD (defaults to today)

**Request Body**: Empty JSON object `{}`

**Example Request**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  "http://localhost:6969/sentinel/download_all_station_images?\
start_date=2024-01-01&\
end_date=2024-01-31"
```

**Example Response**:
```json
{
  "message": "Request accepted"
}
```

**Notes**:
- Returns immediately (201 status)
- Downloads continue in background thread
- Uses 7 parallel workers for performance
- Skips existing images
- Results saved to `all_bridges_data_hashes-output.json`

**Background Process**:
```
For each date in range:
  For each station:
    1. Check if image exists locally or in Encord
    2. If not, download from Sentinel Hub
    3. Save to IMAGES_PATH
```

---

### GET /sentinel/delete_existing_images

Deletes images from the images directory with date format validation.

**Example Request**:
```bash
curl http://localhost:6969/sentinel/delete_existing_images
```

**Example Response**:
```json
{
  "deleted_count": 42,
  "deleted_files": [
    "Andong-power-station-15-01-2024.jpg",
    "Ansan-power-station-15-01-2024.jpg"
  ]
}
```

**Warning**: This is a destructive operation. Use with caution!

---

## ENTSOE APIs

### GET /entsoe

Fetch energy generation data for a single country and date range.

**Query Parameters**:
- `country_code` (required) - ISO 2-letter country code (e.g., AT, DE, FR)
- `start` (required) - Start date in format YYYYMMDD
- `end` (required) - End date in format YYYYMMDD

**Supported Countries**:
AT, BA, BE, BG, CH, CZ, DE, DK, EE, ES, FI, FR, GR, HR, HU, IE, IT, LT, LU, LV, ME, MK, NL, NO, PL, PT, RO, RS, SE, SK, XK, SI, GE

**Example Request**:
```bash
curl "http://localhost:6969/entsoe?\
country_code=AT&\
start=20240101&\
end=20240102"
```

**Example Response**:
```json
{
  "file": "/path/to/entsoe-download/AT-entsoe_data.csv",
  "country": "AT"
}
```

**CSV File Format**:
```csv
Reading date,Country,Brown Coal,Gas,Hard Coal,Nuclear,Source,Reading Type
2024-01-01 00:00:00,AT,1234.0,567.8,890.2,456.3,entsoe,actual
2024-01-01 01:00:00,AT,1245.1,572.3,895.7,458.9,entsoe,actual
```

**Data Fields**:
- `Reading date` - Timestamp (local timezone)
- `Country` - Country code
- `Brown Coal` - Generation in MW
- `Gas` - Generation in MW
- `Hard Coal` - Generation in MW
- `Nuclear` - Generation in MW
- `Source` - Always "entsoe"
- `Reading Type` - Always "actual"

---

### GET /entsoe/all

Fetch energy generation data for ALL supported countries and date range.

**Query Parameters**:
- `start` (required) - Start date in format YYYYMMDD
- `end` (required) - End date in format YYYYMMDD

**Example Request**:
```bash
curl "http://localhost:6969/entsoe/all?\
start=20240101&\
end=20240102"
```

**Example Response**:
```json
{
  "AT": {
    "file": "/path/to/entsoe-download/AT-entsoe_data.csv",
    "country": "AT"
  },
  "DE": {
    "file": "/path/to/entsoe-download/DE-entsoe_data.csv",
    "country": "DE"
  },
  "FR": {
    "file": "/path/to/entsoe-download/FR-entsoe_data.csv",
    "country": "FR"
  }
}
```

**Notes**:
- Queries 33 European countries sequentially
- May take several minutes to complete
- Each country saved to separate CSV file

---

### GET /entsoe/convert_files

Converts raw ENTSOE CSV files to standardized format with daily aggregation.

**No Parameters Required**

**Example Request**:
```bash
curl http://localhost:6969/entsoe/convert_files
```

**Example Response**:
```json
{
  "files_converted": 15,
  "output_directory": "/path/to/entsoe-revised-output/",
  "converted_files": [
    "converted-AT-entsoe_data.csv",
    "converted-DE-entsoe_data.csv"
  ]
}
```

**Conversion Process**:
1. Read from `ENTSOE_CSV_PATH`
2. Aggregate hourly data to daily values
3. Multiply by 24 to get daily total MWh
4. Add prefix "converted-" to filename
5. Save to `ENTSOE_OUTPUT_DIR`

---

### GET /entsoe/archive_converted_files

Moves converted files to archive directory.

**No Parameters Required**

**Example Request**:
```bash
curl http://localhost:6969/entsoe/archive_converted_files
```

**Example Response**:
```json
{
  "files_archived": 15,
  "archive_directory": "/path/to/entsoe-revised-archive/"
}
```

**Note**: Files are moved (not copied) from output to archive directory.

---

## Encord APIs

### GET /encord

Lists all data rows (images) in an Encord dataset.

**Query Parameters**:
- `bridge` (optional) - Bridge name: "forward", "legacy", "catchups", or "test" (default: "forward")

**Example Request**:
```bash
curl "http://localhost:6969/encord?bridge=forward"
```

**Example Response**:
```json
[
  {
    "data_hash": "d13cf1b6-a794-4428-b11e-d6555264a645",
    "data_title": "Andong-power-station-12-01-2024.jpg",
    "file_size": 125678
  },
  {
    "data_hash": "e24df2c7-b805-5539-c22f-e7666375c756",
    "data_title": "Ansan-power-station-12-01-2024.jpg",
    "file_size": 132456
  }
]
```

**Response Fields**:
- `data_hash` - Unique identifier for the image in Encord
- `data_title` - Original filename
- `file_size` - Size in bytes

---

### GET /encord/upload_image

Uploads a single image file to Encord dataset.

**Query Parameters**:
- `filename` (required) - Full path to image file
- `bridge` (optional) - Bridge name (default: "test")

**Example Request**:
```bash
curl "http://localhost:6969/encord/upload_image?\
filename=/path/to/images/Andong-power-station-12-01-2024.jpg"
```

**Example Response**:
```json
{
  "data_hash": "d13cf1b6-a794-4428-b11e-d6555264a645",
  "file_link": "cord-images-prod/19emyUB3TaSkhuacBApD0LpwapD3/d13cf1b6-a794-4428-b11e-d6555264a645",
  "title": "Andong-power-station-12-01-2024.jpg"
}
```

**Notes**:
- File must exist and be > 25KB
- File moved to `/uploaded/` on success
- File moved to `/unusable/` if too small
- Returns null if upload fails

---

### GET /encord/upload_all_images

Uploads all images from the images directory to Encord dataset.

**Query Parameters**:
- `bridge` (optional) - Bridge name (default: "test")

**Example Request**:
```bash
curl "http://localhost:6969/encord/upload_all_images?bridge=forward"
```

**Example Response**:
```json
[
  {
    "data_hash": "d13cf1b6-a794-4428-b11e-d6555264a645",
    "file_link": "cord-images-prod/.../d13cf1b6-a794-4428-b11e-d6555264a645",
    "title": "Andong-power-station-12-01-2024.jpg"
  },
  {
    "data_hash": "e24df2c7-b805-5539-c22f-e7666375c756",
    "file_link": "cord-images-prod/.../e24df2c7-b805-5539-c22f-e7666375c756",
    "title": "Ansan-power-station-12-01-2024.jpg"
  }
]
```

**Process**:
1. Scans `IMAGES_PATH` directory
2. Validates each image (> 25KB)
3. Uploads to Encord dataset
4. Moves successful uploads to `/uploaded/`
5. Moves failed/invalid to `/unusable/`

---

### GET /encord/labels

Retrieves labels (classifications) for a specific project and date.

**Query Parameters**:
- `project_hash` (optional) - Encord project ID (defaults to legacy bridge)
- `project_name_like` (optional) - Search by project name
- `for_date` (optional) - Date filter in format YYYY-MM-DD (defaults to yesterday)

**Example Request**:
```bash
curl "http://localhost:6969/encord/labels?\
project_name_like=Catchup&\
for_date=2024-01-09"
```

**Example Response**:
```json
[
  {
    "data_hash": "d13cf1b6-a794-4428-b11e-d6555264a645",
    "data_title": "Andong-power-station-09-01-2024.jpg",
    "label_hash": "f35eg3d8-c916-6650-d33g-f8777486d867",
    "classification": {
      "answer_value": "Active",
      "last_edited_at": "2024-01-09T14:30:00Z"
    }
  }
]
```

---

### GET /encord/labels/all

Exports all labels from a project, starting from a specific date.

**Query Parameters**:
- `bridge` (optional) - Bridge name: "forward", "legacy", "catchups" (default: "forward")
- `from_date` (optional) - Start date YYYY-MM-DD (default: "2022-10-18")
- `media_type` (optional) - "csv" or "json" (default: "csv")
- `format` (optional) - "simple" or "full" (default: "simple")

**Example Request**:
```bash
curl "http://localhost:6969/encord/labels/all?\
bridge=forward&\
from_date=2024-01-01&\
media_type=csv&\
format=simple"
```

**Example Response (CSV)**:
```json
{
  "filename": "/path/to/encord-download/encord_labels_forward_uuid.csv"
}
```

**CSV File Format (Simple)**:
```csv
data_hash,data_title,answer,file_link,label_hash,last_edited_at
d13cf1b6-...,Andong-power-station-09-01-2024.jpg,Active,cord-images-prod/...,f35eg3d8-...,2024-01-09T14:30:00Z
```

**Example Response (JSON)**:
```json
[
  {
    "data_hash": "d13cf1b6-a794-4428-b11e-d6555264a645",
    "data_title": "Andong-power-station-09-01-2024.jpg",
    "answer": "Active",
    "file_link": "cord-images-prod/.../d13cf1b6-a794-4428-b11e-d6555264a645",
    "label_hash": "f35eg3d8-c916-6650-d33g-f8777486d867",
    "last_edited_at": "2024-01-09T14:30:00Z"
  }
]
```

**Format Options**:
- `simple` - Flattened structure with key fields only
- `full` - Complete label object with all metadata

---

### GET /encord/sync_station_image_yesterday

Combined operation: Downloads satellite image AND uploads to Encord in one call.

**Query Parameters**:
- `station` (required) - Station name
- `l1, l2, l3, l4` (required) - Bounding box coordinates
- `collectionID` (required) - Sentinel Hub collection ID
- `bridge` (optional) - Encord bridge to upload to (default: "test")

**Example Request**:
```bash
curl "http://localhost:6969/encord/sync_station_image_yesterday?\
station=Andong%20power%20station&\
l1=128.545254&\
l2=36.599082&\
l3=128.537342&\
l4=36.59273&\
collectionID=34170c46-7edb-491d-8a5e-69e7bfd4a741"
```

**Example Response**:
```json
{
  "download": {
    "station": "Andong power station",
    "date": "2024-01-15",
    "image_filename": "/path/to/images/Andong-power-station-15-01-2024.jpg",
    "file_size": 125678,
    "status": "success"
  },
  "upload": {
    "data_hash": "d13cf1b6-a794-4428-b11e-d6555264a645",
    "file_link": "cord-images-prod/.../d13cf1b6-a794-4428-b11e-d6555264a645",
    "title": "Andong-power-station-15-01-2024.jpg"
  }
}
```

**Process Flow**:
```
1. Download image from Sentinel Hub
2. Save to local disk
3. Validate file size
4. Upload to Encord dataset
5. Move to /uploaded/ folder
6. Return both download and upload results
```

---

## Error Responses

### 400 Bad Request

Missing or invalid parameters.

```json
{
  "error": "Missing required parameter: country_code"
}
```

### 401 Unauthorized

Authentication failed (invalid credentials).

```json
{
  "error": "Invalid Sentinel Hub credentials"
}
```

### 404 Not Found

Resource not found.

```json
{
  "error": "Station not found: InvalidStation"
}
```

### 500 Internal Server Error

Server-side error.

```json
{
  "error": "Failed to download image",
  "details": "Connection timeout to Sentinel Hub"
}
```

---

## Rate Limiting

The application doesn't enforce rate limits, but external APIs have their own limits:

**Sentinel Hub**: 
- 10 requests/second
- Processing units consumed per request

**ENTSOE**: 
- 400 requests/minute
- Consider this when querying all countries

**Encord**: 
- No published rate limits
- Use reasonable request patterns

---

## Testing with curl

### Health Check
```bash
curl http://localhost:6969/api
```

### List Stations
```bash
curl http://localhost:6969/sentinel/stations
```

### Get Energy Data
```bash
curl "http://localhost:6969/entsoe?country_code=AT&start=20240101&end=20240102"
```

### List Encord Images
```bash
curl "http://localhost:6969/encord?bridge=forward"
```

---

## Testing with Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:6969"

# Health check
response = requests.get(f"{BASE_URL}/api")
print(response.json())

# Get stations
response = requests.get(f"{BASE_URL}/sentinel/stations")
stations = response.json()
print(f"Found {len(stations)} stations")

# Get energy data
params = {
    "country_code": "AT",
    "start": "20240101",
    "end": "20240102"
}
response = requests.get(f"{BASE_URL}/entsoe", params=params)
result = response.json()
print(f"Data saved to: {result['file']}")

# Batch download (async)
params = {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
}
response = requests.post(
    f"{BASE_URL}/sentinel/download_all_station_images",
    json={},
    params=params
)
print(response.json())  # {"message": "Request accepted"}
```

---

## Testing with JavaScript

```javascript
const BASE_URL = 'http://localhost:6969';

// Health check
fetch(`${BASE_URL}/api`)
  .then(res => res.json())
  .then(data => console.log(data));

// Get stations
fetch(`${BASE_URL}/sentinel/stations`)
  .then(res => res.json())
  .then(stations => console.log(`Found ${stations.length} stations`));

// Get energy data
const params = new URLSearchParams({
  country_code: 'AT',
  start: '20240101',
  end: '20240102'
});

fetch(`${BASE_URL}/entsoe?${params}`)
  .then(res => res.json())
  .then(result => console.log(`Data saved to: ${result.file}`));

// Batch download
fetch(`${BASE_URL}/sentinel/download_all_station_images?start_date=2024-01-01&end_date=2024-01-31`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({})
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Next Steps

- Review [FUNCTIONALITY.md](./FUNCTIONALITY.md) to understand what each endpoint does internally
- Check [INTEGRATION.md](./INTEGRATION.md) to learn about external service requirements
- See [MAINTENANCE.md](./MAINTENANCE.md) for adding new endpoints
