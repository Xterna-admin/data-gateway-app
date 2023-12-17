import tempfile
from app import app
from dotenv import load_dotenv
import os

load_dotenv()

# create a function to return the private key path
def get_private_key():
    return os.getenv('PRIVATE_KEY_PATH') or exit("Please provide a private key path in .env file.")

# create a function to return the private key file from the path
def get_private_key_file():
    with open(get_private_key(), 'r') as f:
        return f.read()

def get_entsoe_api_key():
    return os.getenv('ENTSOE_API_KEY') or exit("Please provide an Entsoe API Key in .env file.")

def get_sentinel_clientId():
    return os.getenv('SENTINEL_CLIENT_ID') or exit("Please provide a Sentinel Client ID in .env file.")

def get_sentinel_clientSecret():
    return os.getenv('SENTINEL_CLIENT_SECRET') or exit("Please provide a Sentinel Client Secret in .env file.")

def get_stations_csv_path():
    return os.getenv('STATIONS_CSV_PATH') 

def get_test_dataset_id():
    return os.getenv('ENCORD_TEST_DATASET') or exit("Please provide a Test Dataset ID in .env file.")

def get_images_path():
    # return getenv or system temp path
    return os.getenv('IMAGES_PATH') or tempfile.gettempdir()