from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
import json

from flask import jsonify

from app import app
from pathlib import Path
from modules.config import get_all_bridges_datahashes, get_images_path, get_sentinel_clientId, get_stations_csv_path
from modules.config import get_sentinel_clientSecret

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from sentinelhub import SentinelHubDownloadClient
from sentinelhub import DataCollection
from sentinelhub import SHConfig
import requests

from modules.stations import loadStationsFromCsv
from datetime import datetime, timedelta

token = [None]

def get_oauth_token():

    if token[0]:
        return token[0]['access_token']
    # Your client credentials
    client_id = get_sentinel_clientId()
    client_secret = get_sentinel_clientSecret()

    # Create a session
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)

    # Get token for the session
    token[0] = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                            client_secret=client_secret, include_client_id=True)

    return token[0]['access_token']

def get_sh_config():

    # Your client credentials
    client_id = get_sentinel_clientId()
    client_secret = get_sentinel_clientSecret()

    config = SHConfig(sh_client_id=client_id, sh_client_secret=client_secret)

    return config

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

    return download_image_for_station(station, in_date, dy)

def download_image_for_station(station: Dict, in_date: str, dy: str = None):
    # Replace spaces with hyphens in the station name
    station_name = station['station'].replace(' ', '-')
    image_filename = f"{station_name}-{in_date}.jpg"

    response = do_download_image_for_station(station, dy, image_filename)
    print(f"Downloaded image for station {station_name} on {in_date} with response {response}")

    return response

def download_images_for_date(date, stations, existing_images):
    date_images = []
    in_date = date.strftime("%d-%m-%Y")
    dy = date.strftime("%Y-%m-%d")
    for station in stations:
        if not station['collectionID']:
            continue
        station_name = station['station'].replace(' ', '-')
        image_filename = f"{station_name}-{in_date}.jpg"
        if check_for_existing_encord_image(existing_images, image_filename):
            print(f"Skipping download for {station_name} on {in_date} as image exists")
            continue
        # check if the image exists in IMAGES_PATH and skip if it does
        if Path(get_images_path() + image_filename).exists():
            # print(f"Skipping download for {station_name} on {in_date} as image exists on disk")
            continue
        response = do_download_image_for_station(station, dy, image_filename)
        date_images.append(response)
    return date_images

def download_all_sat_images_between_dates(data: str, args: Dict):
    images = []
    stations = get_stations_list()
    end_date = datetime.strptime(args['end_date'], "%Y-%m-%d") if args.get('end_date') else datetime.now()
    existing_images = load_existing_encord_images()

    # Create a thread pool and execute
    with ThreadPoolExecutor(max_workers=7) as executor:
        # Submit tasks for each date in parallel
        future_tasks = {executor.submit(download_images_for_date, date, stations, existing_images): date for date in get_dates_between(args['start_date'], end_date)}

        # Gather results
        for future in as_completed(future_tasks):
            images.extend(future.result())

    # write images to a new file. use get_all_bridges_datahashes() to get the file path and replace the ending of .json to be -output.json
    with open(get_all_bridges_datahashes().replace('.json', '-output.json'), 'w') as file:
        json.dump(images, file)

# Function to generate dates between start and end dates
def get_dates_between(start_date, end_date):
    # parse start_date into datetime object
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    delta = end_date - start_date
    for i in range(delta.days + 1):
        yield start_date + timedelta(days=i)

def get_available_data_collections():
    return DataCollection.get_available_collections()

def log_data_collections(data_collections: List[Dict]):
    for data_collection in data_collections:
        app.logger.info(data_collection)

def get_stations_list():
    stations = loadStationsFromCsv(get_stations_csv_path())
    return stations

def do_download_image_for_station(station: Dict, date: str, image_filename: str):
    token = get_oauth_token()
    print(f"Downloading on {date} for station {station}")
    bearer = "Bearer {}".format(token)
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
                "from": date + "T00:00:00.00Z",
                "to": date + "T23:59:59.00Z"
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

    response:requests.Response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Error downloading image for station {station} on {date} with response code {response.status_code} and content {response.content}")
        return {'image_filename': image_filename, 'size': -1, 'status': 'error'}
    # save jpeg image bytes to response to file
    with open(get_images_path() + image_filename, 'wb') as f:
        f.write(response.content)

    # get the file size
    file_size = Path(get_images_path() + image_filename).stat().st_size
    return {'image_filename': image_filename, 'size': file_size, 'status': 'success'}

def load_json_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("JSON data is not an array")
            return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print("An error occurred:", e)

def extract_filename_part(filename):
    parts = filename.split('-')
    extracted_part = '-'.join(parts[2:])
    return extracted_part

def check_key_existence(dictionary, key):
    return key in dictionary

def load_existing_encord_images():
    try:
        # Parse JSON data
        data = load_json_from_file(get_all_bridges_datahashes())
        print(f"Data is loaded")
        # Check if data is a list
        if not isinstance(data, list):
            raise ValueError("JSON data is not an array")
        
        # Store the data in a list of dictionaries
        key_value_structure = {}
        for item in data:
            key_value_structure[extract_filename_part(item['data_title'])] = item['data_hash']

        return key_value_structure
    
    except Exception as e:
        print("An error occurred:", e)

def check_for_existing_encord_image(dictionary, substring):
    try:
        for key in dictionary.keys():
            if substring in key:
                return True
        return False
    
    except Exception as e:
        print("An error occurred:", e)

def delete_images_with_date_format_check():
    date_images = []
    end_date = datetime.strptime("2024-01-31", "%Y-%m-%d")
    stations = get_stations_list()
    existing_images = load_existing_encord_images()

    for station in stations:
        station_name = station['station'].replace(' ', '-')
        for date in get_dates_between('2022-10-19', end_date):
            in_date_format1 = date.strftime("%d-%m-%Y")
            in_date_format2 = date.strftime("%Y-%m-%d")
            image_filename1 = f"{station_name}-{in_date_format1}.jpg"
            image_filename2 = f"{station_name}-{in_date_format2}.jpg"
            image_filename3 = f"{station_name}-{in_date_format1}.jpeg"
            image_filename4 = f"{station_name}-{in_date_format2}.jpeg"
            if not Path(get_images_path() + image_filename1).exists():
                continue
            else:
                if check_key_existence(existing_images, image_filename1):
                    print(f"Would delete for {image_filename1} as image already exists")
                    date_images.append(image_filename1)
                    continue
                if check_key_existence(existing_images, image_filename2):
                    print(f"Would delete for {image_filename2} as image already exists")
                    date_images.append(image_filename1)
                    continue
                if check_key_existence(existing_images, image_filename3):
                    print(f"Would delete for {image_filename3} as image already exists")
                    date_images.append(image_filename1)
                    continue
                if check_key_existence(existing_images, image_filename4):
                    print(f"Would delete for {image_filename4} as image already exists")
                    date_images.append(image_filename1)
                    continue
    # for each date_images entry move the file into a folder called deleted
    for image in date_images:
        Path(get_images_path() + image).rename(get_images_path() + "deleted/" + image)
    return date_images
