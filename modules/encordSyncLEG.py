from app import app
from typing import Dict, List
from encord import EncordUserClient
from pathlib import Path
from encord import Dataset, EncordUserClient, Project

import sys
import os

from modules.config import get_private_key_file

user_client = EncordUserClient.create_with_ssh_private_key(get_private_key_file())
dataset: Dataset = user_client.get_dataset("85bf029e-7acb-4d4a-b8e2-f09835e4f747")

directory = './storage'
 
# iterate over files in
# that directorydone
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        print(f)
        dataset.upload_image(f)

        Path(f).rename(directory + "/done/" + filename)


# print(dataset)