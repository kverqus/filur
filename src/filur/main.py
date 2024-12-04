from argparse import ArgumentParser
from jinja2 import Environment, FileSystemLoader
from importlib import resources

from filur.models import File
from filur.schemas import config_schema

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


def write_file(path: str, content: str, mode: str = 'w', encoding: str = 'utf-8') -> None:
    try:
        with open(path, mode, encoding=encoding) as file:
            file.write(content)

        print(clickable_link(path, f'Click to open output'))

    except FileNotFoundError:
        print("Error: The directory or file path does not exist.")

    except PermissionError:
        print("Error: Insufficient permissions to write to the file.")

    except IsADirectoryError:
        print("Error: A directory was provided where a file was expected.")

    except OSError as e:
        print(f"OS error occurred: {e}")

    except ValueError:
        print("Error: Invalid file mode or other argument.")


def export_json(configuration: dict, data: dict) -> None:
    output = configuration['output']
    path = output['path']
    overwrite = output['overwrite'] if 'overwrite' in output else False

    if os.path.exists(path) and not overwrite:
        raise OSError(f"File {path} already exists")

    write_file(path, json.dumps(data))


def export_html(configuration: dict, data: dict) -> None:
    output = configuration['output']
    title = configuration['file']
    path = output['path']
    overwrite = output['overwrite'] if 'overwrite' in output else False

    if os.path.exists(path) and not overwrite:
        raise OSError(f"File {path} already exists")

    with resources.path('filur.templates', '') as templates_path:
        environment = Environment(loader=FileSystemLoader(templates_path))

    template = environment.get_template('template.html')
    content = template.render(title=title, data=data)

    write_file(path, content)


def clickable_link(uri: str, label: str = '') -> str:
    label = uri if not label else label
    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
    return f"\033]8;'';{uri}\033\\{label}\033]8;;\033\\"


def export_output(configuration: dict, data: dict):
    match configuration['output']['type']:
        case 'json':
            export_json(configuration, data)
        case 'html':
            export_html(configuration, data)
        case 'console' | _:
            print(json.dumps(data, indent=2))


def main():
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


if __name__ == "__main__":
    main()
