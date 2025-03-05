import sqlalchemy as sa
from fastapi import Depends
from pydantic import AfterValidator, field_validator
from uuid import UUID
from uuid_extensions import uuid7
from orchestrix.db import metadata, DbSession
from orchestrix.fw.service import Service, redefine_model
from orchestrix.fw.model import Core, CoreIndex, is_valid_urn
from ..tenant import TenantService, Tenant
import fastapi
from sqlmodel import SQLModel, Field, select
from typing import Annotated, Literal
import asyncio
import enum

__all__ = ['OAuthClient', 'OAuthClientSchema', 'OAuthClientService']

class OAuthClientSchema(Core):
    tenant_urn: Annotated[str, AfterValidator(is_valid_urn)] = Field(foreign_key='tenants.urn')
    client_id: str = Field()
    client_secret: str = Field()

class OAuthClient(SQLModel, OAuthClientSchema, table=True):
    __tablename__ = 'oauth_clients'

class OAuthClientService(Service[OAuthClient]):

    @classmethod
    def model_class(cls) -> type[OAuthClient]:
        return OAuthClient
    
    @classmethod
    def schema_class(cls) -> type[OAuthClientSchema]:
        return OAuthClientSchema
    
    @classmethod
    def urn_entity_type(cls) -> Literal['oauth_client']:
        return 'oauth_client'
    
    def urn(self, model: OAuthClient):
        namespace = self.urn_namespace()
        entity_type = self.urn_entity_type()
        urn = f'urn:{namespace}:{entity_type}:{model.client_id})'
        return urn
    
    async def validate_data(self, data: OAuthClientSchema):
        await TenantService(self.request, self.db).get(data.tenant_urn)
        return await super().validate_data(data)
    
    async def get_tenant(self, model: OAuthClient):
        return await TenantService(self.request, self.db).get(model.tenant_urn)