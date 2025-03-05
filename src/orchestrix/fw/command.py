import click
from pydantic import BaseModel
import httpx 
from uuid import UUID
from tabulate import tabulate
from pprint import pprint
from orchestrix.fw.model import is_valid_urn
import json
import sys
import yaml

def load_data_file(path: str) -> list[dict]:
    if path == '-':
        d = sys.stdin.read()
    elif path.lower().endswith('.json'):
        with open(path) as f:
            d = json.loads(path)
    elif path.lower().endswith('.yaml') or path.lower().endswith('.yml'):
        with open(path) as f:
            payload = f.read()
            blocks = payload.split('---')
            return [yaml.safe_load(b) for b in blocks]
    else:
        raise ValueError(f"Unknown extension {path.lower().split('.')[-1]}")
    return [d]


def handle_response(response: httpx.Response, print_errors=True) -> dict:
    if response.status_code / 100 != 2:
        if print_errors:
            print(f"ERROR {response.status_code}", file=sys.stderr)
        try:
            if print_errors:
                pprint(response.json(), stream=sys.stderr)
        except json.JSONDecodeError:
            if print_errors:
                print(response.text, file=sys.stderr)
        return
    return response.json()

def construct_command(name: str, model: type[BaseModel], 
                      service_path: str,
                      server: str):
    
    if service_path.startswith('/'):
        service_path = service_path[1:]
    if service_path.endswith('/'):
        service_path = service_path[:-1]
    
    @click.group(name=name)
    def command():
        pass

    @click.command()
    def list():
        with httpx.Client() as client:
            response = client.get(f"{server}/{service_path}")
            items = [model.model_validate(i) for i in response.json()['records']]
            data = [i.model_dump() for i in items]
            if not data:
                print("No items found")
                return
            for row in data:
                # hide internal fields
                for f in ['uid', 'id', 'created', 'modified', 'deleted', 'version', 'active']:
                    del row[f]
            tbl = tabulate(data, headers='keys')
            print(tbl)

    @click.command()
    def history():
        with httpx.Client() as client:
            response = client.get(f"{server}/{service_path}/+history")
            items = [model.model_validate(i) for i in response.json()['records']]
            data = [i.model_dump() for i in items]
            if not data:
                print("No items found", file=sys.stderr)
                return
            for row in data:
                # hide uid fields
                for f in ['uid', 'id']:
                    del row[f]
            tbl = tabulate(data, headers='keys')
            print(tbl)

    @click.command()
    @click.argument('data')
    def create(data: str):
        with httpx.Client() as client:
            for d in load_data_file(data):
                response = client.post(f"{server}/{service_path}", json=d)
                result = handle_response(response)
                if result is None:
                    continue
                print(result['status'])

    @click.command()
    @click.argument('name')
    def show(name: str):
        with httpx.Client() as client:
            response = client.get(f"{server}/{service_path}/{name}")
            result = handle_response(response)
            if result is None:
                return 
            pprint(model.model_validate(result['record']).model_dump())

    @click.command()
    @click.argument('name')
    def history(name: str):
        with httpx.Client() as client:
            response = client.get(f"{server}/{service_path}/{name}/+history")
            items = [model.model_validate(i) for i in response.json()['records']]
            data = [i.model_dump() for i in items]
            if not data:
                print("No items found", file=sys.stderr)
                return
            for row in data:
                # hide uid fields
                for f in ['uid', 'id']:
                    del row[f]
            tbl = tabulate(data, headers='keys')
            print(tbl)


    @click.command()
    @click.argument('name')
    def delete(name: str):
        with httpx.Client() as client:
            response = client.delete(f"{server}/{service_path}/{name}")
            result = handle_response(response)
            if result is None:
                return 
            print(result['status'])

    @click.command()
    @click.argument('name')
    @click.argument('data')
    def update(name: str, data: str):
        with httpx.Client() as client:
            for d in load_data_file(data):
                response = client.put(f"{server}/{service_path}/{name}", json=d)
                result = handle_response(response)
                if result is None:
                    continue
                print(result['status'])


    command.add_command(list)
    command.add_command(history)
    command.add_command(create)
    command.add_command(show)
    command.add_command(delete)
    command.add_command(update)

    return command