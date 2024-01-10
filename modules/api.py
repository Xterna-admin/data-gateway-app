# Import Libraries 
from app import app
from flask import jsonify
from flask import request

from modules.encordSync import list_data_rows, upload_all_images, pull_labels
from modules.sentinel import get_data_collections, get_sat_images_for_stations, get_stations_list
from modules.entsoe import get_entsoe_data

# Define route "/api".
@app.route('/api')
def api():
  # return in JSON format. (For API)
  return jsonify({"message":"Hello from Flask!"})

# Example: http://localhost:6969/entsoe?country_code=AT&start=20230101&end=20230102 
@app.route('/entsoe')
def entsoe():
  country_code = request.args.get('country_code')
  start = request.args.get('start')
  end = request.args.get('end')
 
  return jsonify(get_entsoe_data(country_code, start, end))

@app.route('/encord')
def encord():
  # return in JSON format. (For API)
  rows = list_data_rows()
  json_rows = []
  for i, row in enumerate(rows):
    # Create a dictionary for the row
    serialized_row = {
        'data_hash': row.get('data_hash', ''),
        'data_title': row.get('data_title', ''),
        'file_size': row.get('file_size', 0)
        # Add other properties as needed
    }

    # Write the serialized row to the file
    json_rows.append(serialized_row)

  return jsonify(json_rows)

@app.route('/encord/labels')
def encord_labels():
  # return in JSON format. (For API)
  return jsonify(pull_labels())

@app.route('/encord/upload_all_images')
def encord_upload_all_images():
  upload_all_images()
  return jsonify({"message":"Uloaded all images to Encord!"})

@app.route('/sentinel')
def sentinel():
  collections = get_data_collections()
  return jsonify(collections)

@app.route('/sentinel/stations')
def sentinel_stations():
  stations = get_stations_list()
  app.logger.info(stations)
  return jsonify(stations)

@app.route('/sentinel/stations_images')
def sentinel_stations_images():
  stations = get_stations_list()
  return jsonify(get_sat_images_for_stations(stations))
