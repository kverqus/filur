from argparse import ArgumentParser

from models import File
from schemas import config_schema

import yaml
import json
import os

def load_configuration(path: str) -> dict:
    configuration = {}

    if not os.path.exists:
        raise OSError(f"{path} not found")

    try:
        with open(path, 'r', encoding='utf-8') as file:
            configuration = yaml.safe_load(file)

    except yaml.parser.ParserError as err:
        print(f"ParserError {err}")
        return configuration

    else:
        if config_schema.validate(configuration) and configuration is not None:
            return configuration
        return {}

def export_json(path: str, data: dict) -> None:
    if os.path.exists(path):
        raise OSError(f"File {path} already exists")
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(data))

def export_output(configuration: dict, data: dict):
    match configuration['output']:
        case 'json':
            export_json()
        case 'html':
            pass
        case _:
            pass
        

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '-p',
        '--playbook',
        required=True,
        help='File path to playbook (yaml) file'
    )
    args = parser.parse_args()
    configuration = load_configuration(args.playbook)

    for file in configuration['files']:
        data = File.from_dict(file)
        processed = data.process()
        export_output(file, processed)
