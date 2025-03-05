from pydantic import BaseModel, Field, create_model, AnyUrl
import fastapi
from fastapi import Depends
import sqlalchemy as sa
from uuid import UUID
from sqlmodel import SQLModel, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
import sqlalchemy.exc as saexc
from orchestrix.db import DbSession
from orchestrix.fw.model import ts_now, Core, is_valid_urn
from orchestrix.fw.exc import ModelValidationError, AlreadyExistError
from typing import Generic, TypeVar, Any, Literal, Annotated, Union, List
import abc
import jinja2 as j2
from .exc import NotFoundError

T = TypeVar("T", bound=Core)
S = TypeVar("S", bound=SQLModel)

class ErrorDetail(BaseModel):
    loc: list[Any] = Field(default_factory=list)
    msg: str | None = None
    type: str | None = None

STATUSES = Literal["success", "error"]

class BaseResult(BaseModel):
    detail: list[ErrorDetail] | None = None
    status: STATUSES = "success"

class Result(BaseResult, Generic[T]):
    record: T

class PaginationMeta(BaseModel):
    page_num: int | None = None
    page_size: int | None = None
    next_page: AnyUrl | None = None
    prev_page: AnyUrl | None = None

class ListResult(BaseResult, Generic[T]):
    records: list[T] | None = None
    meta: PaginationMeta | None = None


def redefine_model(name, Model: type[BaseModel], *, exclude=None) -> type[BaseModel]:
    exclude = exclude or []

    fields = {fname: (field.annotation, field) for fname, field in 
              Model.model_fields.items() if fname not in exclude}

    model = create_model(
        name,
        **fields
    )
    return model 

