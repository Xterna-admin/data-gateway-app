import argparse
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from encord import EncordUserClient, Project
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
    data_title: str
    annotator_email: str
    created_at: str
    label_name: str
    start_frame: int
    end_frame: int
      
def sync_encord_labels():
    user_client = EncordUserClient.create_with_ssh_private_key(get_private_key_file())
    project = user_client.get_project(get_project_hash("catchups"))
    results = []

    for label_row in project.list_label_rows_v2():
        label_row.initialise_labels()
              
        for classification_instance in label_row.get_classification_instances():
            for answer in get_answers(classification_instance):
                start_frame, end_frame = get_frame_range(classification_instance)
                label = Label(
                    project_id=project.project_hash,
                    project_name=project.title,
                    instance_id=classification_instance.classification_hash,
                    data_title=label_row.data_title,
                    annotator_email=classification_instance.get_annotations()[0].created_by,
                    created_at=classification_instance.get_annotations()[0].created_at,
                    label_name=f"{classification_instance.ontology_item.title} - {answer.value}",
                    start_frame=start_frame,
                    end_frame=end_frame,
                    )
                results.append(label)

    for label in results:
        print(label)
