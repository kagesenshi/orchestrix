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
from typing import Annotated
import asyncio

__all__ = ['Host', 'HostSchema', 'HostService']

async def check_tenant(request: fastapi.Request, db: DbSession, tenant_urn: str) -> str:
    tenant_service = TenantService(request, db)
    tenant = await tenant_service.get(tenant_urn)
    return tenant.urn

class HostSchema(Core):
    ip: str = Field()
    tenant_urn: Annotated[str, AfterValidator(is_valid_urn)] = Field(foreign_key='tenants.urn')

class Host(SQLModel, HostSchema, table=True):
    __tablename__ = 'hosts'

class HostService(Service[Host]):

    @classmethod
    def model_class(cls) -> type[Host]:
        return Host
    
    @classmethod
    def schema_class(cls) -> type[HostSchema]:
        return HostSchema
    
    async def create(self, data_model: HostSchema):
        return await super().create(data_model) 
    
    async def get(self, model_id):
        model = await super().get(model_id)
        return model
    
    async def update(self, model_id, data: HostSchema):
        return await super().update(model_id, data)
    
    async def validate_data(self, data: HostSchema):
        await check_tenant(self.request, self.db, data.tenant_urn)
        return await super().validate_data(data)
    
    async def get_tenant(self, model: Host):
        result = await self.db.exec(select(Tenant).where((Tenant.urn==model.tenant_urn) & (Tenant.active == True)))
        return result.first()