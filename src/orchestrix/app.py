import fastapi
from contextlib import asynccontextmanager
from .service.host import host_router
from .service.tenant import tenant_router
from .route import auth, cluster
from orchestrix.db import db_engine
from sqlmodel import SQLModel

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    async with db_engine().connect() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

app = fastapi.FastAPI(lifespan=lifespan)

@app.get("/")
def index():
    # forward to docs
    return fastapi.responses.RedirectResponse(url="/docs")

app.include_router(tenant_router, tags=["tenant"])
app.include_router(host_router, tags=["host"])
#app.include_router(auth.router, tags=["auth"])
#app.include_router(cluster.router, tags=["cluster"])

