from datetime import datetime, timedelta
import json
from typing import Dict, List
from pathlib import Path

from modules.config import get_dataset_id, get_private_key_file, get_images_path, get_project_hash
from typing import Dict, List
from encord import EncordUserClient
from encord import Dataset, EncordUserClient

def get_dataset(bridge: str) -> Dataset:
    # create a user client with the private key
    print(f"Getting dataset for bridge {bridge}")
    user_client = EncordUserClient.create_with_ssh_private_key(get_private_key_file())
    # get the dataset
    dataset_id = get_dataset_id(bridge=bridge)
    print(f"Dataset ID: {dataset_id}")
    dataset: Dataset = user_client.get_dataset(dataset_id)
    return dataset

# create a function to upload an image to a dataset
def upload_image_file(file_name: str, bridge: str = 'test', dataset: Dataset = None):
    file = file_name
    # check if file exists and is > 25000 bytes in size
    if Path(file).is_file() and Path(file).stat().st_size > 25000:
        result = upload_image(file, bridge, dataset=dataset)
        # check if the result is a dictionary and the file_link is in the dictionary and > 0 in length
        if result and 'file_link' in result and len(result['file_link']) > 0:
            print(f"Uploaded {file} to {result['file_link']}")
            # move the image file to the uploaded folder
            Path(file).rename(Path(get_images_path().replace('images', 'uploaded') + Path(file).name))
            return result
        else:
            print(f"Failed to upload {file} to dataset {dataset}")
            return None
    else:
        print(f"File {file} does not exist or is too small.")
        # move the file if it exists to unusable folder
        Path(file).rename(Path(get_images_path().replace('images', 'unusable') + Path(file).name))
        return None

# create a function to upload an image to a dataset
def upload_image(path: str, bridge: str, dataset: Dataset = None):
    if dataset is None:
        dataset = get_dataset(bridge)
    return dataset.upload_image(path)
#    return print(f"Would upload {path} to {dataset}")

def upload_all_images(bridge: str):
    dataset = get_dataset(bridge)
    results = []
    # for each image in the images folder
    for image in Path(get_images_path()).iterdir():
        # upload the image
        result = upload_image_file(image, bridge=bridge, dataset=dataset)
        print(f"Uploaded {image} result {result}")
        if result:
            results.append(result)
    return results

# create a function to list all the images in a dataset
def list_images(bridge: str):
    dataset = get_dataset(bridge=bridge)
    return dataset.list_images()

# create a function to list all the data rows in a dataset
def list_data_rows(bridge: str):
    dataset = get_dataset(bridge=bridge)
    return dataset.list_data_rows()

def integrity_check(bridge: str):
    dataset = get_dataset(bridge=bridge)
    file_path_json = "output_dataset.json"

    # Open the file for writing
    with open(file_path_json, 'w') as json_file:
    # Write the opening bracket for the array
        json_file.write('{"data_rows": [')

        # Process and write each row to the file
        for i, row in enumerate(dataset.data_rows):
            # Add a comma between rows, except for the first row
            if i != 0:
                json_file.write(',')

            # Create a dictionary for the row
            serialized_row = {
                'data_hash': row.get('data_hash', ''),
                'data_title': row.get('data_title', ''),
                'file_size': row.get('file_size', 0)
                # Add other properties as needed
            }

            # Write the serialized row to the file
            json.dump(serialized_row, json_file, indent=2)

        # Write the closing bracket for the array
        json_file.write(']}')

    print(f"Serialized data written to {file_path_json}")

def get_project(bridge: str, project_name_like: str = None):
    user_client = EncordUserClient.create_with_ssh_private_key(get_private_key_file())
    if (bridge):
        return user_client.get_project(get_project_hash(bridge))
    else:
        projects = user_client.get_projects(title_like=project_name_like)
        for project in projects:
            if (project.get('project').get('title').find(project_name_like) != -1):
                return user_client.get_project(project.get('project').get('project_hash'))
    return None

def pull_labels(bridge: str, project_name_like: str, for_date: str):
    myProject = get_project(bridge, project_name_like)
    labels: List[Dict] = []
    start_date = datetime.strptime(for_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    label_rows = myProject.label_rows
    for label_row in label_rows:
        if label_row.get('label_status') == 'LABELLED':
            date_object = datetime.strptime(label_row.get('last_edited_at'), '%Y-%m-%d %H:%M:%S')
            print(f"Found label for Date: {date_object}")

            if for_date is None or (date_object >= start_date and date_object < end_date):
                full_label_row = myProject.get_label_row(label_row.get('label_hash'))
                labels.append({"date": date_object,"label": full_label_row, "classification": get_classification_answer_value(full_label_row)})
    return labels       

def pull_all_labels(bridge: str):
    myProject = get_project(bridge)
    labels: List[Dict] = []
    labels_to_return: List[Dict] = []
    label_rows = myProject.label_rows
    for label_row in label_rows:
        if label_row.get('label_status') == 'LABELLED':
            full_label_row = myProject.get_label_row(label_row.get('label_hash'))
            labels.append({"label": full_label_row, "classification": get_classification_answer_value(full_label_row)})
    for label in labels:
        labels_to_return.append({""})
    return labels       

def get_classification_answer_value(data: dict):
    # Extracting the first classification answer value
    classification_answers = data.get("classification_answers", {})
    first_classification = next(iter(classification_answers.values()), None)
    classification_result = {}

    if first_classification:
        classification = first_classification.get("classifications", [{}])[0]
        answers = classification.get("answers", [{}])
        first_answer_value = answers[0].get("value", None)

        if first_answer_value:
            classification_result = {"classification_name": classification.get('name'), "answer_value": first_answer_value}
        else:
            print("No answer value found.")
    else:
        print("No classification answers found.")
    return classification_result

def generate_date_range(start_date, end_date):
    date_format = "%Y-%m-%d"   
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date.strftime(date_format))
        current_date += timedelta(days=1)
    
    return date_range

# def sync_station_images(args: Dict):
#     start_date = datetime.strptime(args.get('start_date'), '%Y-%m-%d')
#     end_date = datetime.strptime(args.get('end_date'), '%Y-%m-%d')
#     project_hash = get_project(args.get('bridge'))
#     labels = pull_labels(project_hash, None, None)

#     # for each date between start and end date check if there is a label in the labels list. if not download the image
#     date_range = generate_date_range(start_date, end_date)
#     for date in date_range:
#         label_exists = False
#         for label in labels:
#             if label.get('date').strftime('%Y-%m-%d') == date:
#                 label_exists = True
#                 break
#         if not label_exists:
#             download_station_images_from_date(args.get('station_id'), date)