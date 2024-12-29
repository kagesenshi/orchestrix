import click
from pydantic import BaseModel
import httpx 
from uuid import UUID
from tabulate import tabulate
from pprint import pprint
from orchestrix.fw.model import is_valid_urn
import json
import sys


def construct_command(name: str, model: type[BaseModel], 
                      service_path: str,
                      server: str):
    
    if service_path.startswith('/'):
        service_path = service_path[1:]
    if service_path.endswith('/'):
        service_path = service_path[:-1]
    
    def get_item_id(client: httpx.Client, name: str, service_path: str) -> str:
        response = client.get(f"{server}/{service_path}")
        items = [model.model_validate(i) for i in response.json()['records']]
        try:
            name = UUID(name)
            is_uuid = True
        except ValueError:
            is_uuid = False

        try:
            is_valid_urn(name)
            is_urn = True
        except ValueError:
            is_urn = False

        if is_urn:
            matches = [i.id for i in items if i.urn == name]
        elif is_uuid:
            matches = [i.id for i in items if i.id == name]
        else:
            matches = [i.id for i in items if i.name == name]
        if matches:
            return matches[0]
        else:
            raise ValueError(f"No item with name {name} found")
    
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
                # hide uid fields
                for f in ['uid', 'id']:
                    del row[f]
            tbl = tabulate(data, headers='keys')
            print(tbl)

    @click.command()
    @click.argument('data')
    def create(data: dict):
        with httpx.Client() as client:
            d = json.loads(data)
            response = client.post(f"{server}/{service_path}", json=d)
            if response.status_code / 100 != 2:
                print(f"ERROR {response.status_code}")
                print(response.text)
                return
            print(response.json()['status'])

    @click.command()
    @click.argument('name')
    def show(name):
        with httpx.Client() as client:
            try:
                item_id = get_item_id(client, name, service_path)
            except ValueError:
                print(f"No item with name {name}", file=sys.stderr)
                return

            response = client.get(f"{server}/{service_path}/{item_id}")
            if response.status_code / 100 != 2:
                print(f"ERROR {response.status_code}")
                print(response.text)
                return
            tbl = tabulate([model.model_validate(response.json()['record']).model_dump()], headers='keys')
            print(tbl)


    @click.command()
    @click.argument('name')
    def delete(name):
        with httpx.Client() as client:
            try:
                item_id = get_item_id(client, name, service_path)
            except ValueError:
                print(f"No item with name {name}", file=sys.stderr)
                return
            response = client.delete(f"{server}/{service_path}/{item_id}")
            if response.status_code / 100 != 2:
                print(f"ERROR {response.status_code}")
                print(response.text)
                return
            print(response.json()['status'])

    @click.command()
    @click.argument('name')
    @click.argument('data')
    def update(name, data):
        with httpx.Client() as client:
            try:
                item_id = get_item_id(client, name, service_path)
            except ValueError:
                print(f"No item with name {name}", file=sys.stderr)
                return
            d = json.loads(data)
            response = client.put(f"{server}/{service_path}/{item_id}", json=d)
            if response.status_code / 100 != 2:
                print(f"ERROR {response.status_code}")
                print(response.text)
                return

            print(response.json()['status'])

    command.add_command(list)
    command.add_command(create)
    command.add_command(show)
    command.add_command(delete)
    command.add_command(update)

    return command