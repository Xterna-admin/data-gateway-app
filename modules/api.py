# Import Libraries 
from app import app
from flask import jsonify
from flask import request
from datetime import datetime, timedelta
import threading

from modules.encordSync import list_data_rows, upload_all_images, pull_labels, upload_image_file
from modules.sentinel import delete_images_with_date_format_check, download_all_sat_images_between_dates, download_yesterday_image_for_station, get_sat_images_for_stations, get_stations_list
from modules.entsoe import archive_converted_files, convert_files_legacy_format, convert_files_new_format, get_entsoe_data, get_entsoe_data_all_countries
from modules.config import get_encord_legacy_bridge_project, get_entsoe_archive_dir, get_entsoe_csv_path, get_entsoe_output_dir

@app.before_request
def handle_every_request():
  app.logger.info(f'Handling request: {request.url}')
  print(f'Args: {request.args}')

# Define route "/api".
@app.route('/api')
def api():
  # return in JSON format. (For API)
  return jsonify({"message":"Hello from Flask!"})

# Example: http://localhost:6969/entsoe/all?start=20230101&end=20230102 
@app.route('/entsoe/all')
def entsoe_all():
  start = request.args.get('start')
  end = request.args.get('end')
 
  return get_entsoe_data_all_countries(start, end)

# Example: http://localhost:6969/entsoe?country_code=AT&start=20230101&end=20230102 
@app.route('/entsoe')
def entsoe():
  country_code = request.args.get('country_code')
  start = request.args.get('start')
  end = request.args.get('end')
 
  return get_entsoe_data(country_code, start, end)

@app.route('/entsoe/convert_files')
def entsoe_convert_files():
  input_dir = get_entsoe_csv_path()
  output_dir = get_entsoe_output_dir()
 
  return convert_files_new_format(input_dir, output_dir)

@app.route('/entsoe/archive_converted_files')
def entsoe_archive_files():
  input_dir = get_entsoe_output_dir()
  output_dir = get_entsoe_archive_dir()
 
  return archive_converted_files(input_dir, output_dir)

# http://localhost:6969/encord?bridge=legacy
@app.route('/encord')
def encord():
  # return in JSON format. (For API)
  rows = list_data_rows(request.args.get('bridge', 'forward'))
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

# http://localhost:6969/encord/labels?for_date=2024-01-09
@app.route('/encord/labels')
def encord_labels():
  project_hash = request.args.get('project_hash', get_encord_legacy_bridge_project())
  project_name_like = request.args.get('project_name_like')
  yesterday = datetime.now() - timedelta(days=1)
  dy = yesterday.strftime("%Y-%m-%d")
  for_date = request.args.get('for_date', dy)
  print(for_date)

  return jsonify(pull_labels(project_hash=project_hash, project_name_like=project_name_like, for_date=for_date))

@app.route('/encord/upload_all_images')
def encord_upload_all_images():
  print(request.args)
  response = upload_all_images(request.args.get('bridge', 'test'))
  return jsonify(response)

# http://localhost:6969/encord/upload_image?filename=Andong-power-station-12-01-2024.jpg
# {"data_hash":"d13cf1b6-a794-4428-b11e-d6555264a645","file_link":"cord-images-prod/19emyUB3TaSkhuacBApD0LpwapD3/d13cf1b6-a794-4428-b11e-d6555264a645","title":"Andong-power-station-12-01-2024.jpg"}
@app.route('/encord/upload_image')
def encord_upload_image():
  print(request.args)
  filename = request.args.get('filename')
  return jsonify(upload_image_file(filename))

# http://localhost:6969/sentinel/stations
# Returns a list of all stations configured in the stations.csv file
@app.route('/sentinel/stations')
def sentinel_stations():
  stations = get_stations_list()
  app.logger.info(stations)
  return jsonify(stations)

# http://localhost:6969/sentinel/stations_images
# Downloads all of the latest images for each station in the stations.csv file
@app.route('/sentinel/stations_images')
def sentinel_stations_images():
  stations = get_stations_list()
  return jsonify(get_sat_images_for_stations(stations))

# http://localhost:6969/sentinel/download_station_image_yesterday?station=Andong%20power%20station&l1=128.545254&l2=36.599082&l3=128.537342&l4=36.59273&collectionID=34170c46-7edb-491d-8a5e-69e7bfd4a741
#   my_dict = {
  #     'collectionID': request.args.get('collectionID', ''),
  #     'l1': request.args.get('l1', ''),
  #     'l2': request.args.get('l2', ''),
  #     'l3': request.args.get('l3', ''),
  #     'l4': request.args.get('l4', ''),
  #     'station': request.args.get('station', '')
  # }
@app.route('/sentinel/download_station_image_yesterday')
def download_station_image_yesterday():
  return jsonify(download_yesterday_image_for_station(request.args))

# http://localhost:6969/encord/sync_station_image_yesterday?station=Andong%20power%20station&l1=128.545254&l2=36.599082&l3=128.537342&l4=36.59273&collectionID=34170c46-7edb-491d-8a5e-69e7bfd4a741
@app.route('/encord/sync_station_image_yesterday')
def encord_sync_station_image_yesterday():
  image_download = download_yesterday_image_for_station(request.args)
  print(image_download)
  image_upload = upload_image_file(image_download.get('image_filename'))
  return jsonify({"download": image_download, "upload": image_upload})

# # http://localhost:6969/encord/sync_station_missing_images?bridge=forward&start_date=2022-10-18&end_date=2022-10-19
# @app.route('/encord/sync_station_missing_images')
# def encord_sync_station_missing_images():
#   return jsonify(sync_station_images(request.args))

# # http://localhost:6969/sentinel/download_station_images?station=Ansan%20power%20station&start_date=2022-10-18
# @app.route('/sentinel/download_station_images')
# def download_station_images():
#   return jsonify(download_station_images_from_date(request.args))

# curl -X POST \
#  -H "Content-Type: application/json" \
#  -d '{}' \
#  "http://localhost:6969//sentinel/download_all_station_images?start_date=2022-10-19&end_date=2022-10-20"
@app.route('/sentinel/download_all_station_images', methods=['POST'])
def download_all_station_images():
  data = request.json
  args = request.args.to_dict()
  # Start a new thread to process the request
  threading.Thread(target=download_all_sat_images_between_dates, args=(data, args)).start()
  return jsonify({'message': 'Request accepted'}), 201

@app.route('/sentinel/delete_existing_images')
def delete_existing_images():
  return jsonify(delete_images_with_date_format_check())

