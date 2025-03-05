from orchestrix.fw.command import construct_command
from orchestrix.service.tenant import Tenant
from orchestrix.service.host import Host
from orchestrix.service.oauth_client import OAuthClient
from .env import env

__all__ = ['tenant', 'host', 'oauth_client']

tenant = construct_command('tenant', Tenant, '/tenants', server=env.host)
host = construct_command('host', Host, '/hosts', server=env.host)
oauth_client = construct_command('oauth_client', OAuthClient, '/oauth_clients', server=env.host)