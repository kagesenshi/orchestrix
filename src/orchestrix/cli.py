import click
import os
from .app import app
from .command.env import env
import fastapi
import uvicorn
import httpx
from .command.model import *
from .fw.command import handle_response, load_data_file
from getpass import getpass

@click.group()
def cli():
    pass

@click.command()
@click.option('-a', '--host', default='0.0.0.0', help='Host')
@click.option('-p', '--port', default=8000, help='Port')
@click.option('-w', '--workers', default=1, help='Workers')
@click.option('-r', '--reload', is_flag=True, help='Reload')
def run(host, port, reload, workers):
    uvicorn.run('orchestrix.app:app', host=host, port=port, use_colors=True, reload=reload, workers=workers)

@click.command()
@click.argument('tenant')
def login(tenant: str):
    username = input("Username: ")
    password = getpass("Password: ")
    with httpx.Client() as client:
        resp = client.post(f'{env.host}/+login?tenant_urn={tenant}', auth=(username, password))
        print(resp.json())


@click.command()
@click.argument('data')
def apply(data: str):
    server = env.host
    service_paths = {
        'tenant': '/tenants',
        'host': '/hosts'
    }
    with httpx.Client() as client:
        for d in load_data_file(data):
            urn = d['metadata']['urn']
            entity_type = d['metadata']['entity_type']
            service_path = service_paths[entity_type]
            response = client.get(f"{server}{service_path}/{urn}")
            check_result = handle_response(response, print_errors=False)
            if check_result is not None:
                print(f"Creating {urn}")
                response = client.post(f"{server}{service_path}", json=d['data'])
                result = handle_response(response)
                if result is None:
                    continue
            else:
                print(f"Updating {urn}")
                response = client.put(f"{server}{service_path}/{urn}", json=d['data'])
                result = handle_response(response)
                if result is None:
                    continue
            print(result['status'])

cli.add_command(run)
cli.add_command(login)
cli.add_command(apply)
cli.add_command(tenant)
cli.add_command(host)
cli.add_command(oauth_client)
