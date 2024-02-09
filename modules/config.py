import tempfile
from app import app
from dotenv import load_dotenv
import os

load_dotenv()

# create a function to return the private key path
def get_private_key():
    if (os.getenv('PRIVATE_KEY_PATH') == None):
        print("Please provide a private key path in .env file.")
    return os.getenv('PRIVATE_KEY_PATH', None)

# create a function to return the private key file from the path
def get_private_key_file():
    with open(get_private_key(), 'r') as f:
        return f.read()

def get_entsoe_api_key():
    if (os.getenv('ENTSOE_API_KEY') == None):
        print("Please provide an Entsoe API Key in .env file.")
    return os.getenv('ENTSOE_API_KEY',None)

def get_sentinel_clientId():
    if (os.getenv('SENTINEL_CLIENT_ID') == None):
        print("Please provide a Sentinel Client ID in .env file.")
    return os.getenv('SENTINEL_CLIENT_ID', None) 

def get_sentinel_clientSecret():
    if (os.getenv('SENTINEL_CLIENT_SECRET') == None):
        print("Please provide a Sentinel Client Secret in .env file.")
    return os.getenv('SENTINEL_CLIENT_SECRET', None)

def get_stations_csv_path():
    if (os.getenv('STATIONS_CSV_PATH') == None):
        print("Please provide a Stations CSV Path in .env file.")
    return os.getenv('STATIONS_CSV_PATH', None) 

def get_test_dataset_id():
    if (os.getenv('ENCORD_TEST_DATASET') == None):
        print("Please provide a Test Dataset ID in .env file.")
    return os.getenv('ENCORD_TEST_DATASET', None)

def get_images_path():
    if (os.getenv('IMAGES_PATH') == None):
        print(f"Using tmpdir {tempfile.gettempdir()} for images. Please provide a Images Path in .env file.")
    return os.getenv('IMAGES_PATH', tempfile.gettempdir())

def get_encord_forward_bridge():
    if (os.getenv('ENCORD_FORWARD_BRIDGE_PROJECT') == None):
        print("Please provide a Encord Forward Bridge in .env file.")
    return os.getenv('ENCORD_FORWARD_BRIDGE_PROJECT', None)

def get_entsoe_input_dir():
    if (os.getenv('ENTSOE_INPUT_DIR') == None):
        print("Please provide a Entsoe Input Directory in .env file.")
    return os.getenv('ENTSOE_INPUT_DIR', None)
def get_entsoe_output_dir():
    if (os.getenv('ENTSOE_OUTPUT_DIR') == None):
        print("Please provide a Entsoe Output Directory in .env file.")
    return os.getenv('ENTSOE_OUTPUT_DIR', None)