class Service(Generic[S], abc.ABC):

    @classmethod
    @abc.abstractmethod
    def model_class(cls) -> type[S]:
        raise NotImplementedError("model_class must be implemented")
    
    @classmethod
    def createmodel_class(cls) -> type[BaseModel]:
        model_class = cls.model_class()
        schema_class = cls.schema_class()
        return redefine_model(f'Create {model_class.__name__}', schema_class, 
                                     exclude=cls.internal_fields())
    
    @classmethod
    def updatemodel_class(cls) -> type[BaseModel]:
        model_class = cls.model_class()
        schema_class = cls.schema_class()
        return redefine_model(f'Update {model_class.__name__}', schema_class,
                                     exclude=cls.internal_fields() + cls.immutable_fields())


    @classmethod
    @abc.abstractmethod
    def schema_class(cls) -> type[Core]:
        raise NotImplementedError("schema_class must be implemented")

    @classmethod
    def service_path(cls) -> str:
        return f'/{cls.urn_entity_type()}s'

    @classmethod
    def model_path(cls) -> str:
        return f'{cls.service_path()}/{{urn}}'

    @classmethod
    def internal_fields(cls) -> list[str]:
        return ['urn', 'uid', 'id', 'created', 'modified', 'deleted', 'version', 'active']
    
    @classmethod
    def hidden_fields(cls) -> list[str]:
        return ['uid']
    
    @classmethod
    def noninheritable_fields(cls) -> list[str]:
        return ['uid', 'modified', 'deleted', 'version', 'active']
    
    @classmethod
    def immutable_fields(cls) -> list[str]:
        # fields that can't be updated, but not internal fields
        return ['name']
    
    @classmethod
    def urn_namespace(cls) -> str:
        model_class = cls.model_class()
        return model_class.__module__.split('.')[0]

    @classmethod
    def urn_entity_type(cls) -> str:
        model_class = cls.model_class()
        return model_class.__name__.lower()

    def __init__(self, request: fastapi.Request, db: AsyncSession):
        self.request = request
        self.db = db

    def urn(self, model: Core):
        namespace = self.urn_namespace()
        entity_type = self.urn_entity_type()
        urn = f'urn:{namespace}:{entity_type}:{model.name}'
        return urn

    async def create(self, data: Core) -> S:
        model_class = self.__class__.model_class()
        data = await self.validate_data(data)
        parsed_data = data.model_dump(exclude=self.internal_fields())
        urn = self.urn(data)
        parsed_data['urn'] = urn
        if not parsed_data:
            raise ValueError("No data provided")
        
        try:
            await self.get(urn)
            raise AlreadyExistError(message=f'Already Exists: {urn}')
        except NotFoundError:
            pass
        model = model_class(**parsed_data)
        self.db.add(model)
        try:
            await self.db.flush()
        except saexc.IntegrityError as e:
            raise ModelValidationError(message=e.args[0])
        await self.db.refresh(model)
        return model

    async def get(self, model_id: str | UUID) -> S:
        model_class = self.__class__.model_class()

        if isinstance(model_id, str):
            try:
                is_valid_urn(model_id)
                filter = model_class.urn == model_id
            except ValueError:
                try:
                    model_id = UUID(model_id)
                    filter = model_class.id == model_id
                except ValueError:
                    filter = model_class.name == model_id

        else:
            filter = model_class.id == model_id

        filter &= (model_class.active == True)
        result = await self.db.exec(select(model_class).where(filter))
        obj = result.first()
        if not obj:
            raise NotFoundError(message=f"{model_class.__name__}({model_id})")
        return obj
    
    async def get_history(self, model_id: str | UUID) -> list[S]:
        model_class = self.__class__.model_class()

        if isinstance(model_id, str):
            try:
                is_valid_urn(model_id)
                filter = model_class.urn == model_id
            except ValueError:
                model_id = UUID(model_id)
                filter = model_class.id == model_id
        else:
            filter = model_class.id == model_id

        results = await self.db.exec(select(model_class).where(filter))
        return results


    async def update(self, model_id: str | UUID, data: Core) -> S:

        data = await self.validate_data(data)
        model = await self.get(model_id)
        model_class = self.model_class()
        # delete old record
        old_version = model.version
        model.sqlmodel_update({'deleted': ts_now(), 'active': False})
        # create new record
        newdata = model.model_dump(exclude=self.noninheritable_fields())
        newdata.update(data.model_dump(exclude_unset=True))
        newdata['version'] = old_version + 1
        new = model_class(**newdata)
        self.db.add(new)
        await self.db.flush()
        await self.db.refresh(model)
        return model

    async def delete(self, model_id: str | UUID):
        model = await self.get(model_id)
        model.sqlmodel_update({'deleted': ts_now(), 'active': False})
        await self.db.flush()

    async def list_active(self) -> list[S]:
        model_class = self.__class__.model_class()
        filter = (model_class.active == True)
        models = await self.db.exec(select(model_class).where(filter))
        return models.all()
    
    async def list_history(self) -> list[S]:
        model_class = self.__class__.model_class()
        models = await self.db.exec(select(model_class))
        return models
    
    async def search(self, *, offset=0, limit=10, sa_filters=None, only_active=True, **filters):
        model_class = self.__class__.model_class()
        if only_active:
            filter = (model_class.active == True)
        else:
            filter = (sa.literal(1)==1)
        if sa_filters and filters:
            raise ValueError("Cannot use both sa_filters and filters")
        for field_name, value in filters.items():
            filter &= (getattr(model_class, field_name) == value)
        if sa_filters:
            filter &= sa_filters
        models = await self.db.exec(select(model_class).where(filter).offset(offset).limit(limit))
        return models


    
    async def validate_data(self, data: Core) -> Core:
        # raise error if fail
        return data

    @classmethod
    async def get_model(cls, request: fastapi.Request, db: DbSession, urn: str) -> S:
        svc = await cls.get_service(request, db)
        return await svc.get(urn)

    @classmethod
    async def get_service(cls, request: fastapi.Request, db: DbSession):
        return cls(request, db)


    @classmethod
    def router(cls) -> fastapi.APIRouter:
        if not getattr(cls, '_router', None):
            router = fastapi.APIRouter()
            cls.register_views(router, cls.service_path(), cls.model_path())
            cls._router = router
        return cls._router

    @classmethod
    def register_views(cls, router: fastapi.APIRouter, 
                       service_path: str,
                       model_path: str):
        """Register views for the service."""
        # Implement view registration logic here

        model_class = cls.model_class()
        entity_type = cls.urn_entity_type()

        CreateModel = cls.createmodel_class()
        UpdateModel = cls.updatemodel_class()

        @router.get(service_path, operation_id=f"orchestrix-list-{entity_type}")
        async def list_active(svc: Annotated[cls, Depends(cls.get_service)]) -> ListResult[model_class]: # type: ignore
            return {
                "records": await svc.list_active()
            }
        
        @router.get(f'{service_path}/+history', operation_id=f"orchestrix-history-{entity_type}")
        async def list_history(svc: Annotated[cls, Depends(cls.get_service)]) -> ListResult[model_class]: # type: ignore
            return {
                "records": await svc.list_history()
            }
        
        @router.post(service_path, operation_id=f"orchestrix-create-{entity_type}")
        async def create(svc: Annotated[cls, Depends(cls.get_service)], data: CreateModel) -> Result[model_class]: # type: ignore
            created_model = await svc.create(data)
            return {"record": created_model}
        
        @router.get(model_path, operation_id=f"orchestrix-get-{entity_type}")
        async def get(model: Annotated[model_class, Depends(cls.get_model)]) -> Result[model_class]: # type: ignore
            return {
                "record": model
            }
        
        @router.get(f'{model_path}/+history', operation_id=f'orchestrix-get-history-{entity_type}')
        async def get_history(svc: Annotated[cls, Depends(cls.get_service)], model: Annotated[model_class, Depends(cls.get_model)]) -> ListResult[model_class]: # type: ignore
            return {
                "records": await svc.get_history(model.id)
            }

        if UpdateModel.model_fields: 
            @router.put(model_path, operation_id=f'orchestrix-update-{entity_type}')
            async def update(svc: Annotated[cls, Depends(cls.get_service)], 
                         model: Annotated[model_class, Depends(cls.get_model)], # type: ignore
                         data: UpdateModel) -> Result[model_class]: # type: ignore
                updated_model = await svc.update(model.id, data)
                return {
                    "record": updated_model
                }
        
        @router.delete(model_path, operation_id=f'orchestrix-delete-{entity_type}')
        async def delete(svc: Annotated[cls, Depends(cls.get_service)], 
                         model: Annotated[model_class, Depends(cls.get_model)]) -> BaseResult: # type: ignore
            await svc.delete(model.id)
            return {
                "status": "success"
            }
        