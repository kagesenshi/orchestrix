from orchestrix.fw.command import construct_command
from orchestrix.service.tenant import Tenant
from orchestrix.service.host import Host
from .env import env

__all__ = ['tenant', 'host']

tenant = construct_command('tenant', Tenant, '/tenants', server=env.host)
host = construct_command('host', Host, '/hosts', server=env.host)