from app import app
from entsoe import EntsoePandasClient
import pandas as pd
import os

from modules.config import get_entsoe_api_key

def get_entsoe_data(country_code: str, start: str, end: str):
    client = EntsoePandasClient(api_key=get_entsoe_api_key())
    start_pd = pd.Timestamp(start, tz='Europe/Brussels')
    end_pd = pd.Timestamp(end, tz='Europe/Brussels')
    
    ts = client.query_generation(country_code, start=start_pd,end=end_pd, psr_type=None)
    return ts.to_json()

def convert_files(input_dir: str, output_dir: str):
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
                'Fossil Brown coal/Lignite': 'sum',
                'Fossil Gas': 'sum',
                'Fossil Hard coal': 'sum',
                'Nuclear': 'sum'
            }).round(0).reset_index()

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

            # return the number of files processed
    return f"Processed {len(os.listdir(input_directory))} files."
