import sqlalchemy as sa
from fastapi import Depends
from pydantic import AfterValidator, field_validator
from uuid import UUID
from uuid_extensions import uuid7
from orchestrix.db import metadata, DbSession
from orchestrix.fw.service import Service, redefine_model
from orchestrix.fw.model import Core, CoreIndex, is_valid_urn
from ..tenant.model import TenantService, Tenant
import fastapi
from sqlmodel import SQLModel, Field, select
from typing import Annotated, Literal
import asyncio
import enum

__all__ = ['Host', 'HostSchema', 'HostService']

class HostStateEnum(enum.StrEnum):
    NEW = enum.auto()
    REGISTERING = enum.auto()
    REGISTERED = enum.auto()
    ONLINE = enum.auto()
    OFFLINE = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()

class HostSchema(Core):
    tenant_urn: Annotated[str, AfterValidator(is_valid_urn)] = Field(foreign_key='tenants.urn')
    hostname: str = Field()
    state: HostStateEnum = HostStateEnum.NEW

class Host(SQLModel, HostSchema, table=True):
    __tablename__ = 'hosts'

class HostService(Service[Host]):

    @classmethod
    def model_class(cls) -> type[Host]:
        return Host
    
    @classmethod
    def schema_class(cls) -> type[HostSchema]:
        return HostSchema
    
    def urn(self, model: Host):
        namespace = self.urn_namespace()
        entity_type = self.urn_entity_type()
        urn = f'urn:{namespace}:{entity_type}:host({model.tenant_urn},{model.name})'
        return urn

    async def validate_data(self, data: HostSchema):
        await TenantService(self.request, self.db).get(data.tenant_urn)
        return await super().validate_data(data)
    
    async def get_tenant(self, model: Host):
        result = await self.db.exec(select(Tenant).where((Tenant.urn==model.tenant_urn) & (Tenant.active == True)))
        return result.first()