from pydantic import BaseModel
from uuid import UUID
import sqlalchemy as sa
import fastapi
from typing import Annotated
from uuid_extensions import uuid7
from orchestrix.db import DbSession, metadata
from orchestrix.fw.service import Service, redefine_model
from orchestrix.fw.model import Core, CoreIndex
from sqlmodel import SQLModel, Field, Session, select

__all__ = ['Tenant', 'TenantSchema', 'TenantService']

class TenantSchema(Core):
    pass

class Tenant(SQLModel, TenantSchema, table=True):
    __tablename__ = "tenants"
    pass

class TenantService(Service[Tenant]):

    @classmethod
    def model_class(cls) -> type[Tenant]:
        return Tenant
    
    @classmethod
    def schema_class(cls) -> type[TenantSchema]:
        return TenantSchema
    
    