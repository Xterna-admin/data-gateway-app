from typing import Dict, List

from flask import jsonify

from app import app
from pathlib import Path
from modules.config import get_images_path, get_sentinel_clientId, get_stations_csv_path
from modules.config import get_sentinel_clientSecret

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from sentinelhub import SentinelHubDownloadClient
from sentinelhub import DataCollection
from sentinelhub import SHConfig
import requests

from modules.stations import loadStationsFromCsv
from datetime import datetime, timedelta

def get_oauth_token():

    # Your client credentials
    client_id = get_sentinel_clientId()
    client_secret = get_sentinel_clientSecret()

    # Create a session
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)

    # Get token for the session
    token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                            client_secret=client_secret, include_client_id=True)

    return token['access_token']

def get_sh_config():

    # Your client credentials
    client_id = get_sentinel_clientId()
    client_secret = get_sentinel_clientSecret()

    config = SHConfig(sh_client_id=client_id, sh_client_secret=client_secret)

    return config

# create a method that receives an array of stations and returns an array of images

def get_sat_images_for_stations(stations: List[Dict]):
    images = []
    for station in stations:
        # check if station has a collection ID
        if not station['collectionID']:
            continue
        image_filename = download_yesterday_image_for_station(station)
        images.append(image_filename)
    return images

def download_yesterday_image_for_station(station: Dict):
    # Get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    dy = yesterday.strftime("%Y-%m-%d")
    in_date = yesterday.strftime("%d-%m-%Y")

    # Replace spaces with hyphens in the station name
    station_name = station['station'].replace(' ', '-')
    image_filename = f"{station_name}-{in_date}.jpg"

    download_image_for_station(station, dy, image_filename)

    return image_filename

def get_data_collections():
    # create a client that can call the Sentinel Hub API using standard python HTTPS client
    client = SentinelHubDownloadClient(config=get_sh_config())
    return

def get_available_data_collections():
    return DataCollection.get_available_collections()

def log_data_collections(data_collections: List[Dict]):
    for data_collection in data_collections:
        app.logger.info(data_collection)

def get_stations_list():
    stations = loadStationsFromCsv(get_stations_csv_path())
    return stations

def download_image_for_station(station: Dict, date: str, image_filename: str):
    bearer = "Bearer {}".format(get_oauth_token())
    url = "https://services.sentinel-hub.com/api/v1/process"
    headers = {
    "Content-Type": "application/json",
    "Authorization": bearer
    }
    data = {
    "input": {
        "bounds": {
        "bbox": [
            station['l1'],
            station['l2'],
            station['l3'],
            station['l4'],
            ],
        },
        "data": [
        {
            "dataFilter": {
            "timeRange": {
                "from": date + "T00:00:00Z",
                "to": date + "T23:59:59Z"
            }
            },
            "type": f"byoc-{station['collectionID']}"
        }
        ]
    },
    "output": {
        "width": 512,
        "height": 512,
        "responses": [
        {
            "identifier": "default",
            "format": {
            "type": "image/jpeg"
            }
        }
        ]
    },
    "evalscript": "//VERSION=3\n//True Color\n\nfunction setup() {\n  return {\n    input: [\"Red\", \"Green\", \"Blue\", \"dataMask\"],\n    output: { bands: 4 }\n  };\n}\n\nfunction evaluatePixel(sample) {\n  return [sample.Red/3000, \n          sample.Green/3000, \n          sample.Blue/3000,\n          sample.dataMask];\n}"
    }

    response = requests.post(url, headers=headers, json=data)
    # save jpeg image bytes to response to file
    with open(get_images_path() + image_filename, 'wb') as f:
        f.write(response.content)
    return response
