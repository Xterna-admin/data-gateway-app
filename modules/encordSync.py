from datetime import datetime, timedelta
import json
from typing import Dict, List
from encord import EncordUserClient
from pathlib import Path
from encord import Dataset, EncordUserClient, Project

import sys

from modules.config import get_private_key_file
from app import app
from typing import Dict, List
from encord import EncordUserClient
from pathlib import Path
from encord import Dataset, EncordUserClient, Project
import sys
from modules.config import get_private_key_file, get_images_path, get_test_dataset_id

def get_dataset() -> Dataset:
    # create a user client with the private key
    user_client = EncordUserClient.create_with_ssh_private_key(get_private_key_file())
    # get the dataset
    dataset: Dataset = user_client.get_dataset(get_test_dataset_id())
    return dataset

# create a function to upload an image to a dataset
def upload_image_file(file_name: str):
    return upload_image(get_images_path() + file_name)

# create a function to upload an image to a dataset
def upload_image(path: str):
    dataset = get_dataset()
    return dataset.upload_image(path)

def upload_all_images():
    dataset = get_dataset()
    
    # for each image in the images folder
    for image in Path(get_images_path()).iterdir():
        # upload the image
        dataset.upload_image(image)

# create a function to list all the images in a dataset
def list_images():
    dataset = get_dataset()
    return dataset.list_images()

# create a function to list all the data rows in a dataset
def list_data_rows():
    dataset = get_dataset()
    return dataset.list_data_rows()

def integrity_check():
    dataset = get_dataset()
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

def get_project(project_hash: str, project_name_like: str):
    user_client = EncordUserClient.create_with_ssh_private_key(get_private_key_file())
    if (project_hash):
        return user_client.get_project(project_hash)
    else:
        projects = user_client.get_projects(title_like=project_name_like)
        for project in projects:
            if (project.get('project').get('title').find(project_name_like) != -1):
                return user_client.get_project(project.get('project').get('project_hash'))
    return None

def pull_labels(project_hash: str, project_name_like: str, for_date: str):
    myProject = get_project(project_hash, project_name_like)
    labels: List[Dict] = []
    start_date = datetime.strptime(for_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    label_rows = myProject.label_rows
    for label_row in label_rows:
        if (label_row.get('label_status') == 'LABELLED'):
            date_object = datetime.strptime(label_row.get('last_edited_at') , '%Y-%m-%d %H:%M:%S')

            if date_object >= start_date and date_object < end_date:
                full_label_row = myProject.get_label_row(label_row.get('label_hash'))
                labels.append({"label": full_label_row, "classification": get_classification_answer_value(full_label_row)})
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
