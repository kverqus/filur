from argparse import ArgumentParser
from jinja2 import Environment, FileSystemLoader

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


def export_html(title: str, path: str, data: dict) -> None:
    if os.path.exists(path):
        raise OSError(f"File {path} already exists")

    environment = Environment(loader=FileSystemLoader('templates/'))
    template = environment.get_template('template.html')
    content = template.render(title=title, data=data)

    with open(path, mode='w', encoding='utf-8') as file:
        file.write(content)


def export_output(configuration: dict, data: dict):
    match configuration['output']['type']:
        case 'json':
            export_json(configuration['output']['path'], data)
        case 'html':
            export_html(configuration['file'],
                        configuration['output']['path'], data)
        case 'console' | _:
            print(json.dumps(data, indent=2))


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
