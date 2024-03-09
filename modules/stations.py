import csv

def loadStationsFromCsv(csv_file):
    """
    Load stations from a CSV file into a data type.

    Args:
        csv_file (str): Path to the CSV file.

    Returns:
        list: List of dictionaries representing each station.

    Raises:
        FileNotFoundError: If the CSV file is not found.
    """
    stations = []
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file, delimiter=',')
            for row in reader:
                station = {
                    'station': row['Name'].strip(),
                    'l1': float(row['L1']),
                    'l2': float(row['L2']),
                    'l3': float(row['L3']),
                    'l4': float(row['L4']),
                    'collectionID': row['Collection ID']
                }
                stations.append(station)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file '{csv_file}' not found.")
    
    return stations
