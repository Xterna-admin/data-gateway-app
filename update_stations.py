import csv

# Function to escape apostrophes in station name
def escape_apostrophes(station_name):
    return station_name.replace("'", "''")

# Function to generate SQL update statement
def generate_update_sql(station_name, weather_region):
    escaped_station_name = escape_apostrophes(station_name)
    return f"""UPDATE "Station" SET "weatherRegion" = '{weather_region}' WHERE "name" = '{escaped_station_name}');\n"""

# Open the CSV file for reading and output file for writing
with open('your_file.csv', 'r', newline='', encoding='utf-8') as csvfile, \
        open('output.sql', 'w', encoding='utf-8') as output_file:
    reader = csv.DictReader(csvfile)
    # Iterate through each row in the CSV
    for row in reader:
        station_name = row['Name']
        weather_region = row['Weather region']
        # Generate SQL update statement for the current row
        sql_statement = generate_update_sql(station_name, weather_region)
        # Write the SQL statement to the output file
        output_file.write(sql_statement)
