# Creating new model

## Concepts

Orchestrix uses a CRUD framework in `orchestrix.fw` for defining content types. This CRUD framework
uses declarative approach to create data model. Model inherits from `orchestrix.fw.model.Core`
which is a `sqlmodel.SQLModel` metaclass which provides DublinCore compliant metadata.

Example of a model definition is as follows:

### Model definition `model.py`

```python
from pydantic import BaseModel
from uuid import UUID
import sqlalchemy as sa
import fastapi
from typing import Annotated
from uuid_extensions import uuid7
from orchestrix.db import DbSession, metadata
from orchestrix.fw.service import Service, redefine_model
from orchestrix.fw.model import Core, CoreIndex
from sqlmodel import SQLModel, Field, Session, select, Relationship

__all__ = ['Tenant', 'TenantSchema', 'TenantService', 'router']

class TenantSchema(Core):
    address: str = Field()

class Tenant(SQLModel, TenantSchema, table=True):
    __tablename__ = "tenants"
    hosts : list['orchestrix.service.host.model.Host'] = Relationship() # type: ignore

class TenantService(Service[Tenant]):

    @classmethod
    def model_class(cls) -> type[Tenant]:
        return Tenant
    
    @classmethod
    def schema_class(cls) -> type[TenantSchema]:
        return TenantSchema

router = TenantService.router()
```

### Explanation

#### Schema model definition

```python
class TenantSchema(Core):
    address: str = Field()
```

In this section, we extend `orchestrix.fw.model.Core` to create a table schema
for `Tenant`. This class should be where you define additional field/columns to 
be introduced to the data model that will be stored into database. This 
class also will be used by FastAPI to generate input/output schema.

#### SQL model definition

```python
class Tenant(SQLModel, TenantSchema, table=True):
    __tablename__ = "tenants"
    hosts : list['orchestrix.service.host.model.Host'] = Relationship() # type: ignore
```

In this section, we extend the schema model with SQLModel to declare a table in database.
Make sure you set `table=True` and `__tablename__` on the class definition. 
You can declare relationship resolvers on this class. This model object will be passed
around the application to interact with data.

#### Service definition

```python
class TenantService(Service[Tenant]):

    @classmethod
    def model_class(cls) -> type[Tenant]:
        return Tenant
    
    @classmethod
    def schema_class(cls) -> type[TenantSchema]:
        return TenantSchema

router = TenantService.router()
```

After defining the schema model and SQL model, declare the service class for
this data model. `model_class` and `schema_class` classmethod tell the framework
on which class to use for schema and sql model. 

The service class handles the actual CRUD operation for the model. Override the 
`create`,`read`,`update`,`delete` method to change default behavior.

`router` object can be then used to register model routes to your application
using:

```
app.include_router(router)
```
