from .model import UserService
from ..tenant import TenantService, Tenant
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Request, Depends
from orchestrix.db import DbSession

router = UserService.router()

@router.post('/{tenant_id}/+login')
def login(request: Request, db: DbSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
        tenant: Annotated[Tenant, Depends(TenantService.get_model)]):
    users = UserService(request, db)
    client_id = form_data.client_id
    username = form_data.username
    password = form_data.password
    # TODO: Implement actual authentication logic here
    if username == "admin" and password == "password":
        return {"access_token": "fake-jwt-token", "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")