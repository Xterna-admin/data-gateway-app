from app import app
from entsoe import EntsoePandasClient
import pandas as pd
import os
from datetime import datetime
from modules.config import get_entsoe_api_key, get_entsoe_csv_path
import json
import csv
import pytz
from pytz import country_timezones, timezone

def get_entsoe_data_all_countries(start: str, end: str):
    country_list = ['AT','BA','BE','BG','CH','CZ','DE','DK','EE','ES','FI','FR','GR','HR','HU','IE','IT','LT','LU','LV','ME','MK','NL','NO','PL','PT','RO','RS','SE','SK','XK']
    # country_list = ['BA','BG','CZ','DE','EE','GR','HR','HU','IE','LU','ME','MK','PL','RO','RS','SK']
    all_data = {}
    for country in country_list:
        print(f"Getting data for {country}")
        all_data[country] = get_entsoe_data(country, start, end)
    return all_data

def get_entsoe_data(country_code: str, start: str, end: str):
    client = EntsoePandasClient(api_key=get_entsoe_api_key())
    if country_code == 'XK':
        tz_str = 'Europe/Rome'
    else:    
        tz_str = country_timezones(country_code)[0]
    start_pd = pd.Timestamp(start, tz=tz_str)
    end_pd = pd.Timestamp(end, tz=tz_str)
    
    ts = client.query_generation(country_code, start=start_pd,end=end_pd, psr_type=None)
    return transform_to_csv(json.loads(ts.to_json()), country_code)

def is_string_in_array(target_string, string_array):
    for string in string_array:
        if string in target_string:
            return True
    return False

def are_all_strings_in_array(target_string, string_array):
    if string_array[0] == target_string:
        return True
    return all(string in target_string for string in string_array)

def transform_to_csv(json_data, country_code):
    headers = ['Reading date', 'Country', 'Brown Coal', 'Gas', 'Hard Coal', 'Nuclear', 'Source', 'Reading Type']
    rows = {}
    if country_code == 'XK':
        tz = 'Europe/Rome'
    else:    
        tz = country_timezones(country_code)[0]
    for key, value in json_data.items():
        if is_string_in_array(key, ['Fossil Brown coal', 'Fossil Gas','Fossil Hard coal', 'Nuclear']):
            for timestamp_str, val in value.items():
                timestamp = int(timestamp_str)
                utc_time = datetime.utcfromtimestamp(timestamp / 1000)
                # utc_time_with_timezone = utc_time.astimezone(timezone(tz))
                utc_time_with_timezone = pytz.utc.localize(utc_time, is_dst=None).astimezone(timezone(tz))
                date_str = utc_time_with_timezone.strftime('%Y-%m-%d %H:%M:%S')
                if date_str not in rows:
                    rows[date_str] = {'Reading date': date_str, 'Country': country_code, 'Source': 'entsoe', 'Reading Type': 'actual'}
                if are_all_strings_in_array(key, ['Fossil Brown coal/Lignite','Aggregated']):
                    rows[date_str]['Brown Coal'] = val
                elif are_all_strings_in_array(key, ['Fossil Gas','Aggregated']):
                    rows[date_str]['Gas'] = val
                elif are_all_strings_in_array(key, ['Fossil Hard coal','Aggregated']):
                    rows[date_str]['Hard Coal'] = val
                elif are_all_strings_in_array(key, ['Nuclear','Aggregated']):
                    rows[date_str]['Nuclear'] = val

    file_name = get_entsoe_csv_path() + f'/{country_code}-entsoe_data.csv'
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows.values())

    return {"file":file_name, "country":country_code}

def convert_files_legacy_format(input_dir: str, output_dir: str):
    # Input and output directories
    input_directory = input_dir
    output_directory = output_dir

    # Process all CSV files in the input directory
    for file in os.listdir(input_directory):
        if file.endswith(".csv"):
            # Read the CSV file
            print(f"Processing file: {file}")
            df = pd.read_csv(os.path.join(input_directory, file))

            # Assign 'DT' to the first column
            df.columns.values[0] = 'DT'

            # Drop rows with missing 'Reading Datetime' values
            df = df.dropna(subset=['DT'])

            # Convert 'Reading Datetime' to datetime and set it as the index
            df['DT'] = pd.to_datetime(df['DT'], utc=True)
            df.set_index('DT', inplace=True)

            # Group by date and aggregate the values, preserving other columns
            df_grouped = df.groupby([df.index.date, 'Country']).agg({
                'Fossil Brown coal/Lignite': 'mean',
                'Fossil Gas': 'mean',
                'Fossil Hard coal': 'mean',
                'Nuclear': 'mean'
            }).round(0).multiply(24).reset_index()

            # Add new static columns for 'Source' and 'Reading Type'
            df_grouped['Source'] = 'entsoe'
            df_grouped['Reading Type'] = 'actual'

            # Rename columns
            df_grouped.rename(columns={'Fossil Brown coal/Lignite': 'Brown Coal'}, inplace=True)
            df_grouped.rename(columns={'Fossil Gas': 'Gas'}, inplace=True)
            df_grouped.rename(columns={'Fossil Hard coal': 'Hard Coal'}, inplace=True)
            df_grouped.rename(columns={'level_0': 'Reading date'}, inplace=True)

            # Save to a new CSV file with the 'converted-' prefix
            output_file = os.path.join(output_directory, 'converted-' + file)
            df_grouped.to_csv(output_file, index=False)

def convert_files_new_format(input_dir: str, output_dir: str):
    # Input and output directories
    input_directory = input_dir
    output_directory = output_dir
    processed_files = []

    # Process all CSV files in the input directory
    for file in os.listdir(input_directory):
        if file.endswith(".csv"):
            # Read the CSV file
            print(f"Processing file: {file}")
            df = pd.read_csv(os.path.join(input_directory, file))

            df['Reading date'] = pd.to_datetime(df['Reading date'], utc=True)
            df.set_index('Reading date', inplace=True)

            # Group by date and aggregate the values, preserving other columns
            df_grouped = df.groupby([df.index.date, 'Country']).agg({
                'Brown Coal': 'mean',
                'Gas': 'mean',
                'Hard Coal': 'mean',
                'Nuclear': 'mean'
            }).multiply(24).round(0).reset_index()

            # Add new static columns for 'Source' and 'Reading Type'
            df_grouped['Source'] = 'entsoe'
            df_grouped['Reading Type'] = 'actual'
            df_grouped.rename(columns={'level_0': 'Reading date'}, inplace=True)

            # Save to a new CSV file with the 'converted-' prefix
            output_file = os.path.join(output_directory, 'converted-' + file)
            df_grouped.to_csv(output_file, index=False)
            processed_files.append({"file": output_file})
            # move file to archive folder
            os.rename(os.path.join(input_directory, file), os.path.join(input_directory + '-archive', file))

    print(f"Processed {len(os.listdir(input_directory))} files.")
    return processed_files

def archive_converted_files(input_dir: str, output_dir: str):
    # Input and output directories
    input_directory = input_dir
    output_directory = output_dir
    archived_files = []

    # Process all CSV files in the input directory
    for file in os.listdir(input_directory):
        if file.startswith("converted-"):
            # Move the file to the output directory
            print(f"Archiving file: {file}")
            os.rename(os.path.join(input_directory, file), os.path.join(output_directory, file))
            archived_files.append({"file": file})

    print(f"Processed {len(os.listdir(input_directory))} files.")
    return archived_files


    print(f"Archived {len(os.listdir(output_directory))} files.")
