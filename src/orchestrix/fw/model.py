from sqlmodel import SQLModel, Field
from uuid_extensions import uuid7
from uuid import UUID
from datetime import datetime
import sqlalchemy as sa
from pydantic import AfterValidator, BaseModel
from typing import Annotated, Optional
import re
import pendulum

def ts_now() -> datetime:
    from ..env import env
    tz = pendulum.timezone(env.timezone)
    return datetime.now(tz=tz)

def is_valid_name(name: str) -> str:
    if not name:
        raise ValueError("Name cannot be empty")
    if not re.match("^[a-z0-9_]+$", name):
        raise ValueError("Name can only contain lowercase letters, numbers, and underscores")
    if len(name) > 64:
        raise ValueError("Name cannot be longer than 64 characters")
    return name

def is_valid_urn(urn: str) -> str:
    if not urn:
        raise ValueError("URN cannot be empty")
    if not re.match(r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9]+:[a-z0-9_\(\):,]+$", urn):
        raise ValueError("URN is not valid")
    if len(urn) > 128:
        raise ValueError("URN cannot be longer than 128 characters")
    return urn

class CoreIndex(type(SQLModel)):
    def __new__(cls, name: str, bases: tuple[type], attrs: dict, **kwargs):
        c = super().__new__(cls, name, bases, attrs, **kwargs)

        if kwargs.get('table', False):
            core_indexes = (
                sa.Index(f'ix_{name.lower()}_id_version', 'id', 'version', unique=True),
                sa.Index(f"ix_{name.lower()}_id_active", "id", "active"),
                sa.Index(f'ix_{name.lower()}_urn_version', 'urn', 'version', unique=True),
            )
            if hasattr(c, "__table_args__"):
                c.__table_args__ = (c.__table_args__ + core_indexes)
            else:
                c.__table_args__ = core_indexes

        return c


# model based on dublin core standard
class Core(BaseModel, metaclass=CoreIndex):
    uid: UUID = Field(primary_key=True, default_factory=uuid7)
    id : UUID = Field(default_factory=uuid7)
    urn: Annotated[str, AfterValidator(is_valid_urn)] = Field(index=True, max_length=128)
    name : Annotated[str, AfterValidator(is_valid_name)] = Field(index=True, max_length=64)
    created: datetime = Field(sa_type=sa.TIMESTAMP(timezone=True), nullable=False, default_factory=ts_now)
    modified: datetime = Field(sa_type=sa.TIMESTAMP(timezone=True), nullable=False, default_factory=ts_now)
    deleted: Optional[datetime] = Field(sa_type=sa.TIMESTAMP(timezone=True), nullable=True)
    version : int = Field(nullable=False, default=1, index=True)
    active: bool = Field(nullable=False, default=True)


class DublinCore(Core):
    description : str = Field(nullable=True)
    publisher : str = Field(nullable=True)
    contributor : list[str] = Field(nullable=True)
    published : datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True)))
    type : str = Field(nullable=True)
    format : str = Field(nullable=True)
    source : str = Field(nullable=True)
    language : str = Field(nullable=True)
    relation : str = Field(nullable=True)
    coverage : str = Field(nullable=True)
    rights : str = Field(nullable=True)



