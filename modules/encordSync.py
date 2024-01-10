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

def get_projects():
    user_client = EncordUserClient.create_with_ssh_private_key(get_private_key_file())
    projects: List[Dict] = user_client.get_projects()
    return projects

def pull_labels():
    user_client = EncordUserClient.create_with_ssh_private_key(get_private_key_file())
    projects = get_projects()
    labels: List[Dict] = []
    after_date = datetime.now() - timedelta(days=1)
    for project in projects:
        print(project)
        if (project.get('project').get('title').find('Forward') == -1):
            continue
        project_hash = project.get('project').get('project_hash')
        myProject = user_client.get_project(project_hash)
        print(myProject)
        label_rows = myProject.label_rows
        for label_row in label_rows:
            if (label_row.get('label_status') == 'LABELLED'):
                date_object = datetime.strptime(label_row.get('last_edited_at') , '%Y-%m-%d %H:%M:%S')

                if date_object > after_date:
                    labels.append(myProject.get_label_row(label_row.get('label_hash')))
                else:
                    print(f"Label is too old => {date_object}")
    return labels       