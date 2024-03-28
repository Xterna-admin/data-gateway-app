import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from encord import EncordUserClient
from encord.objects import ChecklistAttribute, ClassificationInstance, RadioAttribute
from encord.objects.common import Option
from tqdm import tqdm

from modules.config import get_private_key_file, get_project_hash

#A      
def get_frame_range(classification_instance: ClassificationInstance) -> (int, int):
    frames = [annotation.frame for annotation in classification_instance.get_annotations()]
    return min(frames), max(frames)
#B    
def get_answers(classification_instance: ClassificationInstance) -> Iterable[Option]:
    assert (
        len(classification_instance.ontology_item.attributes) == 1
    ), "Only one attribute per ontology item expected"

    attribute = classification_instance.ontology_item.attributes[0]
    if isinstance(attribute, RadioAttribute):
        yield classification_instance.get_answer(attribute)
    elif isinstance(attribute, ChecklistAttribute):
        yield from classification_instance.get_answer(attribute)
    else:
        assert False, f"Unexpected ontology item type: {attribute.__class__.__name__}"
        
        
@dataclass
class Label:
    project_id: str
    project_name: str
    instance_id: str
    data_hash: str
    label_hash: str
    data_title: str
    last_edited_at: str
    last_edited_by: str
    label_name: str
    answer_value: str = None
    file_link: str = None
      
def sync_encord_labels(bridge: str, from_date:str):
    user_client = EncordUserClient.create_with_ssh_private_key(get_private_key_file())
    project = user_client.get_project(get_project_hash(bridge))
    results = []

    for label_row in project.list_label_rows_v2(edited_after=datetime.strptime(from_date, '%Y-%m-%d')):
        label_row.initialise_labels()
        if label_row.label_status.value != "LABELLED":
            print(f"Skipping {label_row.label_status} label row {label_row.data_title}")
            continue
              
        for classification_instance in label_row.get_classification_instances():
            for answer in get_answers(classification_instance):
                label = Label(
                    project_id=project.project_hash,
                    project_name=project.title,
                    instance_id=classification_instance.classification_hash,
                    data_title=label_row.data_title,
                    last_edited_at=classification_instance.get_annotations()[0].last_edited_at,
                    last_edited_by=classification_instance.get_annotations()[0].last_edited_by,
                    label_name=classification_instance.ontology_item.title,
                    answer_value=answer.value,
                    label_hash=label_row.label_hash,
                    data_hash=label_row.data_hash,
                    file_link=label_row.data_link
                    )
                results.append(label)

    for label in results:
        print(label)
    return results
