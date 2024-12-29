import click
import os
from .app import app
from .command.env import env
import fastapi
import uvicorn
import httpx
from .command.model import *

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

plugin_folder = os.path.join(os.path.dirname(__file__), 'command')

cli.add_command(run)
cli.add_command(tenant)
cli.add_command(host)