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

__all__ = ['User', 'UserSchema', 'UserService']

class UserStateEnum(enum.StrEnum):
    PENDING = enum.auto()
    ACTIVE = enum.auto()
    DISABLED = enum.auto()

class UserSchema(Core):
    tenant_urn: Annotated[str, AfterValidator(is_valid_urn)] | None = Field(foreign_key='tenants.urn', default=None)
    username: str = Field()
    email: str = Field()
    password_hash: str = Field()
    state: UserStateEnum = UserStateEnum.PENDING

class User(SQLModel, UserSchema, table=True):
    __tablename__ = 'users'

class UserService(Service[User]):

    @classmethod
    def model_class(cls) -> type[User]:
        return User
    
    @classmethod
    def schema_class(cls) -> type[UserSchema]:
        return UserSchema
    
    def urn(self, model: User):
        namespace = self.urn_namespace()
        entity_type = self.urn_entity_type()
        urn = f'urn:{namespace}:{entity_type}:user({model.tenant_urn},{model.name})'
        return urn
    
    async def validate_data(self, data: UserSchema):
        await TenantService(self.request, self.db).get(data.tenant_urn)
        await self.validate_password(data)
        return await super().validate_data(data)
    
    async def validate_password(self, data: UserSchema):
        pass

    async def get_tenant(self, model: User):
        result = await self.db.exec(select(Tenant).where((Tenant.urn==model.tenant_urn) & (Tenant.active == True)))
        return result.first()